from pprint import pformat
from lxml import etree, objectify
from jinja2 import Environment, PackageLoader

from jnpr.space import xmlutil, util, rest

class Resource(object):
    """
    Represents a **resource** that is exposed by Junos Space REST API.
    Some examples of resources are:

    * A device (``/api/space/device-management/devices/{id}``)
    * Configuration of a device \
      (``/api/space/device-management/devices/{id}/configurations/raw``)
    * A user (``/api/space/user-management/users/{id}``)
    * A tag (``/api/space/tag-management/tags/{id}``)

    """

    def __init__(self, type_name, rest_end_point,
                 xml_data=None, attributes=None, parent=None):
        """Initializes a Resource object.

        :param str type_name: Fully qualified type name for the Resource to be
            created. It is of the format ``<service_name>.<resource_type>`` or
            ``<app-name>.<service_name>.<resource_type>``
            Some examples are:

            * ``device_management.device``
            * ``user_management.user``
            * ``servicenow.device_management.device``

        :param rest_end_point: A *Space* object encapsulating the Junos
            Space cluster which contains this resource.
        :type rest_end_point: jnpr.space.rest.Space

        :param lxml.etree.Element xml_data:  The state of the resource as an
            XML object. This defaults to ``None``.

        :param dict attributes:  The state of the resource as a dict where the
            keys are attribute names and values are attribute values.
            This defaults to ``None``.

        :param parent: The parent object of this resource. This defaults to
            ``None``.
        :type parent: jnpr.space.collection.Collection

        """
        self._type_name = type_name
        self._rest_end_point = rest_end_point
        self._xml_data = xml_data
        self._attributes = attributes
        self._parent = parent
        self._collections = {}
        self._methods = {}
        self._init_meta_data(rest_end_point, type_name)
        if xml_data is not None:
            if self._meta_object.xml_name != xml_data.tag:
                e = Exception('Invalid xml object for this resource!')
                e.ignore = True
                raise e
            self._xml_data = xmlutil.xml2obj(etree.tostring(xml_data))

    def _init_meta_data(self, rest_end_point, type_name):
        """
        Helper method to initialize meta data for this resource.
        """
        parts = type_name.split('.')
        if len(parts) == 3:
            app_name = parts[0]
            service_name = parts[1]
            resource_type = parts[2]
            try:
                app = rest_end_point.__getattr__(app_name)
            except AttributeError:
                raise Exception("Unknown service name in '%s'" % type_name)

            try:
                service = app.__getattr__(service_name)
            except AttributeError:
                raise Exception("Unknown service name in '%s'" % type_name)
        elif len(parts) == 2:
            app = None
            service_name = parts[0]
            resource_type = parts[1]
            try:
                service = rest_end_point.__getattr__(service_name)
            except AttributeError:
                raise Exception("Unknown service name in '%s'" % type_name)
        else:
            raise Exception("Invalid resource type given: '%s'" % type_name)

        try:
            values = service.get_meta_resource(resource_type)
            self._meta_object = get_meta_object(type_name, values)
        except KeyError:
            raise Exception("Unknown resource type in '%s'" % type_name)

    def __getattr__(self, attr):
        """
        This method is overridden in the class so that collections and
        methods contained by this resource can be accessed as *normal* Python
        attributes of this object. For example, if ``d`` is an object
        representing a *device* resource, ``d.exec_rpc`` gives access to the
        contained *exec-rpc* method. Also, ``d.configurations`` gives access
        to the contained *configurations* collection.

        If the given attr name does not match the name of a contained
        collection or method (based on meta object data), then it is passed on
        to the contained _xml_data for look-up. For example,
        ``d.platform`` will return the ``platform`` field value of the device
        object's XML representation.

        :param str attr: Name of the attribute being accessed.

        :returns: Collection or Method or the XML data field being accessed.
        """
        if attr in self._collections:
            return self._collections[attr]

        if attr in self._methods:
            return self._methods[attr]

        collection = self._meta_object.create_collection(self, attr)
        if collection is not None :
            self._collections[attr] = collection
            return collection

        method = self._meta_object.create_method(self, attr)
        if method is not None:
            self._methods[attr] = method
            return method

        # Check if it is an XML attribute
        thing = self._xml_data.get(attr)
        if thing is not None:
            return thing

        return self._xml_data[xmlutil.make_xml_name(attr)]
        # return self._xml_data.__getattr__(attr) # For issue #27

        """
        Fix for issue #19
        xml_name = util.make_xml_name(attr)

        # Check if it is an element in xml data
        el = self._xml_data.find(xml_name)
        if el is not None:
            return el.text

        # Check if it is an attribute in xml data
        val = self._xml_data.get(xml_name)
        if val is not None:
            return val
        else:
            raise AttributeError("No attribute '%s'" % attr)
        """

    def __getitem__(self, attr):
        """
        This method is overridden so that contained elements can be accessed
        using their 'xml names' - e.g. user['first-name']. The implementation
        just calls __getattr__ internally.

        See doc for __getattr__ for more details.
        """

        return self.__getattr__(xmlutil.unmake_xml_name(attr))

    def get_meta_object(self):
        """Returns the meta object which holds meta data for this resource.

        :returns: ``jnpr.space.resource.MetaResource``
        """
        return self._meta_object

    def _get_xml_attr(self, attr):
        """Returns the named XML attribute from the XML data element contained
        by this resource.

        :returns: Value of the named attribute
        :raises: ``AttributeError`` if there is no such XML attribute
        """
        return self._xml_data.get(attr)

    def get(self, attr=None, version=None):
        """
        This is an overloaded method that does two things: If the ``attr``
        parameter is passed, it returns the corresponding XML attribute from
        the top level XML data element contained by this resource. If the
        ``attr`` parameter is not passed, it performs an HTTP GET for
        this resource and get its current state.

        :returns:
            - Value of the named XML attribute. OR
            - The current state of this resource fetched from Space and
              represented as a Python object. You can access the fields of the
              resource's state directly as attributes of this object.

        :raises: ``jnpr.space.rest.RestException`` if the GET method results in an
            error response. The exception's ``response`` attribute will have the
            full response from Space.

        """
        if attr is not None:
            return self._get_xml_attr(attr)

        mtype = self._meta_object.get_media_type(version)
        if mtype is not None:
            if not self._meta_object.retain_charset_in_accept:
                end = mtype.find(';charset=')
                if end > 0:
                    mtype = mtype[0:end]
            headers = {'accept' : mtype}
        else:
            headers = {}

        response = self._rest_end_point.get(self.get_href(), headers)
        if response.status_code != 200:
            raise rest.RestException("GET failed on %s" % self.get_href(),
                                     response)

        #r = response.text
        r = response.content # Fix as part of issue #27
        return xmlutil.xml2obj(r)

    def put(self, new_val_obj = None, version=None):
        """Modifies the state of this resource on Space by sending a PUT request
        with the new state. The attributes of *new_val_obj* are
        formatted to form the XML request body for the PUT request. If the
        parameter *new_val_obj* is ``None``, then the attributes of this object
        itself are formatted to form the XML request body. Once the PUT request
        successfully completes, it re-initializes the state of this Resource
        object based on the XML response from Space.

        :param new_val_obj: A Resource object with the newly desired state for
            the resource. This defaults to ``None``.
        :type new_val_obj: jnpr.space.resource.Resource

        :returns: ``None``
        :raises: ``jnpr.space.rest.RestException`` if the PUT method results in
            an error response. The exception's ``response`` attribute will have
            the full response from Space.

        """
        if new_val_obj is not None:
            x = new_val_obj.form_xml()
        else:
            x = self.form_xml()

        response = self._rest_end_point.put(
                            self.get_href(),
                            {'content-type': self.get_meta_object().get_media_type(version)},
                            etree.tostring(x)
                        )
        if response.status_code != 200:
            raise rest.RestException("PUT failed on %s" % self.get_href(),
                                     response)

        # Fixing issue #17
        #r = response.text
        # Skip the <?xml> line to avoid encoding errors in lxml
        #start = r.index('?><') + 2
        #root = etree.fromstring(r[start:])
        #root = etree.fromstring(response.content)

        # Fixing issue #19 self._xml_data = root
        self._xml_data = xmlutil.xml2obj(response.content) # Changed text to content

    def delete(self):
        """Deletes this resource on Space by sending a DELETE request with the
        url of this resource.

        :returns: ``None``
        :raises: ``jnpr.space.rest.RestException`` if the DELETE method results
            in an error response. The exception's ``response`` attribute will
            have the full response from Space.

        """
        if self._meta_object.use_uri_for_delete:
            url = self._xml_data.get('uri')
            if url is None:
                url = '/'.join([self._parent.get_href(), str(self.id)])
        else:
            url = self.get_href()
        response = self._rest_end_point.delete(url)
        if response.status_code != 204 and response.status_code != 200 and \
           response.status_code != 202:
            raise rest.RestException("DELETE failed on %s" % url, response)

    def post(self, task_monitor=None, schedule=None, *args, **kwargs):
        """
        Some resources support the POST method. For example, the configuration
        of a device supports the POST method which can be used to fetch
        selected portions of the configuration based on xpath expressions.
        On such resources, this method can be used to send the POST request.

        :param task_monitor: A TaskMonitor object that can be used to monitor
            the progress of the POST request, in case of asynchronous
            invocations. You need to check Junos Space API documentation to
            see if the POST invocation on this resource has asynchronous
            semantics and supply the task_monitor parameter only if it is
            asynchronous. Otherwise, this will default to ``None`` and the
            method will behave with synchronous semantics.
        :type task_monitor: jnpr.space.async.TaskMonitor

        :param str schedule: A string specifying a cron expression for
            scheduling the execution of the request on the Space server side.
            This is applicable only if the POST invocation on this resource
            has asynchronous semantics and you want to schedule the execution.
            Otherwise, this will default to ``None``.

        :param kwargs: Keyword args of the form name=value which will be used
            to substitute variables in a pre-defined template (if applicable)
            to form the request body.
        :type kwargs: A variable list of name=value arguments.

        :returns: A Python object constructed from the response body that Space
            returned for the POST method invocation. In the case of asynchronous
            invocation, this will represent a Task object and will contain the
            unique id of the Task executing the POST request in Space.

        :raises: ``jnpr.space.rest.RestException`` if the POST method results in
            an error response. The exception's ``response`` attribute will have
            the full response from Space.

        """
        url = self.get_href()
        if task_monitor:
            url = '?queue='.join([url, task_monitor.get_queue_url()])
            if schedule:
                url = '&schedule='.join([url, schedule])

        headers = {}
        if self._meta_object.response_type:
            headers['accept'] = self._meta_object.response_type

        if self._meta_object.request_template:
            body = self._meta_object.request_template.render(**kwargs)
            headers['content-type'] = self._meta_object.request_type
        else:
            body = None

        response = self._rest_end_point.post(url,headers,body)
        if (response.status_code != 202) and (response.status_code != 200):
            raise rest.RestException("POST failed on %s" % url, response)

        return xmlutil.xml2obj(xmlutil.cleanup(response.content)) # Changed text to content

    def get_href(self):
        """Gets the href for this resource. If ``href`` is available as an attr
        inside _xml_data, it is returned. Otherwise, this method checks if
        _xml_data has a valid ``uri`` attr and if so, returns that. Otherwise,
        it checks if the _parent reference is set and if yes, it will concat
        the parent's href with the ``id`` attr from _xml_data. If all this
        fail, then it concatentates ``service_url`` and ``collection_name``
        from its meta object and appends the ``id`` attr from _xml_data.

        :returns: The href of this resource.

        """
        if self._xml_data is not None:
            h = self._xml_data.get('href')
            # Fixing issue #19 h = self._xml_data.get('href')
            if h:
                return h

            u = self._xml_data.get('uri')
            if u and not u.endswith(self._meta_object.collection_name):
                return u

        if self._parent:
            return '/'.join([self._parent.get_href(), str(self.id)])

        """
        if self._xml_data is not None:
            h = self._xml_data.uri # Fixing issue #19 h = self._xml_data.get('uri')
            # Working around problems in Space API.
            # E.g. equipment-holder does not have href, but only uri
            if h and not h.endswith(self._meta_object.collection_name):
                # Working around problems in Space API.
                # E.g. A newly created tag returns uri (but no href) in the
                # POST response. But the uri does not end with the id
                # of the tag!
                return h
        """
        return self._meta_object.service_url + "/" + self._meta_object.collection_name + "/" + str(self.id)

    def form_xml(self):
        """Forms an XML representation of the state of this resource based on
        its attribute values.

        :returns: An ``lxml.etree.Element`` object representing the state of
            this resource.

        """
        e = etree.Element(self._meta_object.xml_name)
        attributes = {}
        if self._attributes is not None:
            attributes = self._attributes
        else:
            attributes = self.__dict__

        for key, value in attributes.iteritems():
            if key.startswith('_'):
                continue

            xml_name = util.make_xml_name(key)
            if xml_name == 'href':
                e.attrib[xml_name] = str(value)
            elif isinstance(value, Resource):
                e.append(value.form_xml())
            elif isinstance(value, list):
                l = etree.SubElement(e, xml_name)
                for each in value:
                    l.append(each.form_xml());
            elif isinstance(value, dict):
                l = etree.SubElement(e, xml_name)
                for k, v in value.iteritems():
                    if k == 'href':
                        l.attrib[k] = str(v)
                    else:
                        etree.SubElement(l, util.make_xml_name(k)).text = str(v)
            else:
                etree.SubElement(e, xml_name).text = str(value)

        return e

    def __str__(self):
        return pformat(self, depth=6)

    def xml_string(self):
        """
        Returns a string that contains formatted XML representing the
        state of this resource.
        """
        if self._xml_data is not None:
            return etree.tostring(self._xml_data, pretty_print=True)
        else:
            return 'No XML data'

    def xml_data(self):
        """
        Returns a formatted string that represents the state of this resource.
        """
        if self._xml_data is not None:
            return objectify.dump(self._xml_data)
        else:
            return 'No XML data'

