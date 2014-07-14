import logging.config
import ConfigParser

from jnpr.space.platform.core import rest, async

class TestChangeDeviceCredentials:

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

    def test_change_1(self):
        tm = async.TaskMonitor(self.space, 'test_DC_q')
        devices_list = self.space.device_management.devices.get(
                            filter_={'managedStatus': 'In Sync'})
        assert len(devices_list) > 0, "Not enough devices on Space"

        try:
                result = self.space.device_management.change_device_credentials.post(
                            task_monitor=tm,
                            devices=devices_list,
                            user_name='regress',
                            password='MaRtInI',
                            change_to='MaRtInI2',
                            change_on_device=True)

                from pprint import pprint
                pprint(result)

                assert result.id > 0, "Device Change Credential execution Failed"

                pu = tm.wait_for_task(result.id)
                assert (pu.state == "DONE")
                pprint(pu)
        finally:
                tm.delete()
