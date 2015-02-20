import ConfigParser

from jnpr.space import rest, async

class TestChangeRequests:

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = ConfigParser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_get_change_requests(self):
        crs = self.space.configuration_management.change_requests.get(paging={
                    'start':0, 'limit':5})
        assert len(crs) > 0, "No change-requests on Space!"

    def test_get_change_request_details(self):
        crs = self.space.configuration_management.change_requests.get()
        n = len(crs)
        assert n > 0, "No change-requests on Space!"

        for cr in crs[n-2:]:
            details = cr.get()
            assert details

    def test_one_change_request_sync(self):
        devices = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos', 'connectionStatus': 'up'})
        assert len(devices) > 1, 'No Junos devices present on Space!'

        cr = self.space.configuration_management.change_requests.v2_single.post(
                    name = 'Test-from-space-ez',
                    description = 'Test case for space-ez via PyTest',
                    device = devices[1],
                    xmlData = '''<configuration>
                                   <snmp>
                                     <contact>space-ez Test Case</contact>
                                   </snmp>
                                 </configuration>''')

        assert cr.result, "Did not get a result"

    def test_multiple_change_requests_sync(self):
        devices = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos', 'connectionStatus': 'up'})
        assert len(devices) > 1, 'Not enough Junos devices present on Space!'

        crs = self.space.configuration_management.change_requests.v2_multiple.post(
                    name = 'Test-from-space-ez',
                    description = 'Test case for space-ez via PyTest',
                    devices = devices[len(devices)-2:],
                    xmlData = '''<configuration>
                                   <snmp>
                                     <contact>space-ez Test Case</contact>
                                   </snmp>
                                 </configuration>''')

        assert crs

    def test_multiple_change_requests_async(self):
        tm = async.TaskMonitor(self.space, 'test_cr_q')

        try:
            devices = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos', 'connectionStatus': 'up'})
            assert len(devices) > 1, 'Not enough Junos devices present on Space!'

            result = self.space.configuration_management.change_requests.v2_multiple_async.post(
                    task_monitor = tm,
                    name = 'Test-from-space-ez',
                    description = 'Test case for space-ez via PyTest',
                    devices = devices[len(devices)-2:],
                    xmlData = '''<configuration>
                                   <snmp>
                                     <contact>space-ez Test Case</contact>
                                   </snmp>
                                 </configuration>''')

            pu = tm.wait_for_task(result.id)

            assert pu
        finally:
            tm.delete()