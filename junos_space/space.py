import requests
import json
import logging
import logging.config

from lxml import etree

my_space_url = "https://10.204.79.100"
my_space_user = "super"
my_space_passwd = "juniper123"

class Space:

    """Encapsulates a Space REST endpoint"""
    def __init__(self, url=my_space_url, user=my_space_user, passwd=my_space_passwd):
        self.space_url = url
        self.space_user = user
        self.space_passwd = passwd
        self.logger = logging.getLogger('root')
        self.services = self._init_services()

    def _init_services(self):
        class_def = self._get_class_def('tag_management.tags.TagManager')
        return {'tag_management': class_def(self) }

    def _get_class_def(self, class_name):
        parts = class_name.split('.')
        module = ".".join(parts[:-1])
        m = __import__( module, globals=globals())
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    def __getattr__(self, attr):
        return self.services[attr]

    def get(self, get_url, headers={}):
        req_url = self.space_url + get_url
        self.logger.debug("GET %s" % req_url)
        self.logger.debug(headers)
        r = requests.get(req_url, auth=(self.space_user, self.space_passwd), headers=headers, verify=False)
        self.logger.debug(r)
        return r

    def post(self, post_url, headers, body):
        req_url = self.space_url + post_url
        self.logger.debug("POST %s" % req_url)
        self.logger.debug(headers)
        self.logger.debug(body)
        r = requests.post(req_url, auth=(self.space_user, self.space_passwd), data=body, headers=headers, verify=False)
        self.logger.debug(r)
        self.logger.debug(r.text)
        return r

    def put(self, put_url, headers, body):
        req_url = self.space_url + put_url
        self.logger.debug("PUT %s" % req_url)
        self.logger.debug(headers)
        self.logger.debug(body)
        r = requests.put(req_url, auth=(self.space_user, self.space_passwd), data=body, headers=headers, verify=False)
        self.logger.debug(r)
        self.logger.debug(r.text)
        return r

    def delete(self, delete_url):
        req_url = self.space_url + delete_url
        self.logger.debug("DELETE %s" % req_url)
        r = requests.delete(req_url, auth=(self.space_user, self.space_passwd), verify=False)
        return r


class Resource(object):
    """Encapsulates a Space Resource"""

    def __init__(self, rest_end_point, xml_rep, attrs_dict):
        self._rest_end_point = rest_end_point
        self._data = xml_rep
        self._attrs_dict = attrs_dict

    def __getattr__(self, attr):
        el = self._data.find(attr)
        if (el != None):
            return el.text
        else:
            raise Exception('No field named %s!' % attr)

    def get(self):
        response = self._rest_end_point.get(self.get_href())
        if (response.status_code != 200):
            raise Exception(response.text)

        return response.text

    def put(self, new_val_obj):
        x = new_val_obj.form_xml()
        response = self._rest_end_point.put(
                            self.get_href(),
                            {'content-type': self._media_type},
                            etree.tostring(x)
                        )
        if (response.status_code != 200):
            raise Exception(response.text)

        r = response.text
        # Skip the <?xml> line to avoid encoding errors in lxml
        start = r.index('?><') + 2
        root = etree.fromstring(r[start:])
        self._data = root

    def delete(self):
        response = self._rest_end_point.delete(self.get_href())
        if (response.status_code != 204):
            raise Exception(response.text)

    def get_href(self):
        href = self._data.get('href')
        if (href != None):
            return href
        else:
            return self._service_url + "/" + self._collection_name + "/" + str(self.id)

    def form_xml(self):
        if (self._data != None):
            return self._data
        elif (self._attrs_dict != None):
            e = etree.Element(self._xml_name)
            for key, value in self._attrs_dict.iteritems():
                etree.SubElement(e, key).text = str(value)

            return e

    def __str__(self):
        return etree.tostring(self._data)


class Collection(object):
    """Encapsulates a collection of Space Resources"""

    def __init__(self, rest_end_point, name, href):
        self._rest_end_point = rest_end_point
        self._name = name
        self._href = href

    def get(self, filter=None):
        url = self._href
        if (filter != None):
            url = url + self._stringify_filter(filter)

        resource_list = []
        response = self._rest_end_point.get(url)
        if (response.status_code != 200):
            raise Exception(response.text)

        r = response.text
        # Skip the <?xml> line to avoid encoding errors in lxml
        start = r.index('?><') + 2
        root = etree.fromstring(r[start:])

        for child in root:
            resource_list.append(self._create_resource(child))

        return resource_list

    def post(self, new_obj):
        x = new_obj.form_xml()
        response = self._rest_end_point.post(self._href, {'content-type': new_obj._media_type}, etree.tostring(x))
        if ((response.status_code != 202) and (response.status_code != 200)):
            raise Exception(response.text)

        r = response.text
        # Skip the <?xml> line to avoid encoding errors in lxml
        start = r.index('?><') + 2
        root = etree.fromstring(r[start:])
        new_obj._data = root
        new_obj._rest_end_point = self._rest_end_point
        return new_obj


    def _stringify_filter(self, filter):
        if isinstance(filter, basestring):
            return '?filter=(' + filter + ')'


class Service(object):
    """Encapsulates a Space Service"""

    def __init__(self, rest_end_point):
        self._rest_end_point = rest_end_point
        self._collections = {}
        self._methods = {}

    def __getattr__(self, attr):
        if (attr in self._collections):
            return self._collections[attr]
        elif (attr in self._methods):
            return self._methods[attr]
        else:
            raise AttributeError


