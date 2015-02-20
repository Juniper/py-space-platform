from lxml import etree

from jnpr.space import util
from jnpr.space import rest

class Collection(object):
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
        self.meta_object = meta_object
        self._methods = {}

    def get_href(self):
        """
        Gets the href for this collection. If the meta object has a ``url``
        set, it is returned. Otherwise, it concatenates the href of the parent
        object and the name of this collection to form the href and returns it.

        :returns: The href of this collection.

        """
        if self.meta_object.url:
            return self.meta_object.url
        else:
            return self._parent.get_href() + "/" + util.make_xml_name(self._name)

    def __getattr__(self, attr):
        """
        This method is overridden in the class so that named members and
        methods contained by this collection can be accessed as *normal* Python
        attributes of this object.

        :param str attr: Name of the attribute being accessed.

        :returns: Contained Resource (named member) or Method.
        """
        if attr in self.meta_object.named_members:
            r = self._create_named_resource(attr,
                            self.meta_object.named_members[attr], None)
            r.id = attr
            return r

        if attr in self._methods:
            return self._methods[attr]

        method = self.meta_object.create_method(self, attr)
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

        from jnpr.space import xmlutil
        return self.__getattr__(xmlutil.unmake_xml_name(attr))

    def get(self, version=None, filter_=None, domain_id=None, paging=None, sortby=None):
        """Gets the contained resources of this collection from Space.

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

        mtype = self.meta_object.get_media_type(version)
        if mtype is not None:
            if not self.meta_object.retain_charset_in_accept:
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

        if self.meta_object.single_object_collection:
            resource_list.append(self._create_resource(root))
        elif self.meta_object.named_members:
            for key, value in self.meta_object.named_members.iteritems():
                r = self._create_named_resource(key, value,root)
                r.id = key
                resource_list.append(r)
        else:
            for child in root:
                try:
                    r = self._create_resource(child)
                    resource_list.append(r)
                except Exception as e:
                    if e.ignore:
                        pass
                    else:
                        raise e

        return ResourceList(resource_list)

    def _create_named_resource(self, key, meta_object, xml_root):
        """
        Helper method to create a named resource under this collection.
        """
        type_name = meta_object['resource_type']
        xml_data = xml_root.find(meta_object['xml_name']) \
            if xml_root is not None else None
        from jnpr.space.resource import Resource
        return Resource(type_name=type_name,
                        rest_end_point=self._rest_end_point,
                        xml_data=xml_data,
                        parent=self)

    def _create_resource(self, xml_data):
        """
        Helper method to create a resource under this collection. This is used
        to populate entries in the list returned by the get() method of this
        collection.
        """
        if self.meta_object.resource_type:
            from jnpr.space import resource
            return resource.Resource(type_name=self.meta_object.resource_type,
                                 rest_end_point=self._rest_end_point,
                                 xml_data=xml_data, parent=self)
        else:
            from jnpr.space import xmlutil
            s = etree.tostring(xml_data)
            return xmlutil.xml2obj(s)

    def post(self, new_obj, version=None, xml_name=None, content_type=None, accept=None):
        """
        Sends a POST request to the Space server to create a new Resource in
        this collection.

        :param new_obj: The new Resource that needs to be created as a member
            of this collection.
        :type new_obj: A single ``jnpr.space.resource.Resource`` instance
            or a list of them.

        :param str xml_name: Can be used to override the name of the top-level
            XML element in the generated request body. This is useful in some
            cases such as creating a quick config template.
            This parameter defaults to ``None``.

        :param str content_type: Can be used to override the *content-type*
            header of the POST request. This is useful in some
            cases such as creating a quick config template.
            This parameter defaults to ``None``.

        :param str accept: Can be used to override the *accept*
            header of the POST request. This is useful in some
            cases such as creating a quick config template.
            This parameter defaults to ``None``.

        :returns: If the new_obj parameter is a list, then the same list is
            returned. Otherwise, this method creates a new Resource object
            based on the state of the newly created resource, as extracted from
            the POST response body.

        :raises: ``jnpr.space.rest.RestException`` if the POST method results in
            an error response. The exception's ``response`` attribute will have
            the full response from Space.

        """
        if content_type:
            media_type = content_type
        elif isinstance(new_obj, list):
            if self.meta_object.content_type is not None:
                media_type = self.meta_object.content_type
            else:
                media_type = self.meta_object.get_media_type(version)
        else:
            media_type = new_obj.get_meta_object().get_media_type(version)

        headers = {'content-type': media_type}
        if accept:
            headers['accept'] = accept

        x = None
        if isinstance(new_obj, list):
            x = etree.Element(self._name)
            for o in new_obj:
                x.append(o.form_xml())
        else:
            x = new_obj.form_xml()

        saved_root_tag = x.tag

        if xml_name:
            x.tag = xml_name

        response = self._rest_end_point.post(self.get_href(),
                                             headers,
                                             etree.tostring(x))

        if response.status_code == 204: # Special case of post with null response
            return new_obj

        if response.status_code not in [200, 202]:
            raise rest.RestException("POST failed on %s" % self.get_href(),
                                     response)

        if not isinstance(new_obj, list):
            # Fixing issue #17
            #r = response.text
            # Skip the <?xml> line to avoid encoding errors in lxml
            #start = r.index('?><') + 2
            #root = etree.fromstring(r[start:])
            root = etree.fromstring(response.content)
            #new_obj._xml_data = root
            #new_obj._rest_end_point = self._rest_end_point
            root.tag = saved_root_tag
            new_obj = self._create_resource(root)

        return new_obj

    def _form_get_url(self, filter_, domain_id, paging, sortby):
        """
        Helper method to form the URL for a GET on this collection including
        filtering, paging, and sortby clauses.
        """
        url = self.get_href()

        f, d, p, s = None, None, None, None
        if filter_ is not None:
            f = self._stringify_filter(filter_)
        if domain_id is not None:
            d = "domainContext=(filterDomainIds eq %d)" % domain_id
        if paging is not None:
            p = self._stringify_paging(paging)
        if sortby is not None:
            s = self._stringify_sortby(sortby)

        if d is not None:
            url = '?'.join([url, d])
            if f is not None:
                url = '&'.join([url, f])
            if p is not None:
                url = '&'.join([url, p])
            if s is not None:
                url = '&'.join([url, s])
        elif f is not None:
            url = '?'.join([url, f])
            if p is not None:
                url = '&'.join([url, p])
            if s is not None:
                url = '&'.join([url, s])
        elif p is not None:
            url = '?'.join([url, p])
            if s is not None:
                url = '&'.join([url, s])
        elif s is not None:
                url = '?'.join([url, s])

        return url

    def _stringify_filter(self, filter_):
        """
        Helper method to stringify the given filter_ parameter and form a
        proper filter clause for the GET URL.
        """
        if isinstance(filter_, basestring):
            return ''.join(['filter=(', filter_, ')'])

        if isinstance(filter_, dict):
            filter_list = ['filter=(']
            index = 1
            for key, value in filter_.iteritems():
                if (index < len(filter_)):
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
            pg_str = 'paging=(%s, %s)' % (start,limit)
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
        for r in self.resources:
            val.append(r.xml_data())
        return '\n\n'.join(val)

    def xml_string(self):
        """
        Returns a string that contains formatted XML representing the
        state of all resources in this list.
        """
        val = []
        for r in self.resources:
            val.append(r.xml_string())
        return '\n\n'.join(val)

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
            mObj = method.get_meta_object(
                                          self.app_name,
                                          service._name,
                                          name,
                                          self.methods[name]
                                          )
            return method.Method(service, name, mObj)

"""
A dictionary that acts as a cache for meta objects representing collections.
Keys are collection names. Values are instances of
jnpr.space.collection.MetaCollection.
"""
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

    c = MetaCollection(app_name, service_name, coll_name, values)
    _meta_collections[fullname] = c
    return c