import os
import yaml

class Service(object):
    """
    Represents a **service** that is exposed by Junos Space REST API.
    Some examples of services are:

    * Device Management
      (``/api/space/device-management``)

    * User Management
      (``/api/space/user-management``)

    """

    def __init__(self, rest_end_point, name, values):
        """Initializes a Service object.

        :param rest_end_point: A *Space* object encapsulating the Junos
            Space cluster which contains this service.
        :type rest_end_point: jnpr.space.rest.Space

        :param str name: Name of this service.

        :param dict values:  Attribute value settings which form the meta data
            for this service. This is read from the descriptions yml file for
            this service.

        """
        self._rest_end_point = rest_end_point
        self._name = name
        self.meta_object = MetaService(name, values)
        self._collections = {}
        self._methods = {}

    def get_meta_resource(self, resource_type):
        """Returns the MetaResource object with the given name.

        :param str name: Name of the resource.

        :returns: A ``jnpr.space.resource.Resource`` object.

        """
        return self.meta_object.get_meta_resource(resource_type)

    def get_href(self):
        """
        Returns the href of this service.
        """
        return self.meta_object.url

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

        collection = self.meta_object.create_collection(self, attr)
        if collection is not None :
            self._collections[attr] = collection
            return collection
        method = self.meta_object.create_method(self, attr)
        if method is not None:
            self._methods[attr] = method
            return method
        else:
            raise AttributeError

class MetaService(object):
    """
    Encapsulates the meta data for a service.
    """

    def __init__(self, name, values):
        """Initializes a MetaService object.

        :param str key: Name of the service.

        :param dict values:  Attribute value settings which form the meta data
            for this service. This is read from the descriptions yml file for
            this service.

        """
        self.url = values['url']
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        with open(dir_path + '/descriptions/' + name + '.yml') as f:
            y = yaml.load(f)
            self._meta_collections = y['collections']
            self._meta_methods = y['methods']
            self._meta_resources = y['resources']

    def create_collection(self, service, name):
        """Creates a collection object corresponding to the given service and
        name.

        :param str service: Name of the parent service.
        :param str name: Name of the collection.

        :returns: A ``jnpr.space.collection.Collection`` object.

        """
        if name in self._meta_collections:
            from jnpr.space import collection
            mObj = collection.get_meta_object(name, self._meta_collections[name])
            return collection.Collection(service, name, mObj)

    def create_method(self, service, name):
        """Creates a method object corresponding to the given service and
        name.

        :param str service: Name of the parent service.
        :param str name: Name of the method.

        :returns: A ``jnpr.space.method.Method`` object.

        """
        if name in self._meta_methods:
            from jnpr.space import method
            mObj = method.get_meta_object(service._name, name, self._meta_methods[name])
            return method.Method(service, name, mObj)

    def get_meta_resource(self, name):
        """Returns the MetaResource object with the given name.

        :param str name: Name of the resource.

        :returns: A ``jnpr.space.resource.Resource`` object.

        """
        return self._meta_resources[name]