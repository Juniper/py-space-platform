import logging.config
import ConfigParser

from jnpr.space import rest

class TestDevices:

    def setup_class(self):
        # Initialize logging
        logging.config.fileConfig('../logging.conf')

        # Extract Space URL, userid, password from config file
        config = ConfigParser.RawConfigParser()
        config.read("../test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_devices(self):
        devices_list = self.space.servicenow.device_management.devices.get()
        assert len(devices_list) > 0, "Not enough devices on Service Now"

        for d in devices_list:
            details = d.get()

            assert details.eventProfileInstalltionStatus