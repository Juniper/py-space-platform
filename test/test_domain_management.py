from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import object
import configparser

from jnpr.space import rest, factory

class TestDomainManagement(object):

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = configparser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_get_domains(self):
        ds = self.space.domain_management.domains.get()
        assert len(ds) >= 1

    def test_get_domain_children(self):
        ds = self.space.domain_management.domains.get()
        assert len(ds) >= 1

        for d in ds[0].children.domain:
            assert d.name
            dom = factory.fetch_resource(self.space, d.get('href'))
            assert dom.name
            assert dom.id

            us = dom.users.get()
            for u in us:
                user = factory.fetch_resource(self.space, u.get('href'))
                assert user

    def test_add_devices_to_domain(self):
        ds = self.space.domain_management.domains.get()
        assert len(ds) >= 1

        global_devices = self.space.device_management.devices.get(filter_={'domain-id': ds[0].id})
        assert len(global_devices) > 0

        device_to_move = factory.make_resource(type_name='domain_management.device_ref',
                                        rest_end_point=self.space)
        device_to_move.href = global_devices[0].href

        for d in ds[0].children.domain:
            assert d.name
            if d.name == 'test_domain':
                """ Move one device to test_domain """
                dom = factory.fetch_resource(self.space, d.get('href'))
                report = dom.devices.post(device_to_move)
                assert report.status

                """ Move the device back to global domain """
                report = ds[0].devices.post(device_to_move)
                assert report.status

    def test_create_user(self):
        rls = self.space.user_management.roles.get()
        assert len(rls) > 0

        r = factory.make_resource(type_name='user_management.role',
                                        rest_end_point=self.space)
        r.href = rls[0].href

        u = factory.make_resource(type_name='user_management.user',
                                        rest_end_point=self.space)
        u.name = 'space_ez'
        u.firstName = 'Space'
        u.lastName = 'EZ'
        u.password = '123Juniper'
        u.primaryEmail = 'space_ez@juniper.net'
        u.roles = [r]
        u.read_only = False
        u.domain_id = 2

        u = self.space.user_management.users.post(u)
        assert u.id > 0

    def test_add_user_to_domain(self):
        ds = self.space.domain_management.domains.get()
        assert len(ds) >= 1

        usrs = self.space.user_management.users.get(filter_={'name': 'space_ez'})
        assert len(usrs) > 0

        user_to_move = factory.make_resource(type_name='domain_management.user_ref',
                                        rest_end_point=self.space)
        user_to_move.href = usrs[0].href

        for d in ds[0].children.domain:
            assert d.name
            if d.name == 'test_domain':
                """ Assign user to test_domain """
                dom = factory.fetch_resource(self.space, d.get('href'))
                dom.users.post(user_to_move)

    def test_remove_user_from_domain(self):
        ds = self.space.domain_management.domains.get()
        assert len(ds) >= 1

        for d in ds[0].children.domain:
            assert d.name
            if d.name == 'test_domain':
                """ Remove user from test_domain """
                dom = factory.fetch_resource(self.space, d.get('href'))
                usrs = dom.users.get()

                assert len(usrs) == 1

                import pytest
                with pytest.raises(rest.RestException) as except_info:
                    usrs[0].delete()

                assert except_info.value.response.status_code == 412

    def test_delete_user(self):
        us = self.space.user_management.users.get(filter_={'name':'space_ez'})
        if len(us) > 0:
            us[0].delete()
