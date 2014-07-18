import logging.config
import ConfigParser

from juniper.space import rest
from juniper.space import async

class TestRpc:

    def setup_class(self):
        # Initialize logging
        logging.config.fileConfig('./logging.conf')

        # Extract Space URL, userid, password from config file
        config = ConfigParser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_rpc_sync(self):
        devices_list = self.space.device_management.devices.get(
                                    filter_={'connectionStatus': 'up'})
        assert len(devices_list) > 0, "No devices connected!"

        d = devices_list[0]

        result = d.exec_rpc_v1.post(rpcCommand="<get-system-information/>")

        from pprint import pprint
        pprint(result)

        assert result.status == 'Success', "RPC Failed"
        assert result.netConfReplies.netConfReply.replyMsgData.system_information.os_name.startswith('junos')

    def test_rpc_async(self):
        devices_list = self.space.device_management.devices.get(
                                    filter_={'connectionStatus': 'up'})
        assert len(devices_list) > 0, "No devices connected!"

        d = devices_list[0]

        tm = async.TaskMonitor(self.space, 'test_rpc_q')

        try:
            result = d.exec_rpc_v3.post(
                                        task_monitor=tm,
                                        rpcCommand="<get-system-information/>"
                                       )

            from pprint import pprint
            pprint(result)

            assert result.id > 0, "Async RPC execution Failed"

            pu = tm.wait_for_task(result.id)
            pprint(pu)

            assert (pu.state == "DONE" and pu.status == "SUCCESS" and
                    pu.percentage == "100.0")
        finally:
            tm.delete()

    def test_multiple_rpc_async(self):
        devices_list = self.space.device_management.devices.get(
                                    filter_={'connectionStatus': 'up'})
        assert len(devices_list) > 0, "No devices connected!"

        tm = async.TaskMonitor(self.space, 'test_rpc_q')

        try:
            task_id_list = []
            for d in devices_list:
                result = d.exec_rpc_v3.post(
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
                        r.percentage == "100.0")
        finally:
            tm.delete()

    def test_resync(self):
        devices_list = self.space.device_management.devices.get(
                                    filter_={'connectionStatus': 'up'})
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
                        r.percentage == "100.0")
        finally:
            tm.delete()