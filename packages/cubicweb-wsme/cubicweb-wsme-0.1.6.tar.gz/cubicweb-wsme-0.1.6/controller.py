""" 'webservice' controller implementation
"""
import inspect
import sys

from cubicweb.web.controller import Controller
from cubicweb.web import NotFound
from cubicweb.predicates import yes
from cubicweb import ValidationError
import cubicweb

import wsme
import wsme.rest.json
import wsme.rest.xml

from wsme.types import text
from cubes.wsme.types import PassThroughType, JsonData, wsattr, Any
from cubes.wsme.predicates import match_ws_etype
from rqlquery.filter import FilterParser

from rqlquery import query

restformats = {
    'json': wsme.rest.json,
    'xml': wsme.rest.xml
}


class ParamsAdapter(dict):
    """ Adapter for passing cubicweb request params to
    :func:`wsme.rest.args.get_args`
    """

    def getall(self, path):
        v = self[path]
        if not isinstance(v, list):
            v = [v]
        return v


class WSController(Controller):
    """
    A controller that rely on WSME to provide webservice API for an entity.
    """
    __regid__ = 'webservice'
    __abstract__ = True

    @classmethod
    def resolve_types(cls, registry):
        """ Late-resolve the types of the function signatures.

        This function is called at regitering time (by :meth:`__registered__`).
        """
        for name, attr in inspect.getmembers(cls, wsme.api.iswsmefunction):
            funcdef = wsme.api.FunctionDefinition.get(attr)
            funcdef.resolve_types(registry)

    @classmethod
    def __registered__(cls, reg):
        cls.resolve_types(reg.vreg.wsme_registry)

    def publish(self, rset):
        """ Main entry-point of the controller.

        Will dispatch the request to the adequate function depending on the
        http method and the form/rset content.

        It also takes care of converting the inputs (form & body) to call
        arguments using the WSME api, based on the function signatures.

        The following `form` values are used, which are normaly set by
        :class:`cubes.wsme.views.RestPathEvaluator`:

        -   `_ws_method`: the HTTP method
        -   `_ws_etype`: the etype (ignored, only used by the selector)
        -   `_ws_rtype`: the relation type if provided
        -   `_ws_rtype_target`: An option relation target id

        If the :arg:`rset` contains an entity, it will be considered as the
        target of the API call.

        """
        content_type = self._cw.get_header('Content-Type')
        accept = self._cw.get_header('Accept')

        restformat = None

        for accept in self._cw.parse_accept_header('Accept'):
            for candidate in restformats.values():
                if accept in candidate.accept_content_types:
                    restformat = candidate
                    break
            if restformat is not None:
                break

        if restformat is None:
            for candidate in restformats.values():
                if self._cw.content_type in candidate.accept_content_types:
                    restformat = candidate
                    break

        if restformat is None:
            restformat = restformats['json']

        try:
            methodname = self._cw.form.pop('_ws_method')
            self._cw.form.pop('_ws_etype')
            rtype = self._cw.form.pop('_ws_rtype', None)
            rtype_target = self._cw.form.pop('_ws_rtype_target', None)

            prefix, args = '', []
            if rset is not None and rset.rowcount == 1:
                prefix = 'entity_'
                args.append(rset.one())

            if rtype:
                prefix += 'rtype_'
                args.append(rtype)

            if rtype_target:
                prefix += 'target_'
                args.append(rtype_target)

            methodname = prefix + methodname

            method = getattr(self, methodname, None)

            if method is None or not wsme.api.iswsmefunction(method):
                # XXX Raise a 405 http error
                raise NotFound()

            funcdef = wsme.api.FunctionDefinition.get(method)

            if '_' in self._cw.form:
                del self._cw.form['_']

            self._cw.content.seek(0)
            content = self._cw.content.read()
            self._cw.content.seek(0)
            args, kwargs = wsme.rest.args.get_args(
                funcdef, args, {}, ParamsAdapter(self._cw.form), None,
                content, content_type
            )

            self._cw.set_content_type(restformat.content_type)
            result = method(*args, **kwargs)
            if isinstance(result, wsme.api.Response):
                self._cw.status_out = result.status_code
                result = result.obj
            return restformat.encode_result(result, funcdef.return_type)
        except NotFound:
            self._cw.status_out = 404
            return restformat.encode_error(None, {
                'faultcode': 'Client',
                'faultstring': 'Not Found'
            })
        except ValidationError, e:
            fmtexc = {
                'faultcode': 'Client',
                'faultstring': "ValidationError",
                'errors': e.errors
            }
            self._cw.status_out = 400
            return restformat.encode_error(funcdef, fmtexc)
        except:
            self.exception('Error while calling method {}'.format(methodname))
            self._cw.cnx.rollback()
            exc_info = sys.exc_info()
            fmtexc = wsme.api.format_exception(
                exc_info, debug=self._cw.vreg.config.debugmode)
            if isinstance(exc_info[1], cubicweb.Unauthorized):
                fmtexc['faultcode'] = 'Client'
                self._cw.status_out = 401
            elif fmtexc['faultcode'] == 'Client':
                self._cw.status_out = 400
            elif fmtexc['faultcode'] == 'Server':
                self._cw.status_out = 500
            return restformat.encode_error(funcdef, fmtexc)


