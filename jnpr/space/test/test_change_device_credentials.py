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

from jnpr.space import rest
from jnpr.space import async

class TestChangeDeviceCredentials(object):

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

    def test_change_1(self):
        tm = async.TaskMonitor(self.space, 'test_DC_q')
        devices_list = self.space.device_management.devices.get(
                            filter_={'managedStatus': 'In Sync'})
        assert len(devices_list) > 0, "Not enough devices on Space"

        try:
                result = self.space.device_management.change_device_credentials.post(
                            task_monitor=tm,
                            devices=devices_list[0:2],
                            user_name='regress',
                            password='MaRtInI',
                            change_to='CREDENTIAL',
                            change_on_device=True)

                from pprint import pprint
                pprint(result)

                assert result.id > 0, "Device Change Credential execution Failed"

                pu = tm.wait_for_task(result.id)
                assert (pu.state == "DONE")
                pprint(pu)
        finally:
                tm.delete()
