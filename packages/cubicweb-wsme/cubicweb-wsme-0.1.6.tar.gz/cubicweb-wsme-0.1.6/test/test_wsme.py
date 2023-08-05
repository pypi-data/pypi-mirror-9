# copyright 2014 Christophe de Vienne, all rights reserved.
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

"""cubicweb-wsme tests
"""

import base64
import json
import urllib

import wsme

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.devtools.httptest import CubicWebServerTC
import cubicweb

from cubes.wsme.types import Base, wsattr


class WSMETest(CubicWebTC):
    @classmethod
    def init_config(cls, config):
        super(WSMETest, cls).init_config(config)
        config.debugmode = True

    def test_types_final_rel(self):
        class ACWUser(Base):
            __etype__ = 'CWUser'
            login = wsattr('login', datatype=wsme.types.text)
            # XXX in real-life, the upassword would never be copied from an
            # entity to a ws type, only from a ws type to an entity (with
            # encryption at the same time)
            password = wsattr('upassword', datatype=wsme.types.text)

        ACWUser.reginit(self.vreg)

        with self.admin_access.repo_cnx() as cnx:
            u = cnx.find("CWUser", login=u"admin").one()
            u_eid = u.eid
            ws_u = ACWUser(u)

        self.assertEqual(u_eid, ws_u.eid)
        self.assertEqual(u"admin", ws_u.login)

        ws_u.login = u"anotherone"
        ws_u.password = 'somepassword'
        with self.admin_access.repo_cnx() as cnx:
            cls = self.vreg['etypes'].etype_class('CWUser')
            u = cls.cw_instantiate(cnx.execute, **ws_u.final_values())

            self.assertNotEqual(u_eid, u.eid)
            self.assertEqual(u"anotherone", ws_u.login)

    def test_types_final_rel_autoattr(self):
        class ACWUser(Base):
            __etype__ = 'CWUser'

            login = wsattr()
            password = wsattr('upassword')

        ACWUser.reginit(self.vreg)
        self.vreg.wsme_registry.finalize_init()

        with self.admin_access.repo_cnx() as cnx:
            u = cnx.find("CWUser", login=u"admin").one()
            u_eid = u.eid
            ws_u = ACWUser(u)

        self.assertEqual(u_eid, ws_u.eid)
        self.assertEqual(u"admin", ws_u.login)

    def test_types_relations(self):
        class ACWUser(Base):
            __etype__ = 'CWUser'

            login = wsattr('login', datatype=wsme.types.text)
            # XXX in real-life, the upassword would never be copied from an
            # entity to a ws type, only from a ws type to an entity (with
            # encryption at the same time)
            password = wsattr('upassword', datatype=wsme.types.text)

            in_group = wsattr('in_group', datatype=['ACWGroup'])

        class ACWGroup(Base):
            __etype__ = 'CWGroup'

            name = wsattr('name', datatype=wsme.types.text)
            users = wsattr('in_group', role='object', datatype=[ACWUser])

        ACWUser.reginit(self.vreg)
        ACWGroup.reginit(self.vreg)

        with self.admin_access.repo_cnx() as cnx:
            u = cnx.find("CWUser", login=u"admin").one()
            u_eid = u.eid
            g_eid = u.in_group[0].eid
            ws_u = ACWUser(u, fetch=['in_group'])
            ws_u2 = ACWUser(u, fetch=['in_group.name'])

        self.assertEqual(u_eid, ws_u.eid)
        self.assertEqual(u"admin", ws_u.login)

        self.assertEqual(g_eid, ws_u.in_group[0].eid)
        self.assertEqual(u"managers", ws_u2.in_group[0].name)

    def test_polymorphic_relations(self):
        State = self.vreg.wsme_registry.lookup('State')

        with self.admin_access.repo_cnx() as cnx:
            state = cnx.find('State', name='activated').one()
            tr_eid = state.allowed_transition[0].eid
            tr_created_by_eid = state.allowed_transition[0].created_by[0].eid
            ws_state = State(state, fetch=['allowed_transition.created_by'])

        self.assertEqual(tr_eid, ws_state.allowed_transition[0].eid)
        self.assertEqual('Transition', ws_state.allowed_transition[0].cw_etype)
        self.assertEqual(
            tr_created_by_eid,
            ws_state.allowed_transition[0].created_by.eid)

    def test_object_relations(self):
        CWGroup = self.vreg.wsme_registry.lookup('CWGroup')
        self.assertTrue(hasattr(CWGroup, 'in_group_object'))
        self.assertEqual('<in_group', CWGroup.in_group_object.name)


