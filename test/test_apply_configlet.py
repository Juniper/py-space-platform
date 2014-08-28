import ConfigParser

from jnpr.space import rest
from jnpr.space import async

class TestApplyConfiglet:

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = ConfigParser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_apply_configlet(self):
        devices_list = self.space.device_management.devices.get(
                                    filter_={'connectionStatus': 'up'})
        assert len(devices_list) > 0, "No devices connected!"

        d = devices_list[0]

        tm = async.TaskMonitor(self.space, 'test_q')

        try:
            result = d.apply_cli_configlet.post(
                                        task_monitor=tm,
                                        configletId = 754773,
                                        parameters={
                                                    'portName' : 'ge-0/0/1',
                                                    'vlanId' : '999',
                                                    'ipAddress': '10.1.2.3/30'
                                                    }
                                       )

            from pprint import pprint
            pprint(result)

            assert result.id > 0, "Async cli configlet execution Failed"

            pu = tm.wait_for_task(result.id)
            pprint(pu)

            assert ((pu.state == "DONE" and pu.percentage == "100.0") or
                (pu.percentage == "100.0" and pu.subTask.state == "DONE"))
        finally:
            tm.delete()