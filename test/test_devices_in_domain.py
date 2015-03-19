from __future__ import unicode_literals
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import object
import configparser

from jnpr.space import rest

class TestLogin(object):

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = configparser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd, use_session=True)

    def test_get_devices_in_domains(self):
        ds = self.space.domain_management.domains.get()

        for d in ds[0].children.domain:
            assert d.name
            devices_list = self.space.device_management.devices.get(filter_={'domainId': d.id})
            for dev in devices_list:
                print(dev.name)

    def test_alternate(self):
        ds = self.space.domain_management.domains.get()

        for d in ds[0].children.domain:
            assert d.name
            devices = self.space.device_management.devices.get(domain_id=d.id)
            for d in devices:
                print(d.name, d.ipAddr, d['domain-id'])