"""
A dictionary that acts as a cache for meta objects representing resources.
Keys are of the form ``<service-name>.<type_name>``. Values are instances of
jnpr.space.resource.MetaResource.
"""
_meta_resources = {}

def get_meta_object(full_name, values):
    """Looks up the meta object for a resource based on its fully qualified
    type name of the form ``<service-name>.<type_name>`` or
    ``<app-name>.<service-name>.<type_name>``

    :param str full_name: Fully qualified type name of the resource.

    :returns: A ``jnpr.space.resource.MetaResource`` object.

    """
    if full_name in _meta_resources:
        return _meta_resources[full_name]

    parts = full_name.split('.')
    if len(parts) == 3:
        app_name = parts[0]
        service_name = parts[1]
        resource_type = parts[2]
    elif len(parts) == 2:
        app_name = None
        service_name = parts[0]
        resource_type = parts[1]
    else:
        raise Exception("Invalid resource type given: '%s'" % full_name)

    m = MetaResource(app_name, service_name, resource_type, values)
    _meta_resources[full_name] = m
    return m

class MetaResource(object):
    """ Encapsulates the meta data for a resource type.
    """

    def __init__(self, app_name, service_name, key, values):
        """Initializes a MetaResource object.

        :param str app_name: Name of the app to which this resource
            belongs. Some examples are:

            * ``servicenow``
            * ``serviceinsight``

        :param str service_name: Name of the service to which this resource
            belongs. Some examples are:

            * ``device_management``
            * ``user_management``

        :param str key: Type name of the resource. Some examples are:

            * ``device``
            * ``user``

        :param dict values:  Attribute value settings which form the meta data
            for this resource. This is read from the descriptions yml file for
            the corresponding service.

        """
        self.app_name = app_name
        self.service_name = service_name
        self.key = key
        self.name = values['name'] \
            if ('name' in values) else None
        self.xml_name = values['xml_name'] \
            if ('xml_name' in values) else None
        self.media_type = values['media_type'] \
            if ('media_type' in values) else None
        self.retain_charset_in_accept = values['retain_charset_in_accept'] \
            if ('retain_charset_in_accept' in values) else False
        self.collection_name = values['collection_name'] \
            if ('collection_name' in values) else None
        self.service_url = values['service_url'] \
            if ('service_url' in values) else None
        self.use_uri_for_delete = values['use_uri_for_delete'] \
            if ('use_uri_for_delete' in values) else False
        self.collections = {}
        self.methods = {}

        self.request_type = values['request_type'] \
            if ('request_type' in values) else None
        self.response_type = values['response_type'] \
            if 'response_type' in values else None

        if 'request_template' in values:
            env = Environment(loader=PackageLoader('jnpr.space',
                                                   'templates'))
            self.request_template = env.get_template(values['request_template'])

        try:
            from jnpr.space import collection
            for key in values['collections']:
                value = values['collections'][key]
                mObj = collection.get_meta_object(self.app_name,
                                                  self.service_name,
                                                  self.key + ':' + key,
                                                  value)
                self.collections[key] = mObj
        except KeyError:
            pass

        try:
            from jnpr.space import method
            for key in values['methods']:
                value = values['methods'][key]
                mObj = method.get_meta_object(self.app_name,
                                              self.service_name,
                                              key,
                                              value)
                self.methods[key] = mObj
        except KeyError:
            pass

    def get_media_type(self, version):
        if isinstance(self.media_type, dict):
            if version is not None:
                return self.media_type[str(version)]
            if len(self.media_type) == 1:
                return self.media_type.itervalues().next()
            else:
                raise Exception("You must specify the required media-type version")
        elif version is None:
            return self.media_type

        raise Exception("Version %s not defined for '%s' in descriptions!" %
                        (str(version), self.key))

    def create_collection(self, resrc, name):
        """Creates a collection object.

        :param resrc: Parent resource.
        :type resrc: jnpr.space.resource.Resource

        :param str name: Name of the collection.

        :returns: A ``jnpr.space.collection.Collection`` object.

        """
        if name in self.collections:
            from jnpr.space import collection
            return collection.Collection(resrc, name, self.collections[name])

    def create_method(self, resrc, name):
        """Creates a method object.

        :param resrc: Parent resource.
        :type resrc: jnpr.space.resource.Resource

        :param str name: Name of the method.

        :returns: A ``jnpr.space.method.Method`` object.

        """
        if name in self.methods:
            from jnpr.space import method
            mObj = method.get_meta_object(self.app_name,
                                          self.service_name,
                                          name,
                                          self.methods[name])
            return method.Method(resrc, name, mObj)
