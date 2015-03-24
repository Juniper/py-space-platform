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
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import object
import configparser

from jnpr.space import rest, method

class TestResourceAccess(object):

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = configparser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_user(self):
        users = self.space['user-management']['users'].get()
        assert len(users) > 0, "No users present!"

        print(users[0].first_name, users[0]['first-name'])
        assert users[0].first_name == users[0]['first-name']

        print(users[0].read_only, users[0]['read-only'])
        assert users[0].read_only == users[0]['read-only']

        for d in users[0].domains.domain:
            print(d.get('href'), d.id, d.name)
            assert d.get('href').endswith(d.id.text)

    def test_device(self):
        devices = self.space['device-management']['devices'].get()
        assert len(devices) > 0, "No devices present!"

        print(devices[0].domain_id, devices[0]['domain-id'])
        assert devices[0].domain_id == devices[0]['domain-id']

        for d in devices[:1]:
            exp = d['configurations']['raw'].post(xpaths=['/configuration/version'])
            c = exp.configuration
            assert c.version[:7] == d.OSVersion[:7]
            print(c.version, d.OSVersion)

            assert d['exec-resync'] == d.exec_resync
            assert isinstance(d['exec-resync'], method.Method)
