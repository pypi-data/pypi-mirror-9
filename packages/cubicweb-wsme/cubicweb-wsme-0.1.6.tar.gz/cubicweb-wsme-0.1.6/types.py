# -*- coding: utf-8 -*-
# copyright 2014 UNLISH, all rights reserved.
# contact http://www.unlish.com/ -- mailto:christophe@unlish.com
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
Types
"""

import base64
import inspect
import itertools
import json
import re

import six
import wsme
import wsme.types
import wsme.rest.args
import wsme.rest.json

from cubicweb import Unauthorized, Binary


class PassThroughType(object):
    """Special webservice type that transmit a value without doing anything

    It is used in wsme signature for the 'entity' argument which is passed by
    the controller itself and should not be transtyped in any way."""

    @classmethod
    def validate(self, value):
        return value


@wsme.rest.args.from_param.when_object(PassThroughType)
def any_from_param(datatype, value):
    return value


class JsonDataType(wsme.types.UserType):
    name = 'json'
    basetype = wsme.types.text

    def frombasetype(self, value):
        if value is None:
            return value
        return json.loads(value)

    def tobasetype(self, value):
        return json.dumps(value)

    @classmethod
    def validate(self, value):
        return value

#: User type that carry json encoded arbitrary data.
JsonData = JsonDataType()


@wsme.rest.json.fromjson.when_object(JsonData)
def jsondata_fromjson(datatype, value):
    return value


class wsattr(wsme.types.wsattr):
    """Cubicweb-specific version of :class:`wsme.types.wsattr`

    To be used on a :class:`Base` class.
    All the attributes are optionnal and can be deduced from the :attr:`rtype`.

    .. attribute:: rtype

        The corresponding relation in the model

    .. attribute:: role

        The role of the parent class in the relation

    .. attribute:: etype

        The entity type on the other side of the relation

    .. attribute:: datatype

        The webservice type
    """
    def __init__(
            self, rtype=None, role='subject', etype=None, datatype=None, **kw):
        super(wsattr, self).__init__(datatype, **kw)
        self.rtype = rtype
        self.role = role
        self.etype = etype

    def reginit(self, vreg, class_):
        if self.rtype is None:
            self.rtype = self.name
        rschema = vreg.schema.rschema(self.rtype)
        self.isfinal = rschema.final
        self.inlined = rschema.inlined

        etypes = rschema.targets(
            None if class_.__etype__ == 'Any' else class_.__etype__, self.role)
        if self.role == 'subject':
            self.rname = self.rtype
        elif self.role == 'object':
            self.rname = 'reverse_' + self.rtype

        if self.etype is None:
            # Autodetect the etype
            if len(etypes) != 1:
                self.etype = 'Any'
            else:
                self.etype = etypes[0].type

        else:
            # check that the etype is valid
            if self.etype == 'Any':
                if len(etypes) == 1:
                    raise ValueError(
                        'Any should not be used on non-polymorphic relations')
            else:
                if self.etype not in etypes:
                    raise ValueError(
                        'Wrong etype %s for relation %s %s' %
                        (self.etype, self.rtype, self.role))

    def finalize_init(self, class_):
        if self.datatype is not None and self.datatype != [None]:
            return

        rschema = class_.__registry__.vreg.schema.rschema(self.rtype)
        datatype = class_.__registry__.guess_datatype(self.etype)

        if class_.__etype__ == 'Any' or self.etype == 'Any':
            needarray = False
            for rdef in rschema.rdefs.values():
                if rdef.role_cardinality(self.role) in '+*':
                    needarray = True
                    break
        else:
            rdef = rschema.role_rdef(class_.__etype__, self.etype, self.role)
            needarray = rdef.role_cardinality(self.role) in '+*'
        if needarray:
            datatype = wsme.types.ArrayType(datatype)
        self.datatype = datatype


def iswsattr(obj):
    """returns True if an object is a :class:`wsattr`"""
    return isinstance(obj, wsattr)


class BaseMeta(wsme.types.BaseMeta):
    """
    Metaclass for :class:`Base`

    Bypass the wsme.types.BaseMeta __new__ and __init__
    because they set a default __registry__
    """

    def __new__(cls, name, bases, dct):
        return type.__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        pass


class Base(six.with_metaclass(BaseMeta, wsme.types.Base)):
    """Base class for a complex type that map an entity type
    """
    #: Entity eid
    eid = long

    __autoexclude__ = (
        'is', 'identity', 'cw_source',
        'is_instance_of', 'has_text')

    def __init__(self, entity=None, keyonly=False, fetch=()):
        if entity:
            self.from_entity(entity, keyonly, fetch)

    @classmethod
    def reginit(cls, vreg):
        """ Register the class

        Use the informations in the registry, and most notably the schema, to
        initialize the  attributes.
        """
        if getattr(cls, '__autoattr__', False):
            eschema = vreg.schema.eschema(cls.__etype__)

            existing_rels = set(
                (attr.rtype, attr.role)
                for name, attr in inspect.getmembers(cls, iswsattr))

            if cls.__autoattr__ is True:
                rels = itertools.chain(
                    ((rel, 'subject', rel.type) for rel in
                        eschema.subject_relations()),
                    ((rel, 'object', '<' + rel.type) for rel in
                        eschema.object_relations()))
            else:
                rels = itertools.chain(
                    ((eschema.subjrels[name], 'subject', name)
                     for name in cls.__autoattr__
                     if not name.startswith('<')),
                    ((eschema.objrels[name[1:]], 'object', name)
                     for name in cls.__autoattr__
                     if name.startswith('<')))
            rels = (
                (rel, role, name)
                for rel, role, name in rels
                if name not in cls.__autoexclude__
                and (rel.type, role) not in existing_rels
            )
            for rel, role, name in rels:
                key = rel.type
                if role == 'object':
                    key += '_object'
                setattr(
                    cls, key,
                    wsattr(rel.type, role=role, name=name))

        vreg.wsme_registry.register(cls)

        for attr in cls._wsme_attributes:
            if isinstance(attr, wsattr):
                attr.reginit(vreg, cls)

    @classmethod
    def finalize_init(cls):
        """ Finalize the class initialization.

        This last step resolve types in the underlying attributes.
        """
        for attr in cls._wsme_attributes:
            if isinstance(attr, wsattr):
                attr.finalize_init(cls)

    _rtype_re = re.compile(u'(?P<rtype>[^.[]+)\[(?P<etypes>[^\]]+)\]')

    def from_entity(self, entity, keyonly=False, fetch=()):
        """ Load values from an entity

        :param entity: the entity
        :param keyonly: if `True`, only the .eid and .modfication_date will be
                        loaded. The result can be used as "timestamped
                        reference".
        :param fetch: a list of relations to eager load. Unless specified, all
                      the '1' or '?' relation targets will be loaded as
                      'keyonly', and the '*' or '+' relations will not be
                      loaded at all.
        """
        self.eid = entity.eid
        self.modification_date = entity.modification_date

        if keyonly:
            # Append the modification_date
            return

        typed_fetch = {
            m.group('rtype'): m.group('etypes').split(',')
            for m in (
                self._rtype_re.match(f) for f in fetch) if m is not None}

        for attr in self._wsme_attributes:
            if not isinstance(attr, wsattr):
                continue

            if attr.isfinal:
                subfetch = None
            else:
                prefix = attr.name + '.'
                prefixlen = len(prefix)
                subfetch = [
                    x[prefixlen:] for x in fetch if x.startswith(prefix)
                ]

            if wsme.types.isarray(attr.datatype):
                if not attr.name in fetch \
                        and not attr.name in typed_fetch \
                        and not subfetch:
                    continue

            if attr.name in typed_fetch:
                value = entity.related(
                    attr.rtype, role=attr.role, entities=True,
                    targettypes=typed_fetch[attr.name])
            else:
                try:
                    value = getattr(entity, attr.rname)
                except Unauthorized:
                    # XXX set value = Forbidden ?
                    continue

            if not attr.isfinal:
                attr_keyonly = not subfetch
                if wsme.types.isarray(attr.datatype):
                    if value:
                        value = [
                            attr.datatype.item_type(
                                o,
                                keyonly=attr_keyonly,
                                fetch=subfetch)
                            for o in value
                        ]
                    else:
                        value = []
                else:
                    if value:
                        value = attr.datatype(
                            value[0],
                            keyonly=attr_keyonly,
                            fetch=subfetch
                        )
                    else:
                        value = None

            attr.__set__(self, value)

    def final_values(self):
        """ Returns a dict with all the attribute values.

        This dict can be used to feed :meth:`cubicweb.entity.Entity.cw_set`.
        """
        values = {}
        for attr in self._wsme_attributes:
            if isinstance(attr, wsattr):
                if attr.isfinal:
                    value = attr.__get__(self, self.__class__)
                    if value is not wsme.types.Unset:
                        values[attr.rtype] = value
        return values

    def to_entity(self, entity):
        """ Update the entity attributes (not the non-final relations).
        """
        values = self.final_values()
        if values:
            entity.cw_set(**values)


class Any(Base):
    """Complex type to carry any type of entity.

    Automatically used for polymorphic relations targets
    """

    __etype__ = 'Any'

    cw_etype = wsme.types.text

    created_by = wsattr()
    creation_date = wsattr()

    modification_date = wsattr()

    owned_by = wsattr()

    def from_entity(self, entity, keyonly=False, fetch=()):
        self.cw_etype = entity.cw_etype
        super(Any, self).from_entity(
            entity, keyonly=keyonly, fetch=())


class BinaryType(wsme.types.UserType):
    basetype = wsme.types.bytes
    name = 'binary'

    def tobasetype(self, value):
        if value is not None:
            return base64.encodestring(value.getvalue())

    def frombasetype(self, value):
        if value is not None:
            return Binary(base64.decodestring(value))


#: webservice type that map the :class:`cubicweb.Binary` values.
binary = BinaryType()


def scan(vreg, modname):
    """Scan a module for any class inheriting :class:`Base` and register them.
    """
    mod = __import__(modname)
    if '.' in modname:
        for token in modname.split('.')[1:]:
            mod = getattr(mod, token)

    for name, value in inspect.getmembers(mod):
        if inspect.isclass(value) and issubclass(value, Base):
            value.reginit(vreg)
