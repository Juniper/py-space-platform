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
from builtins import str
from builtins import object
import configparser

from jnpr.space import rest
from jnpr.space import async

class TestRpc(object):

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = configparser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_rpc_sync(self):
        devices_list = self.space.device_management.devices.get(
                                    filter_={'managedStatus':'In Sync'})
        assert len(devices_list) > 0, "No devices connected!"

        d = devices_list[0]

        result = d.exec_rpc.post(rpcCommand="<get-system-information/>")

        from pprint import pprint
        pprint(result)

        assert result.status == 'Success', "RPC Failed"
        assert result.netConfReplies.netConfReply.replyMsgData['system-information']['os-name'].text.startswith('junos')

    def test_rpc_async(self):
        devices_list = self.space.device_management.devices.get(
                                    filter_={'managedStatus':'In Sync'})
        assert len(devices_list) > 0, "No devices connected!"

        d = devices_list[0]

        tm = async.TaskMonitor(self.space, 'test_rpc_q')

        try:
            result = d.exec_rpc_async.post(
                                        task_monitor=tm,
                                        rpcCommand="<get-system-information/>"
                                       )

            from pprint import pprint
            pprint(result)

            assert result.id > 0, "Async RPC execution Failed"

            pu = tm.wait_for_task(result.id)
            pprint(pu)

            assert (pu.state == "DONE" and pu.status == "SUCCESS" and
                    str(pu.percentage) == "100.0")
        finally:
            tm.delete()

    def test_multiple_rpc_async(self):
        devices_list = self.space.device_management.devices.get(
                                    filter_={'managedStatus':'In Sync'})
        assert len(devices_list) > 0, "No devices connected!"

        tm = async.TaskMonitor(self.space, 'test_rpc_q')

        try:
            task_id_list = []
            for d in devices_list[0:1]:
                result = d.exec_rpc_async.post(
                                            task_monitor=tm,
                                            rpcCommand="<get-system-information/>"
                                           )

                from pprint import pprint
                pprint(result)

                assert result.id > 0, "Async RPC execution Failed"
                task_id_list.append(result.id)

            task_results = tm.wait_for_tasks(task_id_list)
            pprint(task_results)

            assert len(task_results) == len(task_id_list), "Only %d tasks completed" % len(task_results)

            for r in task_results:
                assert (r.state == "DONE" and r.status == "SUCCESS" and
                        str(r.percentage) == "100.0")
                assert r.data is not None
        finally:
            tm.delete()

    def test_resync(self):
        devices_list = self.space.device_management.devices.get(
                                    filter_={'managedStatus':'In Sync'})
        assert len(devices_list) > 0, "No devices connected!"

        d = devices_list[0]

        tm = async.TaskMonitor(self.space, 'test_resync_q')

        try:
            result = d.exec_resync.post(task_monitor=tm)

            from pprint import pprint
            pprint(result)

            assert result.id > 0, "Async Resync execution Failed"

            r = tm.wait_for_task(result.id)
            pprint(r)
            assert (r.state == "DONE" and r.status == "SUCCESS" and
                        str(r.percentage) == "100.0")
            assert r.data is not None
        finally:
            tm.delete()
