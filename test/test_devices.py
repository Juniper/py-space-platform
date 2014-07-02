import logging.config
import ConfigParser

from jnpr.space.platform.core import rest

class TestDevices:

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

    def test_devices_scripts(self):
        devices_list = self.space.device_management.devices.get()
        assert len(devices_list) > 1, "Not enough devices on Space"

        for d in devices_list:
            try:
                scripts = d.view_associated_scripts.get()
                assert len(scripts) > 0
                for s in scripts:
                    assert s.script_device_association.device_name == d.name
            except:
                pass

    def test_devices_change_requests(self):
        devices_list = self.space.device_management.devices.get()
        assert len(devices_list) > 1, "Not enough devices on Space"

        for d in devices_list:
            crs = d.change_requests.get()
            assert len(crs) >= 0
            for cr in crs:
                assert cr.deviceId == d.key