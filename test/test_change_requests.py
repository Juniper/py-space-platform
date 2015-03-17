from future import standard_library
standard_library.install_aliases()
from builtins import object
import configparser

from jnpr.space import rest, async, factory

class TestChangeRequests(object):

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = configparser.RawConfigParser()
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

        for cr in crs[n - 2:]:
            details = cr.get()
            assert details

    def test_push_to_one_device(self):
        devices = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos', 'connectionStatus': 'up'})
        assert len(devices) > 1, 'No Junos devices present on Space!'

        cr = self.space.configuration_management.change_requests.push_to_one_device.post(
                    name='Test-from-space-ez',
                    description='Test case for space-ez via PyTest',
                    device=devices[1],
                    xmlData='''<configuration>
                                   <snmp>
                                     <contact>space-ez Test Case</contact>
                                   </snmp>
                                 </configuration>''')

        assert cr.result, "Did not get a result"

    def test_push_to_many_devices(self):
        devices = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos', 'connectionStatus': 'up'})
        assert len(devices) > 1, 'Not enough Junos devices present on Space!'

        crs = self.space.configuration_management.change_requests.push_to_many_devices.post(
                    name='Test-from-space-ez',
                    description='Test case for space-ez via PyTest',
                    devices=devices[len(devices) - 2:],
                    xmlData='''<configuration>
                                   <snmp>
                                     <contact>space-ez Test Case</contact>
                                   </snmp>
                                 </configuration>''')

        assert crs

    def test_push_to_many_devices_async(self):
        tm = async.TaskMonitor(self.space, 'test_cr_q')

        try:
            devices = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos', 'connectionStatus': 'up'})
            assert len(devices) > 1, 'Not enough Junos devices present on Space!'

            result = self.space.configuration_management.change_requests.push_to_many_devices_async.post(
                    task_monitor=tm,
                    name='Test-from-space-ez',
                    description='Test case for space-ez via PyTest',
                    devices=devices[len(devices) - 2:],
                    xmlData='''<configuration>
                                   <snmp>
                                     <contact>space-ez Test Case</contact>
                                   </snmp>
                                 </configuration>''')

            pu = tm.wait_for_task(result.id)

            assert pu
        finally:
            tm.delete()

    def test_one_change_request_sync(self):
        devices = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos', 'connectionStatus': 'up'})
        assert len(devices) > 1, 'No Junos devices present on Space!'

        chg = factory.make_resource(type_name='configuration_management.change_request',
                                        rest_end_point=self.space)
        chg.name = 'Test-single-cr-1'
        chg.description = 'Testing post on collection for one object'
        chg.device = {'href': devices[1].href}
        chg.xmlData = '''<![CDATA[<configuration>
                           <snmp>
                             <contact>Test-single-cr-1</contact>
                           </snmp>
                         </configuration>]]> '''
        cr = self.space.configuration_management.change_requests.post(
                    new_obj=chg,
                    accept='application/vnd.net.juniper.space.configuration-management.change-request+xml;version=2;q=.02',
                    content_type='application/vnd.net.juniper.space.configuration-management.change-request+xml;version=2;charset=UTF-8')

        assert cr.name == chg.name, "Did not get the same CR back"

    def test_many_change_requests_sync(self):
        devices = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos', 'connectionStatus': 'up'})
        assert len(devices) > 1, 'No Junos devices present on Space!'

        chgs = []
        for d in devices[len(devices) - 2:]:
            chg = factory.make_resource(type_name='configuration_management.change_request',
                                            rest_end_point=self.space)
            chg.name = 'Test-multiple-cr-sync'
            chg.description = 'Testing post on collection for many objects'
            chg.device = {'href': d.href}
            chg.xmlData = '''<![CDATA[<configuration>
                               <snmp>
                                 <contact>Test-multiple-cr-sync</contact>
                               </snmp>
                             </configuration>]]> '''
            chgs.append(chg)

        crs = self.space.configuration_management.change_requests.post(
                    new_obj=chgs,
                    accept='application/vnd.net.juniper.space.configuration-management.change-requests+xml;version=2;q=.02',
                    content_type='application/vnd.net.juniper.space.configuration-management.change-requests+xml;version=2;charset=UTF-8')

        assert len(crs) == len(chgs), "Did not get the same number of CRs back"

    def test_many_change_requests_async(self):
        devices = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos', 'connectionStatus': 'up'})
        assert len(devices) > 1, 'No Junos devices present on Space!'

        chgs = []
        for d in devices[len(devices) - 2:]:
            chg = factory.make_resource(type_name='configuration_management.change_request',
                                            rest_end_point=self.space)
            chg.name = 'Test-multiple-cr-async'
            chg.description = 'Testing post on collection for many objects - async'
            chg.device = {'href': d.href}
            chg.xmlData = '''<![CDATA[<configuration>
                               <snmp>
                                 <contact>Test-multiple-cr-async</contact>
                               </snmp>
                             </configuration>]]> '''
            chgs.append(chg)

        tm = async.TaskMonitor(self.space, 'test_q')

        try:
            task = self.space.configuration_management.change_requests.post(
                    new_obj=chgs,
                    accept='application/vnd.net.juniper.space.job-management.task+xml;version=1;q=.01',
                    content_type='application/vnd.net.juniper.space.configuration-management.change-requests+xml;version=2;charset=UTF-8',
                    task_monitor=tm)

            assert task.id, "Did not get Task back"

            pu = tm.wait_for_task(task.id)

            assert pu.state
        finally:
            tm.delete()
