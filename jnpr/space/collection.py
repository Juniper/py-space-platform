"""
This module defines the Collection class.
"""
from __future__ import unicode_literals
from __future__ import print_function
from builtins import str
from builtins import object
from lxml import etree

from jnpr.space import base, xmlutil, rest

class Collection(base._SpaceBase):
    """
    Represents a **collection** that is exposed by Junos Space REST API.
    Some examples of collections are:

    * The devices collection (``/api/space/device-management/devices``)
    * The users collection (``/api/space/user-management/users``)
    * The tags collection (``/api/space/tag-management/tags``)

    """

    def __init__(self, parent, name, meta_object):
        """Initializes a Collection object.

        :param parent: The parent object of this collection. This defaults to
            ``None``.
        :type parent: jnpr.space.service.Service or jnpr.space.resource.Resource

        :param str name: Name of this collection.

        :param meta_object: Meta object for this collection.
        :type meta_object: jnpr.space.collection.MetaCollection.

        """
        self._parent = parent
        self._rest_end_point = parent._rest_end_point
        self._name = name
        self._meta_object = meta_object
        self._methods = {}

    def get_href(self):
        """
        Gets the href for this collection. If the meta object has a ``url``
        set, it is returned. Otherwise, it concatenates the href of the parent
        object and the name of this collection to form the href and returns it.

        :returns: The href of this collection.

        """
        if self._meta_object.url:
            return self._meta_object.url
        else:
            return self._parent.get_href() + "/" + xmlutil.make_xml_name(self._name)

    def __getattr__(self, attr):
        """
        This method is overridden in the class so that named members and
        methods contained by this collection can be accessed as *normal* Python
        attributes of this object.

        :param str attr: Name of the attribute being accessed.

        :returns: Contained Resource (named member) or Method.
        """
        if attr in self._meta_object.named_members:
            resource = self._create_named_resource(attr,
                                                   self._meta_object.named_members[attr],
                                                   None)
            resource.id = attr
            return resource

        if attr in self._methods:
            return self._methods[attr]

        method = self._meta_object.create_method(self, attr)
        if method is not None:
            self._methods[attr] = method
            return method

    def __getitem__(self, attr):
        """
        This method is overridden so that contained elements can be accessed
        using their 'xml names' - e.g. user['first-name']. The implementation
        just calls __getattr__ internally.

        See doc for __getattr__ for more details.
        """

        return self.__getattr__(xmlutil.unmake_xml_name(attr))

    def get(self, accept=None, filter_=None,
            domain_id=None, paging=None, sortby=None):
        """Gets the contained resources of this collection from Space.

        :param str accept: This can be used to supply a media-type that must
            be used as the Accept header in the GET request. This defaults to
            ``None`` and in this case SpaceEZ will use the media-type modeled
            in the description file.

        :param filter_: A filter expression to apply on the collection. This
            can be given as a dict with name:value pairs to filter with. For
            example, ``{'name':'user1'}``. Or this can be given as a string
            which forms a valid filter expression for this collection as per
            Junos Space API documentation.
            This parameter defaults to ``None``.
        :type filter_: str or dict

        :param paging: A paging expression to apply on the collection. This
            must be given as a dict with entries giving values for ``start``
            and ``limit`` paging parameters. For example, ``{'start':10,
            'limit':100}``.
            This parameter defaults to ``None``.
        :type paging: dict

        :param sortby: A list of field names to sort the results by.
            This parameter defaults to ``None``.
        :type sortby: list of str

        :returns: A list of ``jnpr.space.resource.Resource`` objects.

        :raises: ``jnpr.space.rest.RestException`` if the GET method results in an
            error response. The exception's ``response`` attribute will have the
            full response from Space.

        """
        url = self._form_get_url(filter_, domain_id, paging, sortby)

        if accept is not None:
            mtype = accept
        else:
            mtype = self._meta_object.get_media_type(None)

        if mtype is not None:
            if not self._meta_object.retain_charset_in_accept:
                end = mtype.find(';charset=')
                if end > 0:
                    mtype = mtype[0:end]
            headers = {'accept' : mtype}
        else:
            headers = {}

        resource_list = []
        response = self._rest_end_point.get(url, headers)
        if response.status_code != 200:
            if response.status_code == 204:
                return []
            raise rest.RestException("GET failed on %s" % url, response)

        # Fixing issue #17
        #r = response.text
        # Skip the <?xml> line to avoid encoding errors in lxml
        #start = r.index('?><') + 2
        #root = etree.fromstring(r[start:])

        root = etree.fromstring(response.content)

        if self._meta_object.single_object_collection:
            resource_list.append(self._create_resource(root))
        elif self._meta_object.named_members:
            for key, value in self._meta_object.named_members.items():
                resrc = self._create_named_resource(key, value, root)
                resrc.id = key
                resource_list.append(resrc)
        else:
            for child in root:
                try:
                    resrc = self._create_resource(child)
                    resource_list.append(resrc)
                except Exception as ex:
                    if ex.ignore:
                        pass
                    else:
                        raise ex

        return ResourceList(resource_list)

    def _create_named_resource(self, key, meta_object, xml_root):
        """
        Helper method to create a named resource under this collection.
        """
        type_name = meta_object['resource_type']
        xml_data = xml_root.find(meta_object['xml_name']) \
            if xml_root is not None else None
        from jnpr.space.resource import Resource
        resrc = Resource(type_name=type_name,
                         rest_end_point=self._rest_end_point,
                         xml_data=xml_data,
                         parent=self)
        resrc.id = key
        return resrc

    def _create_resource(self, xml_data):
        """
        Helper method to create a resource under this collection. This is used
        to populate entries in the list returned by the get() method of this
        collection.
        """
        if self._meta_object.resource_type:
            from jnpr.space import resource
            return resource.Resource(type_name=self._meta_object.resource_type,
                                     rest_end_point=self._rest_end_point,
                                     xml_data=xml_data,
                                     parent=self)
        else:
            xml_str = etree.tostring(xml_data)
            return xmlutil.xml2obj(xml_str)

    def post(self, new_obj=None, accept=None, content_type=None,
             request_body=None, xml_name=None, task_monitor=None):
        """
        Sends a POST request to the Space server to create a new Resource in
        this collection.

        :param new_obj: The new Resource that needs to be created as a member
            of this collection. This can be omitted in which case the caller
            must supply a request body for the POST request as the
            ``request_body`` argument.
        :type new_obj: A single ``jnpr.space.resource.Resource`` instance
            or a list of them.

        :param str accept: This can be used to supply a media-type that must
            be used as the Accept header in the request. This defaults to
            ``None`` and in this case SpaceEZ will use the media-type modeled
            in the description file.

        :param str content_type: This can be used to supply a media-type that must
            be used as the Content-Type header in the request. This defaults to
            ``None`` and in this case SpaceEZ will use the media-type modeled
            in the description file.

        :param str request_body: This can be used to supply a string that must
            be used as the request body in the request. This defaults to
            ``None`` and in this case the caller must supply the ``new_obj``
            argument from which the request body will be formed.

        :param str xml_name: Can be used to override the name of the top-level
            XML element in the generated request body. This is useful in some
            cases such as creating a quick config template.
            This parameter defaults to ``None``.

        :param task_monitor: A TaskMonitor object that can be used to monitor
            the progress of the POST request, in case of asynchronous
            invocations. You need to check Junos Space API documentation to
            see if the POST invocation on this resource has asynchronous
            semantics and supply the task_monitor parameter only if it is
            asynchronous. Otherwise, this will default to ``None`` and the
            method will behave with synchronous semantics.
        :type task_monitor: jnpr.space.async.TaskMonitor

        :returns: If the new_obj parameter is a list, then the same list is
            returned. Otherwise, this method creates a new Resource object
            based on the state of the newly created resource, as extracted from
            the POST response body. In the case of asynchronous
            invocation, this will represent a Task object and will contain the
            unique id of the Task executing the POST request in Space.

        :raises: ``jnpr.space.rest.RestException`` if the POST method results in
            an error response. The exception's ``response`` attribute will have
            the full response from Space.

        """
        if content_type is not None:
            media_type = content_type
        elif isinstance(new_obj, list):
            if self._meta_object.content_type is not None:
                media_type = self._meta_object.content_type
            else:
                media_type = self._meta_object.get_media_type(None)
        else:
            if new_obj is None:
                raise ValueError('Must provide content_type when providing request_body')
            media_type = new_obj.get_meta_object().get_media_type(None)

        headers = {'content-type': media_type}
        if accept:
            headers['accept'] = accept

        if request_body is not None:
            body = request_body
            saved_root_tag = None
            if new_obj is not None:
                raise ValueError('Cannot use both request_body and new_obj!')
        else:
            if new_obj is None:
                raise ValueError('Cannot omit both request_body and new_obj!')

            xml_obj = None
            if isinstance(new_obj, list):
                xml_obj = etree.Element(self._meta_object.xml_name)
                for obj in new_obj:
                    xml_obj.append(obj.form_xml())
            else:
                xml_obj = new_obj.form_xml()

            saved_root_tag = xml_obj.tag

            if xml_name:
                xml_obj.tag = xml_name

            body = xmlutil.cleanup(etree.tostring(xml_obj))

        url = self.get_href()
        if task_monitor:
            url = '?queue='.join([url, task_monitor.get_queue_url()])

        response = self._rest_end_point.post(url,
                                             headers,
                                             body)

        if response.status_code == 204: # Special case of post with null response
            return new_obj

        if response.status_code not in [200, 202]:
            raise rest.RestException("POST failed on %s" % self.get_href(),
                                     response)

        if task_monitor is not None:
            resp_str = response.content
            return xmlutil.xml2obj(resp_str)

        if not isinstance(new_obj, list):
            # Fixing issue #17
            #r = response.text
            # Skip the <?xml> line to avoid encoding errors in lxml
            #start = r.index('?><') + 2
            #root = etree.fromstring(r[start:])
            root = etree.fromstring(response.content)
            #new_obj._xml_data = root
            #new_obj._rest_end_point = self._rest_end_point
            if saved_root_tag is not None:
                root.tag = saved_root_tag
            new_obj = self._create_resource(root)

        return new_obj

    def _form_get_url(self, filter_, domain_id, paging, sortby):
        """
        Helper method to form the URL for a GET on this collection including
        filtering, paging, and sortby clauses.
        """
        url = self.get_href()

        fltr, dmn, pgng, srtby = None, None, None, None
        if filter_ is not None:
            fltr = self._stringify_filter(filter_)
        if domain_id is not None:
            dmn = "domainContext=(filterDomainIds eq %d)" % domain_id
        if paging is not None:
            pgng = self._stringify_paging(paging)
        if sortby is not None:
            srtby = self._stringify_sortby(sortby)

        if dmn is not None:
            url = '?'.join([url, dmn])
            if fltr is not None:
                url = '&'.join([url, fltr])
            if pgng is not None:
                url = '&'.join([url, pgng])
            if srtby is not None:
                url = '&'.join([url, srtby])
        elif fltr is not None:
            url = '?'.join([url, fltr])
            if pgng is not None:
                url = '&'.join([url, pgng])
            if srtby is not None:
                url = '&'.join([url, srtby])
        elif pgng is not None:
            url = '?'.join([url, pgng])
            if srtby is not None:
                url = '&'.join([url, srtby])
        elif srtby is not None:
            url = '?'.join([url, srtby])

        return url

    def _stringify_filter(self, filter_):
        """
        Helper method to stringify the given filter_ parameter and form a
        proper filter clause for the GET URL.
        """
        if isinstance(filter_, str):
            return ''.join(['filter=(', filter_, ')'])

        if isinstance(filter_, dict):
            filter_list = ['filter=(']
            index = 1
            for key, value in filter_.items():
                if index < len(filter_):
                    filter_list.extend(["(", key, " eq '", str(value), "') and "])
                else:
                    filter_list.extend(["(", key, " eq '", str(value), "')"])
                index += 1
            filter_list.append(')')
            return ''.join(filter_list)

    def _stringify_paging(self, paging):
        """
        Helper method to stringify the given paging parameters and form a
        proper paging clause for the GET URL.
        """
        start, limit = None, None
        if 'start' in paging:
            start = 'start eq %d' % paging['start']
        if 'limit' in paging:
            limit = 'limit eq %d' % paging['limit']

        if start and limit:
            pg_str = 'paging=(%s, %s)' % (start, limit)
        elif start:
            pg_str = 'paging=(%s)' % (start)
        elif limit:
            pg_str = 'paging=(%s)' % (limit)

        return pg_str

    def _stringify_sortby(self, field_list):
        """
        Helper method to stringify the given sortby parameters and form a
        proper sortby clause for the GET URL.
        """
        return 'sortby=(%s)' % ','.join(field_list)

    def state(self):
        """
        Performs a GET on this collection to fetch the current state and
        prints it as XML.
        """
        coll_state = self.get()
        print(coll_state.xml_string())

