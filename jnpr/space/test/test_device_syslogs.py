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
import pytest
import time

from jnpr.space import rest
from jnpr.space import async

_task_id = 0

@pytest.fixture
def task_id():
    global _task_id
    return _task_id

class TestDeviceSyslogs(object):

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

    def test_get_syslog_events(self):
        tm = async.TaskMonitor(self.space, 'test_SYSLOG_q')
        devices_list = self.space.device_management.devices.get(
                            filter_={'managedStatus': 'In Sync',
                                     'deviceFamily': 'junos'})
        assert len(devices_list) > 0, "Not enough devices on Space"

        try:
            result = self.space.device_management.devices.get_syslog_events.post(
                        task_monitor=tm,
                        devices=devices_list[0:1],
                        text_patterns=['roshan', 'joyce'])

            from pprint import pprint
            pprint(result)

            assert result.id > 0, "Device Get Syslog Events execution Failed"

            global _task_id
            _task_id = result.id

        finally:
            tm.delete()

    def test_stop_syslog_events(self, task_id):
        my_task_id = task_id
        print(my_task_id)
        assert my_task_id > 0

        time.sleep(30)

        result = self.space.device_management.devices.stop_syslog_events.post(
                    id=my_task_id)
        from pprint import pprint
        pprint(result)
