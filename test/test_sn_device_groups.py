import ConfigParser

from jnpr.space import rest

class TestDeviceGroups:

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = ConfigParser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_device_groups(self):
        dg_list = self.space.servicenow.device_group_management.device_groups.get()
        assert len(dg_list) >= 0

        for d in dg_list:
            print d.deviceGroupName

        devices_list = self.space.servicenow.device_management.devices.get()
        for d in devices_list:
            d.associateDeviceGroup.post(devicegroup=dg_list[0])
