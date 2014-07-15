'''
Created on 23-Jun-2014

@author: rjoyce
'''

from pprint import pformat
from lxml import etree
from jinja2 import Environment, PackageLoader

from jnpr.space.platform.core import util, xmlutil

class Resource(object):
    """Encapsulates a Space Resource"""

    def __init__(self, type_name, rest_end_point,
                 xml_data=None, attributes=None, parent=None):
        self._type_name = type_name
        self._rest_end_point = rest_end_point
        self._xml_data = xml_data
        self._attributes = attributes
        self._parent = parent
        self._collections = {}
        self._methods = {}
        self._init_meta_data(rest_end_point, type_name)
        if xml_data is not None:
            if self.meta_object.xml_name != xml_data.tag:
                e = Exception('Invalid xml object for this resource!')
                e.ignore = True
                raise e

    def _init_meta_data(self, rest_end_point, type_name):
        parts = type_name.split('.')
        if len(parts) != 2:
            raise Exception("Invalid resource type given: '%s'" % type_name)

        service_name = parts[0]
        try:
            service = rest_end_point.__getattr__(service_name)
        except AttributeError:
            raise Exception("Unknown service name in '%s'" % type_name)

        resource_type = parts[1]
        try:
            values = service.get_meta_resource(resource_type)
            self.meta_object = get_meta_object(type_name, resource_type, values)
        except KeyError:
            raise Exception("Unknown resource type in '%s'" % type_name)

    def __getattr__(self, attr):
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

    def get(self):
        response = self._rest_end_point.get(self.get_href())
        if response.status_code != 200:
            raise Exception(response.text)

        r = response.text
        return xmlutil.xml2obj(r)
        # Skip the <?xml> line to avoid encoding errors in lxml
        #start = r.index('?><') + 2
        #xml_data = etree.fromstring(r[start:])

        #return self.__class__(self._type_name, self._rest_end_point, xml_data)

    def put(self, new_val_obj = None):
        if new_val_obj is not None:
            x = new_val_obj.form_xml()
        else:
            x = self.form_xml()

        response = self._rest_end_point.put(
                            self.get_href(),
                            {'content-type': self.meta_object.media_type},
                            etree.tostring(x)
                        )
        if response.status_code != 200:
            raise Exception(response.text)

        r = response.text
        # Skip the <?xml> line to avoid encoding errors in lxml
        start = r.index('?><') + 2
        root = etree.fromstring(r[start:])
        self._xml_data = root

    def delete(self):
        if self.meta_object.use_uri_for_delete:
            url = self.uri
        else:
            url = self.get_href()
        response = self._rest_end_point.delete(url)
        if response.status_code != 204:
            raise Exception(response.text)

    def post(self, task_monitor=None, schedule=None, *args, **kwargs):
        url = self.get_href()
        if task_monitor:
            url = '?queue='.join([url, task_monitor.get_queue_url()])
            if schedule:
                url = '&schedule='.join([url, schedule])

        headers = {}
        if self.meta_object.response_type:
            headers['accept'] = self.meta_object.response_type

        if self.meta_object.request_template:
            body = self.meta_object.request_template.render(**kwargs)
            headers['content-type'] = self.meta_object.request_type
        else:
            body = None

        response = self._rest_end_point.post(url,headers,body)
        if (response.status_code != 202) and (response.status_code != 200):
            raise Exception(response.text)

        return xmlutil.xml2obj(xmlutil.cleanup(response.text))

    def get_href(self):
        if self._xml_data is not None:
            h = self._xml_data.get('href')
            if h:
                return h

        if self._parent:
            return '/'.join([self._parent.get_href(), str(self.id)])

        if self._xml_data is not None:
            h = self._xml_data.get('uri')
            # Working around problems in Space API.
            # E.g. equipment-holder does not have href, but only uri
            if h and not h.endswith(self.meta_object.collection_name):
                # Working around problems in Space API.
                # E.g. A newly created tag returns uri (but no href) in the
                # POST response. But the uri does not end with the id
                # of the tag!
                return h

        return self.meta_object.service_url + "/" + self.meta_object.collection_name + "/" + str(self.id)

    def form_xml(self):
        e = etree.Element(self.meta_object.xml_name)
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
            else:
                etree.SubElement(e, xml_name).text = str(value)

        return e

    def __str__(self):
        if self._xml_data is not None:
            return etree.tostring(self._xml_data)
        return pformat(self, depth=6)

_meta_resources = {}

def get_meta_object(full_name, type_name, values):
    if full_name in _meta_resources:
        return _meta_resources[full_name]

    m = MetaResource(type_name, values)
    _meta_resources[full_name] = m
    return m

class MetaResource(object):

    def __init__(self, key, values):
        self.key = key
        self.name = values['name'] \
            if ('name' in values) else None
        self.xml_name = values['xml_name'] \
            if ('xml_name' in values) else None
        self.media_type = values['media_type'] \
            if ('media_type' in values) else None
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
            env = Environment(loader=PackageLoader('jnpr.space.platform',
                                                   'templates'))
            self.request_template = env.get_template(values['request_template'])

        try:
            from jnpr.space.platform.core import collection
            for key in values['collections']:
                value = values['collections'][key]
                mObj = collection.get_meta_object(key, value)
                self.collections[key] = mObj
        except KeyError:
            pass

        try:
            from jnpr.space.platform.core import method
            for key in values['methods']:
                value = values['methods'][key]
                mObj = method.get_meta_object(key, value)
                self.methods[key] = mObj
        except KeyError:
            pass

    def create_collection(self, service, name):
        if name in self.collections:
            from jnpr.space.platform.core import collection
            return collection.Collection(service, name, self.collections[name])

    def create_method(self, service, name):
        if name in self.methods:
            from jnpr.space.platform.core import method
            mObj = method.get_meta_object(name, self.methods[name])
            return method.Method(service, name, mObj)
