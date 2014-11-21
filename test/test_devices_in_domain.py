import ConfigParser

from jnpr.space import rest

class TestLogin:

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = ConfigParser.RawConfigParser()
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
                print dev.name

    def test_alternate(self):
        ds = self.space.domain_management.domains.get()

        for d in ds[0].children.domain:
            assert d.name
            devices = self.space.device_management.devices.get(domain_id = d.id)
            for d in devices:
                print d.name, d.ipAddr, d['domain-id']