class WSCRUDController(WSController):
    """
    An entity type CRUD controller

    The displatch is summarized in this table, where 'entity' means that an
    entity exists in the rset:

    .. csv-table::

        form-rset / verb, GET, POST, PUT, DELETE
        , :meth:`_get`, :meth:`_post`, ,
        entity, :meth:`_entity_get`, , :meth:`_entity_put`, :meth:`_entity_delete`
        "entity, _ws_rtype", :meth:`_entity_rtype_get`, :meth:`_entity_rtype_post`
        "entity, _ws_rtype, _ws_rtype_target", , , , :meth:`_entity_rtype_target_delete`
    """

    #: The entity type
    __cwetype__ = None
    __select__ = yes()

    def _get_entity(self, data):
        """
        Get an entity and update/create it and its related entities all along.

        :param data: A webservice type instance
        """
        eid, values, relation_values = self._handle_data(data)
        if eid:
            entity = self._cw.entity_from_eid(eid)
            if values:
                entity.cw_set(**values)
        else:
            entity = self._cw.create_entity(data.__etype__, **values)
        for (rtype, role, inlined), targets in relation_values.items():
            if role == 'subject' and inlined:
                entity.cw_set(**{rtype: targets})
            if not isinstance(targets, list):
                if targets is None:
                    targets = ()
                else:
                    targets = [targets]
            d = {'x': entity.eid}
            if role == 'subject':
                relation = 'X %s Y' % rtype
            else:
                relation = 'Y %s X' % rtype
            if not targets:
                entity._cw.execute(
                    'DELETE %s WHERE X eid %%(x)s' % relation, d)
            else:
                d.update({'y%s' % i: t.eid for i, t in enumerate(targets)})
                entity._cw.execute(
                    "SET %(relation)s WHERE NOT %(relation)s, X eid %%(x)s, "
                    "Y eid IN (%(list)s)" % {
                        'relation': relation,
                        'list': ', '.join(
                            '%%(y%s)s' % x for x in range(len(targets))
                        )},
                    d)
                entity._cw.execute(
                    "DELETE %(relation)s WHERE %(relation)s, X eid %%(x)s, "
                    "NOT Y eid IN (%(list)s)" % {
                        'relation': relation,
                        'list': ', '.join(
                            '%%(y%s)s' % x for x in range(len(targets))
                        )},
                    d)
        return entity

    def _get_entities(self, datalist):
        """
        Get a list of entities from a list a webservice data
        """
        return [self._get_entity(data) for data in datalist]

    def _handle_data(self, data):
        """
        Handle webservice data.

        It returns a tuple `(eid, values, relation_values)`, where eid can be
        None if the data had none, `values` contains the final and inlined
        values, and `relation_values` the relation values. These variables are
        dictionnaries that can be fed cw_set().

        While handling the entity data, the related entities present in the
        data will be updated/create (via :meth:`_get_entity`).
        """
        eid = data.eid if data.eid else None
        values = {}
        relation_values = {}
        for attr in data._wsme_attributes:
            if not isinstance(attr, wsattr):
                continue
            if attr.rtype == 'eid':
                continue
            value = attr.__get__(data, data.__class__)
            if value is wsme.types.Unset:
                continue
            if attr.isfinal:
                values[attr.rtype] = value
            else:
                if value is not None:
                    if wsme.types.isarray(attr.datatype):
                        value = self._get_entities(value)
                    else:
                        value = self._get_entity(value)
                if attr.inlined:
                    values[attr.rtype] = value
                else:
                    relation_values[
                        (attr.rtype, attr.role, attr.inlined)] = value
        return eid, values, relation_values

    def _update(self, data):
        """ Update an existing entity from ws data"""
        assert data.eid, "missing eid on data"
        return self._get_entity(data)

    def _create(self, data):
        """ Create an entity from ws data"""
        if data.eid:
            raise ValueError(
                "Cannot create with a fixed eid. Please remove it")
        return self._get_entity(data)

    @classmethod
    def __registered__(cls, reg):
        if not hasattr(cls, 'get'):
            cls.get = wsme.api.signature(
                [cls.__cwetype__], [text], JsonData, int, int, [text],
                bool, wrap=True
            )(cls._get)

        if not hasattr(cls, 'post'):
            cls.post = wsme.api.signature(
                cls.__cwetype__, [text], bool, body=cls.__cwetype__, wrap=True
            )(cls._post)

        if not hasattr(cls, 'entity_get'):
            cls.entity_get = wsme.api.signature(
                cls.__cwetype__, PassThroughType, [text], wrap=True
            )(cls._entity_get)

        if not hasattr(cls, 'entity_put'):
            cls.entity_put = wsme.api.signature(
                cls.__cwetype__, PassThroughType, [text], body=cls.__cwetype__,
                wrap=True
            )(cls._entity_put)

        if not hasattr(cls, 'entity_delete'):
            cls.entity_delete = wsme.api.signature(
                None, PassThroughType, [text], wrap=True
            )(cls._entity_delete)

        if not hasattr(cls, 'entity_rtype_post'):
            cls.entity_rtype_post = wsme.api.signature(
                None, PassThroughType, text, body=int, wrap=True
            )(cls._entity_rtype_post)

        if not hasattr(cls, 'entity_rtype_get'):
            cls.entity_rtype_get = wsme.api.signature(
                [Any], PassThroughType, text, [text], int, int,
                bool, wrap=True
            )(cls._entity_rtype_get)

        if not hasattr(cls, 'entity_rtype_target_delete'):
            cls.entity_rtype_target_delete = wsme.api.signature(
                None, PassThroughType, text, int, wrap=True
            )(cls._entity_rtype_target_delete)

        if cls.__select__ is WSCRUDController.__select__:
            cls.__select__ = match_ws_etype(cls.__cwetype__.__name__)

        super(WSCRUDController, cls).__registered__(reg)

    def _get(self, orderby=None, filter=None, limit=0, offset=0, fetch=[],
             keyonly=False):
        """List entities with an optional filter.

        Default implementation of `GET /etype`.

        :param filter:
        :param fetch: A list of relations and subrelations of which the target
                      entities will be returned.
        """
        q = query.Query(self._cw.vreg.schema, self.__cwetype__.__etype__)

        if not keyonly:
            eschema = self._cw.vreg.schema.eschema(self.__cwetype__.__etype__)
            cols = []
            for rschema in eschema.ordered_relations():
                card = eschema.rdef(
                    rschema.type, takefirst=True).cardinality[0]
                if (card in ('*', '+')
                        # cardinality '?' with polymorphic relations raises
                        # https://www.cubicweb.org/ticket/4482382
                        or card == '?' and len(rschema.objects(eschema)) > 1):
                    continue
                if rschema.type in (
                        'eid', 'has_text', 'cw_source', 'cwuri', 'is'):
                    continue
                if rschema.objects()[0].type in ('Password',):
                    continue
                cols.append(rschema.type)
            q = q.add_column(*cols)

        if orderby:
            q = q.orderby(*orderby)
        if filter:
            q = q.filter(FilterParser(
                self._cw.vreg.schema, self.__cwetype__.__etype__, filter
            ).parse())
        if limit:
            q = q.limit(limit)
        if offset:
            q = q.offset(offset)
        return [
            self.__cwetype__(e, keyonly=keyonly, fetch=fetch)
            for e in q.all(self._cw.cnx)]

    def _post(self, fetch=[], keyonly=False, data=None):
        """ Default implementation of `POST /etype`."""
        try:
            entity = self._create(data)
        except:
            self._cw.cnx.rollback()
            raise
        else:
            # XXX We dont really want a commit, just make sure all hooks and
            # operations are done.
            self._cw.cnx.commit()
        return self.__cwetype__(entity, keyonly=keyonly, fetch=fetch)

    def _entity_get(self, entity, fetch=[]):
        """ Default implementation of `GET /etype/eid`."""
        return self.__cwetype__(entity, fetch=fetch)

    def _entity_put(self, entity, fetch=[], data=None):
        """ Default implementation of `PUT /etype/eid`."""
        if not data.eid:
            data.eid = entity.eid
        entity = self._update(data)
        # XXX We dont really want a commit, just make sure all hooks and
        # operations are done.
        self._cw.cnx.commit()
        # XXX We should clear the cache of entity to really have the db data if
        # they were modified by some hooks
        return self.__cwetype__(entity, fetch=fetch)

    def _entity_delete(self, entity):
        """ Default implementation of `DELETE /etype/eid`."""
        entity.cw_delete()
        return wsme.api.Response(None, 204)

    def _entity_rtype_post(self, entity, rtype, eid):
        """ Default implementation of `POST /etype/eid/rtype`."""
        if rtype.startswith('<'):
            rtype = 'reverse_' + rtype[1:]
        entity.cw_set(**{rtype: eid})

    def _entity_rtype_get(self, entity, rtype, orderby=None, limit=None,
                          offset=None, keyonly=False):
        """ Default implementation of `GET /etype/eid/rtype`."""
        if rtype.startswith('<'):
            rtype, role = rtype[1:], 'object'
        else:
            role = 'subject'
        rql = entity.cw_related_rql(rtype, role, limit=limit)
        if offset:
            rql = rql.replace(
                'LIMIT %s' % limit,
                'LIMIT %s OFFSET %s' % (limit, offset))
        if orderby:
            raise NotImplementedError('yet')
        return [
            Any(e, keyonly=keyonly) for e in self._cw.execute(
                rql, {'x': entity.eid}).entities()
        ]

    def _entity_rtype_target_delete(self, entity, rtype, eid):
        """ Default implementation of `DELETE /etype/eid/rtype/eid`."""
        if rtype.startswith('<'):
            rtype = rtype[1:]
            relation = 'X %s E'
        else:
            relation = 'E %s X'
        relation = relation % rtype
        rql = "DELETE " + relation + " WHERE X eid %(x)s, E eid %(e)s"
        self._cw.execute(rql, {'e': entity.eid, 'x': eid})
        return wsme.api.Response(None, 204)
