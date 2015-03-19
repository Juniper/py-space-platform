"""
This module defines the Application class.
"""
from __future__ import unicode_literals
from builtins import object
import os
import yaml

class Application(object):
    """
    Represents an **application** that is hosted on Junos Space platform.
    Some examples of applications are:

    * Service Now
      (``/api/juniper/servicenow``)

    * Service Insight
      (``/api/juniper/serviceinsight``)

    """

    def __init__(self, rest_end_point, name, values):
        """Initializes an Application object.

        :param rest_end_point: A *Space* object encapsulating the Junos
            Space cluster which hosts this application.
        :type rest_end_point: jnpr.space.rest.Space

        :param str name: Name of this application.

        :param dict values:  Attribute value settings which form the meta data
            for this application. This is read from the descriptions yml file
            for this application.

        """
        self._rest_end_point = rest_end_point
        self._name = name
        self.meta_object = MetaApplication(name, values)
        self._services = {}

    def get_href(self):
        """
        Returns the href of this application.
        """
        return self.meta_object.url

    def __getattr__(self, attr):
        """
        This method is overridden in the class so that web-services
        contained by this instance can be accessed as *normal* Python
        attributes of this object.

        :param str attr: Name of the web-service being accessed.

        :returns: ``jnpr.space.service.Service`` being accessed.
        :raises: AttributeError if there is no service with the given name.

        """
        if attr in self._services:
            return self._services[attr]

        if attr in self.meta_object._meta_services:
            from jnpr.space import service
            value = self.meta_object._meta_services[attr]
            self._services[attr] = service.Service(self._rest_end_point,
                                                   attr, value, self)
            return self._services[attr]

        raise AttributeError("No attribute '%s'" % attr)

class MetaApplication(object):
    """
    Encapsulates the meta data for an application.
    """

    def __init__(self, name, values):
        """Initializes a MetaApplication object.

        :param str key: Name of the application.

        :param dict values:  Attribute value settings which form the meta data
            for this app. This is read from the descriptions yml file for
            this application.

        """
        self.url = values['url']
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        with open(dir_path + '/descriptions/apps/' +
                  name + '/services.yml') as services_file:
            contents = yaml.load(services_file)
            self._meta_services = contents['services']
