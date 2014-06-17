from .. import space

class Device(space.Resource):
    """Represents a Device object"""

    def __init__(self, rest_end_point=None, xml_data=None, attrs_dict=None):
        super(Device, self).__init__(rest_end_point, xml_data, attrs_dict)
        self._service_url = DeviceManager.service_url
        self._collection_name = "devices"
        self._xml_name = "device"
        self._media_type = "application/vnd.net.juniper.space.device-management.device+xml;version=1;charset=UTF-8"

    def __str__(self):
        s = "Device <name=%s, ip=%s, model=%s, family=%s, version=%s, serialnum=%s>" % \
          (self.name, self.ipAddr, self.platform, self.deviceFamily, self.OSVersion, self.serialNumber)
        return s

class DeviceCollection(space.Collection):
    """Represents a collection of Devices"""

    def __init__(self, rest_end_point, parent):
        super(DeviceCollection, self).__init__(rest_end_point, 'devices', '/api/space/device-management/devices', parent)

    def _create_resource(self, xml_data):
        return Device(self._rest_end_point, xml_data)


class DeviceManager(space.Service):
    """Encapsulates device-management service"""

    service_name = "device_management"
    service_url = "/api/space/device-management"

    def __init__(self, rest_end_point):
        super(DeviceManager, self).__init__(rest_end_point)
        self._collections['devices'] = DeviceCollection(rest_end_point, self)