class ResourceList(list):
    """
    Encapsulates a list of Resource objects and provides
    methods to print the state of all of them.
    """
    def __init__(self, resource_list):
        self.resources = resource_list
        super(ResourceList, self).__init__(resource_list)

    def xml_data(self):
        """
        Returns a formatted string that represents the state of all resources
        in this list.
        """
        val = []
        for resrc in self.resources:
            val.append(resrc.xml_data())
        return '\n\n'.join(val)

    def xml_string(self):
        """
        Returns a string that contains formatted XML representing the
        state of all resources in this list.
        """
        val = []
        for resrc in self.resources:
            val.append(resrc.xml_string())
        return '\n\n'.join(val)

    def state(self):
        """
        Prints the XML string into stdout.
        """
        print(self.xml_string())

class MetaCollection(object):
    """ Encapsulates the meta data for a collection type.
    """

    def __init__(self, app_name, service_name, key, values):
        """Initializes a MetaCollection object.

        :param str app_name: Name of the application.
        :param str service_name: Name of the service.
        :param str key: Name of the collection.
        :param dict values:  Attribute value settings which form the meta data
            for this collection. This is read from the descriptions yml file for
            the corresponding service.
        """
        self.values = values
        self.app_name = app_name
        self.service_name = service_name
        self.key = key
        self.name = values['name'] \
            if ('name' in values) else None
        self.single_object_collection = values['single_object_collection'] \
            if ('single_object_collection' in values) else False
        self.xml_name = values['xml_name'] \
            if ('xml_name' in values) else None
        self.media_type = values['media_type'] \
            if ('media_type' in values) else None
        self.retain_charset_in_accept = values['retain_charset_in_accept'] \
            if ('retain_charset_in_accept' in values) else False
        self.content_type = values['content_type'] \
            if ('content_type' in values) else None
        self.resource_type = values['resource_type'] \
            if ('resource_type' in values) else None
        self.url = values['url'] \
            if ('url' in values) else None
        self.named_members = values['named_members'] \
            if ('named_members' in values) else {}
        self.methods = values['methods'] \
            if ('methods' in values) else {}

    def get_media_type(self, version):
        """Returns the media-type defined inside the meta object.
        """
        if isinstance(self.media_type, dict):
            if version is not None:
                return self.media_type[str(version)]
            if len(self.media_type) == 1:
                return next(iter(self.media_type.values()))
            else:
                raise Exception("You must specify the required media-type version")
        elif version is None:
            return self.media_type

        raise Exception("Version %s not defined for '%s' in descriptions!" %
                        (str(version), self.key))

    def create_method(self, service, name):
        """Creates a method object corresponding to the given service and
        name.

        :param service: Parent service.
        :type service: jnpr.space.service.Service
        :param str name: Name of the method.

        :returns: A ``jnpr.space.method.Method`` object.

        """
        if name in self.methods:
            from jnpr.space import method
            m_obj = method.get_meta_object(self.app_name,
                                           service._name,
                                           name,
                                           self.methods[name])
            return method.Method(service, name, m_obj)

#
# A dictionary that acts as a cache for meta objects representing collections.
# Keys are collection names. Values are instances of
# jnpr.space.collection.MetaCollection.
#
_meta_collections = {}

def get_meta_object(app_name, service_name, coll_name, values):
    """Looks up the meta object for a collection based on its fully qualified
    type name of the form ``<service-name>.<coll_name>`` or
    ``<app-name>.<service-name>.<coll-name>``.

    :param str app_name: Name of the application.
    :param str service_name: Name of the service.
    :param str coll_name: Name of the collection.

    :returns: A ``jnpr.space.collection.MetaCollection`` object.

    """
    if app_name:
        fullname = '.'.join([app_name, service_name, coll_name])
    else:
        fullname = '.'.join([service_name, coll_name])

    if fullname in _meta_collections:
        return _meta_collections[fullname]

    meta_coll = MetaCollection(app_name, service_name, coll_name, values)
    _meta_collections[fullname] = meta_coll
    return meta_coll
