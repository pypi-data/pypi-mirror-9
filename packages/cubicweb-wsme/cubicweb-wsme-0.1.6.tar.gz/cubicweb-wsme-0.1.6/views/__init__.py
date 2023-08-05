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

"""cubicweb-wsme views/forms/actions/components for web ui"""


from cubicweb.web.views.urlpublishing import URLPathEvaluator, PathDontMatch


class RestPathEvaluator(URLPathEvaluator):
    # Priority is set to be have more weight than the default RestPathEvaluator
    priority = 1

    def evaluate_path(self, req, parts):
        if not (0 < len(parts) < 6):
            raise PathDontMatch()
        try:
            etype = self.vreg.case_insensitive_etypes[parts.pop(0).lower()]
        except KeyError:
            raise PathDontMatch()

        accept = set(req.parse_accept_header('Accept'))

        if not accept.intersection(
                ('application/json', 'text/javascript', 'text/xml')):
            raise PathDontMatch()

        # First element must be an etype
        cls = self.vreg['etypes'].etype_class(etype)
        rset = None

        # Get an optional value, ie an entity identifier
        if parts:
            value = parts.pop(0)
            if value in cls.e_schema.subjrels:
                attrname = value
                value = parts.pop(0)
            else:
                attrname = cls.cw_rest_attr_info()[0]
            value = req.url_unquote(value)
            # XXX check the rschema instead
            if attrname == 'eid':
                value = int(value)
            rset = req.find(etype, **{attrname: value})
            if rset.rowcount != 1:
                raise PathDontMatch()

        # Get an optional rtype
        if parts:
            rtype = parts.pop(0)
        else:
            rtype = None

        # Get an optional relation target id
        if parts:
            rtype_target = parts.pop(0)
        else:
            rtype_target = None

        method = parts.pop(0) if parts else req.http_method().lower()
        req.form['_ws_method'] = method
        req.form['_ws_etype'] = etype
        req.form['_ws_rtype'] = rtype
        req.form['_ws_rtype_target'] = rtype_target
        return 'webservice', rset
