#
# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER
#
# Copyright (c) 2015 Juniper Networks, Inc.
# All rights reserved.
#
# Use is subject to license terms.
#
# Licensed under the Apache License, Version 2.0 (the ?License?); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import object
import configparser
import pytest

from jnpr.space import rest, factory

class TestMiscellaneous(object):

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = configparser.RawConfigParser()
        import os
        config.read(os.path.dirname(os.path.realpath(__file__)) +
                    "/test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_get_collection_with_valid_accept(self):
        jobs = self.space.job_management.jobs.get(
                        accept='application/vnd.net.juniper.space.job-management.jobs+xml;version=2',
                        paging={'start': 0, 'limit': 2})
        assert len(jobs) > 0, "Not enough jobs on Space"

    def test_get_collection_with_invalid_accept(self):
        with pytest.raises(rest.RestException) as except_info:
            self.space.job_management.jobs.get(
                            accept='application/vnd.net.juniper.space.job-management.jobs+xml;version=112',
                            paging={'start': 0, 'limit': 2})
            assert except_info.value.response.status_code == 406

    def test_get_collection_with_empty_accept(self):
        with pytest.raises(rest.RestException) as except_info:
            self.space.job_management.jobs.get(
                            accept='',
                            paging={'start': 0, 'limit': 2})
            assert except_info.value.response.status_code == 406

    def test_post_collection_with_media_types(self):
        rls = self.space.user_management.roles.get()
        assert len(rls) > 0

        r = factory.make_resource(type_name='user_management.role',
                                        rest_end_point=self.space)
        r.href = rls[0].href

        u = factory.make_resource(type_name='user_management.user',
                                        rest_end_point=self.space)
        u.name = 'space_ez_test'
        u.firstName = 'Space'
        u.lastName = 'EZ'
        u.password = '123Juniper'
        u.primaryEmail = 'space_ez_test@juniper.net'
        u.roles = [r]
        u.read_only = False

        u = self.space.user_management.users.post(u,
                accept='application/vnd.net.juniper.space.user-management.user+xml;version=1',
                content_type='application/vnd.net.juniper.space.user-management.user+xml;version=1;charset=UTF-8')
        assert u.id > 0

        rls = u.roles.get()
        assert rls[0].href == r.href

        u.delete()

    def test_post_collection_with_invalid_content_type(self):
        rls = self.space.user_management.roles.get()
        assert len(rls) > 0

        r = factory.make_resource(type_name='user_management.role',
                                        rest_end_point=self.space)
        r.href = rls[0].href

        u = factory.make_resource(type_name='user_management.user',
                                        rest_end_point=self.space)
        u.name = 'space_ez_test'
        u.firstName = 'Space'
        u.lastName = 'EZ'
        u.password = '123Juniper'
        u.primaryEmail = 'space_ez_test@juniper.net'
        u.roles = [r]
        u.read_only = False

        with pytest.raises(rest.RestException) as except_info:
            self.space.user_management.users.post(u,
                    accept='application/vnd.net.juniper.space.user-management.user+xml;version=1',
                    content_type='application/vnd.net.juniper.space.user-management.user+xml;version=11;charset=UTF-8')

        assert except_info.value.response.status_code == 415

    def test_post_collection_with_empty_content_type(self):
        rls = self.space.user_management.roles.get()
        assert len(rls) > 0

        r = factory.make_resource(type_name='user_management.role',
                                        rest_end_point=self.space)
        r.href = rls[0].href

        u = factory.make_resource(type_name='user_management.user',
                                        rest_end_point=self.space)
        u.name = 'space_ez_test'
        u.firstName = 'Space'
        u.lastName = 'EZ'
        u.password = '123Juniper'
        u.primaryEmail = 'space_ez_test@juniper.net'
        u.roles = [r]
        u.read_only = False

        with pytest.raises(rest.RestException) as except_info:
            self.space.user_management.users.post(u,
                    accept='application/vnd.net.juniper.space.user-management.user+xml;version=1',
                    content_type='')

        assert except_info.value.response.status_code == 400

    def test_post_collection_with_invalid_accept(self):
        rls = self.space.user_management.roles.get()
        assert len(rls) > 0

        r = factory.make_resource(type_name='user_management.role',
                                        rest_end_point=self.space)
        r.href = rls[0].href

        u = factory.make_resource(type_name='user_management.user',
                                        rest_end_point=self.space)
        u.name = 'space_ez_test'
        u.firstName = 'Space'
        u.lastName = 'EZ'
        u.password = '123Juniper'
        u.primaryEmail = 'space_ez_test@juniper.net'
        u.roles = [r]
        u.read_only = False

        with pytest.raises(rest.RestException) as except_info:
            self.space.user_management.users.post(u,
                    accept='application/vnd.net.juniper.space.user-management.user+xml;version=111')

        assert except_info.value.response.status_code == 406

    def test_post_collection_with_req_body(self):
        rls = self.space.user_management.roles.get()
        assert len(rls) > 0

        u = self.space.user_management.users.post(
                    content_type='application/vnd.net.juniper.space.user-management.user+xml;version=1;charset=UTF-8',
                    request_body='''
                    <user>
                        <read-only>False</read-only>
                        <primaryEmail>space_ez_test@juniper.net</primaryEmail>
                        <password>123Juniper</password>
                        <name>space_ez_test_2</name>
                        <firstName>Space</firstName>
                        <lastName>EZ</lastName>
                        <roles>
                            <role href="/api/space/user-management/roles/353"/>
                        </roles>
                    </user>
                    ''')
        assert u.id > 0

        rls = u.roles.get()
        u.delete()

    def test_get_resource_with_valid_accept(self):
        users = self.space.user_management.users.get()
        assert len(users) > 0, "Not enough users on Space"
        u = users[0].get(accept='application/vnd.net.juniper.space.user-management.user+xml;version=1')
        assert u.id > 0

    def test_get_resource_with_invalid_accept(self):
        users = self.space.user_management.users.get()
        assert len(users) > 0, "Not enough users on Space"

        with pytest.raises(rest.RestException) as except_info:
            users[0].get(accept='application/vnd.net.juniper.space.user-management.user+xml;version=111')

        assert except_info.value.response.status_code == 406

    def test_get_resource_with_empty_accept(self):
        users = self.space.user_management.users.get()
        assert len(users) > 0, "Not enough users on Space"

        with pytest.raises(rest.RestException) as except_info:
            users[0].get(accept='')

        assert except_info.value.response.status_code == 400

    def test_post_method_with_empty_media_types(self):
        rls = self.space.user_management.roles.get()
        assert len(rls) > 0

        r = factory.make_resource(type_name='user_management.role',
                                        rest_end_point=self.space)
        r.href = rls[0].href

        u = factory.make_resource(type_name='user_management.user',
                                        rest_end_point=self.space)
        u.name = 'space_ez_test'
        u.firstName = 'Space'
        u.lastName = 'EZ'
        u.password = '123Juniper'
        u.primaryEmail = 'space_ez_test@juniper.net'
        u.roles = [r]
        u.read_only = False

        u = self.space.user_management.users.post(u,
                accept='application/vnd.net.juniper.space.user-management.user+xml;version=1',
                content_type='application/vnd.net.juniper.space.user-management.user+xml;version=1;charset=UTF-8')
        assert u.id > 0

        with pytest.raises(rest.RestException) as except_info:
            u.change_password.post(
                                    accept='',
                                    content_type='',
                                    oldPassword='123Juniper',
                                    newPassword='456Juniper')
        assert except_info.value.response.status_code == 400

    def test_post_method_with_invalid_content_type(self):
        us = self.space.user_management.users.get(filter_={'name':'space_ez_test'})
        assert len(us) == 1

        with pytest.raises(rest.RestException) as except_info:
            us[0].change_password.post(
                                accept='application/vnd.net.juniper.space.user-management.change-password+xml;version=1;charset=UTF-8',
                                content_type='application/vnd.net.juniper.space.user-management.change-password+xml;version=111;charset=UTF-8',
                                oldPassword='123Juniper',
                                newPassword='456Juniper')

        assert except_info.value.response.status_code == 415

    def test_post_method_with_invalid_accept(self):
        us = self.space.user_management.users.get(filter_={'name':'space_ez_test'})
        assert len(us) == 1

        with pytest.raises(rest.RestException) as except_info:
            us[0].change_password.post(
                                accept='application/vnd.net.juniper.space.user-management.change-password+xml;version=111;charset=UTF-8',
                                content_type='application/vnd.net.juniper.space.user-management.change-password+xml;version=1;charset=UTF-8',
                                oldPassword='123Juniper',
                                newPassword='456Juniper')

        assert except_info.value.response.status_code == 406

    def test_post_method_with_request_body(self):
        us = self.space.user_management.users.get(filter_={'name':'space_ez_test'})
        assert len(us) == 1

        pwd = us[0].change_password.post(
                                accept='application/vnd.net.juniper.space.user-management.change-password+xml;version=1;charset=UTF-8',
                                content_type='application/vnd.net.juniper.space.user-management.change-password+xml;version=1;charset=UTF-8',
                                request_body='''
                                <change-password>
                                  <oldPassword>123Juniper</oldPassword>
                                  <newPassword>456Juniper</newPassword>
                                </change-password>
                                '''
                                )

        assert pwd.newPassword == '456Juniper'
        us[0].delete()

    def test_post_resource_with_invalid_content_type(self):
        devices_list = self.space.device_management.devices.get(
                            filter_={'managedStatus': 'In Sync'},
                            sortby=['name', 'platform'])
        assert len(devices_list) > 0, "Not enough devices on Space"

        d = devices_list[0]
        with pytest.raises(rest.RestException) as except_info:
            d.configurations.expanded.post(
                                         content_type='123',
                                         xpaths=['/configuration/version',
                                                '/configuration/interfaces/interface[starts-with(name, "ge-")]'])

        assert except_info.value.response.status_code == 400

    def test_post_resource_with_invalid_accept(self):
        devices_list = self.space.device_management.devices.get(
                            filter_={'managedStatus': 'In Sync'},
                            sortby=['name', 'platform'])
        assert len(devices_list) > 0, "Not enough devices on Space"

        d = devices_list[0]
        with pytest.raises(rest.RestException) as except_info:
            d.configurations.expanded.post(
                                         accept='123',
                                         xpaths=['/configuration/version',
                                                '/configuration/interfaces/interface[starts-with(name, "ge-")]'])

        assert except_info.value.response.status_code == 400