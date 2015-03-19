from __future__ import unicode_literals
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import object
import configparser

from jnpr.space import rest

class TestDevices(object):

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = configparser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_devices(self):
        devs = self.space.device_management.devices.get()
        for d in devs:
            print(d.name)

        devices_list = self.space.servicenow.device_management.devices.get()
        assert len(devices_list) > 0, "Not enough devices on Service Now"

        for d in devices_list:
            try:
                if d.deviceGroup is not None:
                    print("%s is already put in group %s" % (d.hostName, d.deviceGroup.id))
            except AttributeError:
                pass
