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

from jnpr.space import rest, async

class TestSchemas(object):

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
        self.space = rest.Space(url, user, passwd, use_session=True)

    def test_get_ununsed_schemas(self):
        schemas = self.space.schema_management.unused_schemas.get()
        print(len(schemas))
        assert len(schemas) > 0, "No unused schemas on Space"

        for s in schemas:
            print(s.os_version, s.dev_family)

    def test_install_schemas_svn(self):
        schemas = [{'release': '12.3R8.7', 'device-family': 'junos'}]

        tm = async.TaskMonitor(self.space, 'test_schema_q')
        try:
            task = self.space.schema_management.install_schemas_svn.post(
                                                                         task_monitor=tm,
                                                                         schemas=schemas)

            assert task.id > 0

            pu = tm.wait_for_task(task.id)
            assert pu.state == 'DONE' and pu.status == "Success"
        finally:
            tm.delete()

    def test_install_schemas_tgz(self):
        schemas = [{'schema-location': '/var/tmp/1.tgz',
                    'release': '12.3R8.7',
                    'device-family': 'junos'}]

        tm = async.TaskMonitor(self.space, 'test_schema_q')
        try:
            task = self.space.schema_management.install_schemas_tgz.post(
                                                                         task_monitor=tm,
                                                                         schemas=schemas)

            assert task.id > 0

            pu = tm.wait_for_task(task.id)
            assert pu.state == 'DONE' and pu.status == "Success"
        finally:
            tm.delete()

"""
    def test_delete_unused_schema(self):
        schemas = self.space.schema_management.unused_schemas.get()
        print(len(schemas))
        assert len(schemas) > 2, "Not enough unused schemas on Space"

        tm = async.TaskMonitor(self.space, 'test_schema_q')
        try:
            task = self.space.schema_management.delete_schemas.post(task_monitor=tm,
                                                                    dmi_schema_infos=schemas[0:2])

            assert task.id > 0

            pu = tm.wait_for_task(task.id)
            assert pu.state == 'DONE' and pu.status == "Success"
        finally:
            tm.delete()
"""