class WSMECRUDTest(CubicWebServerTC):
    @classmethod
    def init_config(cls, config):
        super(WSMECRUDTest, cls).init_config(config)
        config.debugmode = True

    def test_cwuser_get(self):
        url = 'cwuser?' + urllib.urlencode({'filter': '{"login": "anon"}'})
        res = self.web_request(
            url, headers={"Accept": "application/json"})
        if '<!DOCTYPE html>' in res.body:
            import html2text
            print html2text.html2text(res.body)
        data = json.loads(res.body)
        self.assertNotIn('faultstring', data)
        self.assertEqual(u"anon", data[0]['login'])

    def test_cwuser_get_keyonly(self):
        url = 'cwuser?' + urllib.urlencode({'keyonly': True})
        res = self.web_request(
            url, headers={"Accept": "application/json"})
        if '<!DOCTYPE html>' in res.body:
            import html2text
            print html2text.html2text(res.body)
        data = json.loads(res.body)
        self.assertNotIn('login', data[0])
        self.assertIn('modification_date', data[0])

    def test_cwuser_entity_get(self):
        url = 'cwuser/anon?fetch=in_group'
        res = self.web_request(
            url, headers={"Accept": "application/json"})
        if '<!DOCTYPE html>' in res.body:
            import html2text
            print html2text.html2text(res.body)
        data = json.loads(res.body)
        self.assertEqual(u"anon", data['login'])
        self.assertEqual(1, len(data['in_group']))
        self.assertIn('modification_date', data['in_group'][0])

    def test_cwuser_entity_get_fetch_typed_relation(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.find('CWGroup', name=u'managers').one().cw_set(
                created_by=cnx.find('CWUser', login=u'admin').one())
            cnx.commit()
        self.web_login()
        url = 'cwuser/admin?fetch=<created_by[CWGroup]'
        res = self.web_request(
            url, headers={"Accept": "application/json"})
        if '<!DOCTYPE html>' in res.body:
            import html2text
            print html2text.html2text(res.body)
        data = json.loads(res.body)
        self.assertEqual(200, res.status, data)
        self.assertEqual(u"admin", data['login'])
        self.assertEqual(1, len(data['<created_by']))
        self.assertIn('modification_date', data['<created_by'][0])

    def test_cwgroup_post(self):
        self.web_login()
        url = 'cwgroup'
        res = self.web_request(
            url, method='POST',
            body='{"name": "test"}',
            headers={"Accept": "application/json",
                     "Content-Type": "application/json"})
        if '<!DOCTYPE html>' in res.body:
            import html2text
            print html2text.html2text(res.body)
            assert False

        data = json.loads(res.body)
        self.assertEqual(200, res.status, data)

        self.assertEqual(u"test", data['name'])
        g_eid = data['eid']

        with self.admin_access.repo_cnx() as cnx:
            self.assertEqual(u"test", cnx.entity_from_eid(g_eid).name)

    def test_cwgroup_entity_put(self):
        with self.admin_access.repo_cnx() as cnx:
            g_eid = cnx.create_entity('CWGroup', name=u'test').eid
            cnx.commit()

        self.web_login()
        url = 'cwgroup/test'
        res = self.web_request(
            url, method='PUT',
            body='{"name": "newname"}',
            headers={"Accept": "application/json",
                     "Content-Type": "application/json"})
        if '<!DOCTYPE html>' in res.body:
            import html2text
            print html2text.html2text(res.body)
            assert False
        self.assertEqual(200, res.status)
        with self.admin_access.repo_cnx() as cnx:
            self.assertEqual(u"newname", cnx.entity_from_eid(g_eid).name)

    def test_cwgroup_entity_delete(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity('CWGroup', name=u'test').eid
            cnx.commit()

        self.web_login()
        url = 'cwgroup/test'
        res = self.web_request(
            url, method='DELETE', headers={"Accept": "application/json"})
        if '<!DOCTYPE html>' in res.body:
            import html2text
            print html2text.html2text(res.body)
            assert False
        self.assertEqual(204, res.status)

    def test_multi_create(self):
        self.web_login()

        res = self.web_request(
            'cwuser?fetch=in_group', method='POST',
            headers={"Accept": "application/json",
                     "Content-Type": "application/json"},
            body=json.dumps({
                'login': "AUser", 'password': "APassword",
                'in_group': [{
                    'name': 'ANewGroup'
                }]
            }),
        )

        data = json.loads(res.body)
        self.assertNotIn('faultcode', data)

        self.assertEqual(200, res.status)

        g_eid = data['in_group'][0]['eid']
        with self.admin_access.repo_cnx() as cnx:
            self.assertEqual(u"ANewGroup", cnx.entity_from_eid(g_eid).name)

    def test_multi_update(self):
        with self.admin_access.repo_cnx() as cnx:
            g_eid = cnx.find('CWGroup', name=u'managers').one().eid

        self.web_login()

        res = self.web_request(
            'cwuser/admin?fetch=in_group', method='PUT',
            headers={"Accept": "application/json",
                     "Content-Type": "application/json"},
            body=json.dumps({
                'surname': 'Admin',
                'in_group': [{
                    'eid': g_eid,
                    'name': 'newname'
                }]
            }),
        )

        data = json.loads(res.body)
        self.assertNotIn('faultcode', data)

        self.assertEqual(200, res.status)

        self.assertEqual(u'Admin', data['surname'])
        self.assertEqual(g_eid, data['in_group'][0]['eid'])

        with self.admin_access.repo_cnx() as cnx:
            self.assertEqual(u"newname", cnx.entity_from_eid(g_eid).name)

    def test_update_and_create(self):
        with self.admin_access.repo_cnx() as cnx:
            g_eid = cnx.find('CWGroup', name=u'managers').one().eid

        self.web_login()

        res = self.web_request(
            'cwuser/admin?fetch=in_group', method='PUT',
            headers={"Accept": "application/json",
                     "Content-Type": "application/json"},
            body=json.dumps({
                'surname': "AdminName",
                'in_group': [{
                    'name': 'ANewGroup'
                }, {
                    'eid': g_eid,
                }]
            }),
        )

        data = json.loads(res.body)
        self.assertNotIn('faultcode', data)

        self.assertEqual(200, res.status)

        g_eid = data['in_group'][0]['eid']
        with self.admin_access.repo_cnx() as cnx:
            self.assertEqual(u"ANewGroup", cnx.entity_from_eid(g_eid).name)

    def test_create_and_update(self):
        with self.admin_access.repo_cnx() as cnx:
            g_eid = cnx.find('CWGroup', name=u'managers').one().eid

        self.web_login()

        res = self.web_request(
            'cwuser', method='POST',
            headers={"Accept": "application/json",
                     "Content-Type": "application/json"},
            body=json.dumps({
                'login': "AUser", 'password': "APassword",
                'in_group': [{
                    'eid': g_eid,
                    'name': 'NewName'
                }]
            }),
        )

        data = json.loads(res.body)
        self.assertNotIn('faultcode', data)

        self.assertEqual(200, res.status)

        with self.admin_access.repo_cnx() as cnx:
            self.assertEqual(u"NewName", cnx.entity_from_eid(g_eid).name)

    def test_get_relation(self):
        self.web_login()

        res = self.web_request(
            'cwgroup/managers/<in_group?keyonly=1&limit=2', method='GET',
            headers={"Accept": "application/json",
                     "Content-Type": "application/json"})

        data = json.loads(res.body)
        self.assertNotIn('faultcode', data)

        self.assertEqual(200, res.status)
        self.assertEqual(1, len(data))
        self.assertEqual('CWUser', data[0]['cw_etype'])

    def test_add_relation(self):
        with self.admin_access.repo_cnx() as cnx:
            u_eid = cnx.find('CWUser', login=u'anon').one().eid

        self.web_login()

        res = self.web_request(
            'cwgroup/managers/<in_group',
            method='POST',
            body=str(u_eid),
            headers={"Accept": "application/json",
                     "Content-Type": "application/json"})

        self.assertEqual(200, res.status)

        with self.admin_access.repo_cnx() as cnx:
            g = cnx.find('CWGroup', name=u'managers').one()
            u = cnx.find('CWUser', login=u'anon').one()

            self.assertIn(g, u.in_group)

    def test_del_relation(self):
        with self.admin_access.repo_cnx() as cnx:
            u = cnx.find('CWUser', login=u'anon').one()
            g = cnx.find('CWGroup', name=u'managers').one()
            u.cw_set(in_group=g)
            g_eid = g.eid
            cnx.commit()

        self.web_login()

        res = self.web_request(
            'cwuser/anon/in_group/%s' % (g_eid),
            method='DELETE',
            headers={"Accept": "application/json"})

        self.assertEqual(204, res.status)

        with self.admin_access.repo_cnx() as cnx:
            u = cnx.find('CWUser', login=u'anon').one()

            self.assertEqual(1, len(u.in_group))

    def test_get_binary(self):
        with self.admin_access.repo_cnx() as cnx:
            f = cnx.create_entity(
                'File', data=cubicweb.Binary('test'),
                data_name=u'filename',
                data_format=u'text/plain')
            cnx.commit()
            eid = f.eid

        self.web_login()

        res = self.web_request(
            'file/{}'.format(eid),
            headers={"Accept": "application/json"})

        data = json.loads(res.body)
        self.assertNotIn('faultcode', data)
        self.assertEqual(200, res.status)

        self.assertEqual(data['data'], base64.encodestring('test'))

    def test_set_binary(self):
        with self.admin_access.repo_cnx() as cnx:
            f = cnx.create_entity(
                'File', data=cubicweb.Binary('test'),
                data_name=u'filename',
                data_format=u'text/plain')
            cnx.commit()
            eid = f.eid

        self.web_login()

        res = self.web_request(
            'file/{}'.format(eid),
            method='PUT',
            body=json.dumps({"data": base64.encodestring('newcontent')}),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"})

        data = json.loads(res.body)
        self.assertNotIn('faultcode', data)
        self.assertEqual(200, res.status)

        self.assertEqual(data['data'], base64.encodestring('newcontent'))

        with self.admin_access.repo_cnx() as cnx:
            f = cnx.entity_from_eid(eid)
            self.assertEqual(f.data.getvalue(), 'newcontent')


class WSMEQueryTest(CubicWebServerTC):
    @classmethod
    def init_config(cls, config):
        super(WSMEQueryTest, cls).init_config(config)
        config.debugmode = True

    def test_orderby(self):
        self.web_login()

        res = self.web_request(
            'cwuser?orderby=login',
            method='GET',
            headers={"Accept": "application/json"})

        data = json.loads(res.body)
        self.assertNotIn('faultcode', data)
        self.assertEqual(
            ['admin', 'anon'],
            [d['login'] for d in data])

        res = self.web_request(
            'cwuser?orderby=-login',
            method='GET',
            headers={"Accept": "application/json"})

        data = json.loads(res.body)
        self.assertNotIn('faultcode', data)
        self.assertEqual(
            ['anon', 'admin'],
            [d['login'] for d in data])

    def test_limit(self):
        self.web_login()

        res = self.web_request(
            'cwuser?limit=1',
            method='GET',
            headers={"Accept": "application/json"})

        data = json.loads(res.body)
        self.assertEqual(1, len(data))

    def test_offset(self):
        self.web_login()

        # we need a limit because sqlite seems not to like an offset without a
        # limit
        res = self.web_request(
            'cwuser?limit=1&offset=2',
            method='GET',
            headers={"Accept": "application/json"})

        data = json.loads(res.body)
        self.assertNotIn('faultcode', data)
        self.assertEqual(0, len(data))

    def test_filter_on_one_attribute(self):
        self.web_login()

        res = self.web_request(
            'cwuser?' + urllib.urlencode({
                'filter': json.dumps({
                    'login': 'admin'
                })
            }),
            method='GET',
            headers={"Accept": "application/json"}
        )

        data = json.loads(res.body)
        self.assertNotIn('faultcode', data)

        self.assertEqual(1, len(data))
        self.assertEqual(u'admin', data[0]['login'])

    def test_filter_on_attribute_and_relation(self):
        self.web_login()

        res = self.web_request(
            'cwuser?' + urllib.urlencode({
                'filter': json.dumps({
                    'login': {'$ne': 'anon'},
                    'in_group': {
                        'name': 'managers'
                    }
                })
            }),
            method='GET',
            headers={"Accept": "application/json"}
        )

        data = json.loads(res.body)
        self.assertNotIn('faultcode', data)

        self.assertEqual(1, len(data))
        self.assertEqual(u'admin', data[0]['login'])

    def test_unset_relation(self):
        with self.admin_access.repo_cnx() as cnx:
            g_eid = cnx.create_entity('CWGroup', name=u'test').eid
            cnx.find('CWUser', login=u'admin').one().cw_set(in_group=g_eid)
            cnx.commit()

        self.web_login()

        url = 'cwgroup/test'
        res = self.web_request(
            url, method='PUT',
            body='{"<in_group": null}',
            headers={"Accept": "application/json",
                     "Content-Type": "application/json"})
        if '<!DOCTYPE html>' in res.body:
            import html2text
            print html2text.html2text(res.body)
            assert False
        self.assertEqual(200, res.status)
        with self.admin_access.repo_cnx() as cnx:
            self.assertEqual(
                (),
                cnx.entity_from_eid(g_eid).reverse_in_group)
