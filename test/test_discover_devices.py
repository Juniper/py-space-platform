"""
DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER

Copyright (c) 2015 Juniper Networks, Inc.
All rights reserved.

Use is subject to license terms.

Licensed under the Apache License, Version 2.0 (the ?License?); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.
"""
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import object
import configparser

from jnpr.space import rest
from jnpr.space import async

class TestDiscoverDevices(object):

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = configparser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_discover_devices_later(self):
        tm = async.TaskMonitor(self.space, 'test_DD_q')
        try:
            result = self.space.device_management.discover_devices.post(
                        task_monitor=tm,
                        schedule='(after(00 01))',
                        hostName='test-host-name',
                        manageDiscoveredSystemsFlag=True,
                        userName='regress', password='MaRtInI')

            from pprint import pprint
            pprint(result)

            assert result.id > 0, "Device Discovery execution Failed"

            pu = tm.wait_for_task(result.id)
            assert (pu.state)
            pprint(pu)
        finally:
            tm.delete()

    def test_discover_devices_1(self):
        tm = async.TaskMonitor(self.space, 'test_DD_q')
        try:
            result = self.space.device_management.discover_devices.post(
                        task_monitor=tm,
                        hostName='test-host-name',
                        manageDiscoveredSystemsFlag=True,
                        userName='regress', password='MaRtInI')

            from pprint import pprint
            pprint(result)

            assert result.id > 0, "Device Discovery execution Failed"

            pu = tm.wait_for_task(result.id)
            assert (pu.state)
            pprint(pu)
        finally:
            tm.delete()

    def test_discover_devices_2(self):
        tm = async.TaskMonitor(self.space, 'test_DD_q')
        try:
            result = self.space.device_management.discover_devices.post(
                        task_monitor=tm,
                        ipAddress='1.1.1.1',
                        usePing=True,
                        manageDiscoveredSystemsFlag=True,
                        userName='regress', password='MaRtInI')

            from pprint import pprint
            pprint(result)

            assert result.id > 0, "Device Discovery execution Failed"

            pu = tm.wait_for_task(result.id)
            assert (pu.state)
            pprint(pu)
        finally:
            tm.delete()

    def test_discover_devices_3(self):
        tm = async.TaskMonitor(self.space, 'test_DD_q')
        try:
            result = self.space.device_management.discover_devices.post(
                        task_monitor=tm,
                        ipAddress='2.1.1.1',
                        usePing=True,
                        useSnmp=True,
                        manageDiscoveredSystemsFlag=True,
                        snmpV1Setting={'communityName': 'public'},
                        userName='regress', password='MaRtInI')

            from pprint import pprint
            pprint(result)

            assert result.id > 0, "Device Discovery execution Failed"

            pu = tm.wait_for_task(result.id)
            assert (pu.state)
            pprint(pu)
        finally:
            tm.delete()

    def test_discover_devices_4(self):
        tm = async.TaskMonitor(self.space, 'test_DD_q')
        try:
            result = self.space.device_management.discover_devices.post(
                        task_monitor=tm,
                        ipAddress='10.155.67.5',
                        usePing=True,
                        useSnmp=True,
                        manageDiscoveredSystemsFlag=True,
                        snmpV2CSetting={'communityName': 'public'},
                        userName='root', password='junk123')

            from pprint import pprint
            pprint(result)

            assert result.id > 0, "Device Discovery execution Failed"

            pu = tm.wait_for_task(result.id)
            assert (pu.state)
            pprint(pu)
        finally:
            tm.delete()

    def test_discover_devices_5(self):
        tm = async.TaskMonitor(self.space, 'test_DD_q')
        try:
            result = self.space.device_management.discover_devices.post(
                        task_monitor=tm,
                        lowerIp='5.1.1.1', upperIp='5.1.1.2',
                        usePing=True,
                        useSnmp=True,
                        manageDiscoveredSystemsFlag=True,
                        snmpV3Setting={'userName': 'user1',
                                       'authenticationPassword': 'pwd1',
                                       'authenticationType': 'MD5'},
                        userName='regress', password='MaRtInI')

            from pprint import pprint
            pprint(result)

            assert result.id > 0, "Device Discovery execution Failed"

            pu = tm.wait_for_task(result.id)
            assert (pu.state)
            pprint(pu)
        finally:
            tm.delete()
