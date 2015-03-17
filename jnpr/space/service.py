"""
This module defines the Service class.
"""
from builtins import object
import os
import yaml
from jnpr.space import base

class Service(base._SpaceBase):
    """
    Represents a **service** that is exposed by Junos Space REST API.
    Some examples of services are:

    * Device Management
      (``/api/space/device-management``)

    * User Management
      (``/api/space/user-management``)

    """

    def __init__(self, rest_end_point, name, values, application=None):
        """Initializes a Service object.

        :param rest_end_point: A *Space* object encapsulating the Junos
            Space cluster which contains this service.
        :type rest_end_point: jnpr.space.rest.Space

        :param str name: Name of this service.

        :param dict values:  Attribute value settings which form the meta data
            for this service. This is read from the descriptions yml file for
            this service.

        :param application: Application object that exposes this service.
            This defaults to ``None``.
        :type application: jnpr.space.application.Application

        """
        self._rest_end_point = rest_end_point
        self._parent = application
        self._name = name
        self._meta_object = MetaService(name, values, application)
        self._collections = {}
        self._methods = {}

    def get_meta_resource(self, resource_type):
        """Returns the MetaResource object with the given name.

        :param str name: Name of the resource.

        :returns: A ``jnpr.space.resource.MetaResource`` object.

        """
        return self._meta_object.get_meta_resource(resource_type)

    def get_href(self):
        """
        Returns the href of this service.
        """
        return self._meta_object.url

    def __getattr__(self, attr):
        """
        This method is overridden in the class so that collections and
        methods contained by this service can be accessed as *normal* Python
        attributes of this object.

        :param str attr: Name of the attribute being accessed.

        :returns: Collection or Method being accessed.
        :raises: AttributeError if there is no collection or method with the
            given name.

        """
        if attr in self._collections:
            return self._collections[attr]
        if attr in self._methods:
            return self._methods[attr]

        collection = self._meta_object.create_collection(self, attr)
        if collection is not None:
            self._collections[attr] = collection
            return collection
        method = self._meta_object.create_method(self, attr)
        if method is not None:
            self._methods[attr] = method
            return method
        else:
            raise AttributeError

    def __getitem__(self, attr):
        """
        This method is overridden so that contained elements can be accessed
        using their 'xml names' - e.g. user['first-name']. The implementation
        just calls __getattr__ internally.

        See doc for __getattr__ for more details.
        """

        from jnpr.space import xmlutil
        return self.__getattr__(xmlutil.unmake_xml_name(attr))

class MetaService(object):
    """
    Encapsulates the meta data for a service.
    """

    def __init__(self, name, values, application=None):
        """Initializes a MetaService object.

        :param str key: Name of the service.

        :param dict values:  Attribute value settings which form the meta data
            for this service. This is read from the descriptions yml file for
            this service.

        :param application: Application object that exposes this service.
            This defaults to ``None``.
        :type application: jnpr.space.application.Application

        """
        self.url = values['url']
        self._application = application
        self.name = name

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        file_name = dir_path + '/descriptions/'
        if application:
            file_name = file_name + 'apps/' + application._name + '/' + name + '.yml'
        else:
            file_name = file_name + name + '.yml'

        with open(file_name) as contents_file:
            contents = yaml.load(contents_file)
            self.values = contents
            self._meta_collections = contents['collections']
            self._meta_methods = contents['methods']
            self._meta_resources = contents['resources']

    def get_application_name(self):
        """Returns the name of the containing application if there is one.
        """
        if self._application:
            return self._application._name

    def create_collection(self, service, name):
        """Creates a collection object corresponding to the given service and
        name.

        :param str service: Name of the parent service.
        :param str name: Name of the collection.

        :returns: A ``jnpr.space.collection.Collection`` object.

        """
        if name in self._meta_collections:
            from jnpr.space import collection
            m_obj = collection.get_meta_object(self.get_application_name(),
                                               service._name,
                                               name,
                                               self._meta_collections[name])
            return collection.Collection(service, name, m_obj)

    def create_method(self, service, name):
        """Creates a method object corresponding to the given service and
        name.

        :param service: Parent service.
        :type service: jnpr.space.service.Service
        :param str name: Name of the method.

        :returns: A ``jnpr.space.method.Method`` object.

        """
        if name in self._meta_methods:
            from jnpr.space import method
            m_obj = method.get_meta_object(self.get_application_name(),
                                           service._name,
                                           name,
                                           self._meta_methods[name])
            return method.Method(service, name, m_obj)

    def get_meta_resource(self, name):
        """Returns the MetaResource object with the given name.

        :param str name: Name of the resource.

        :returns: A ``jnpr.space.resource.MetaResource`` object.

        """
        return self._meta_resources[name]
