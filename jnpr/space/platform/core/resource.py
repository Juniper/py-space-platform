'''
Created on 23-Jun-2014

@author: rjoyce
'''

from pprint import pformat
from lxml import etree


class Resource(object):
    """Encapsulates a Space Resource"""

    def __init__(self, type_, rest_end_point, xml_data=None, attrs_dict=None):
        self._type = type_
        self._rest_end_point = rest_end_point
        self._xml_data = xml_data
        self._attrs_dict = attrs_dict
        self._collections = {}
        self._methods = {}
        self._init_meta_data(rest_end_point, type_)

    def _init_meta_data(self, rest_end_point, type_):
        parts = type_.split('.')
        service_name = parts[0]
        service = rest_end_point.__getattr__(service_name)
        resource_type = parts[1]
        m = service.get_meta_resource(resource_type)
        self._xml_name = m['xml_name']
        self._media_type = m['media_type']
        self._collection_name = m['collection_name']
        self._service_url = m['service_url']
        if 'use_uri_for_delete' in m:
            self._use_uri_for_delete = m['use_uri_for_delete']
        else:
            self._use_uri_for_delete = False
        from jnpr.space.platform.core.collection import Collection
        try:
            for key in m['collections']:
                value = m['collections'][key]
                self._collections[key] = Collection(self,
                                                    key,
                                                    value)
        except KeyError:
            pass

    def __getattr__(self, attr):
        if attr in self._collections:
            return self._collections[attr]
        elif attr in self._methods:
            return self._methods[attr]

        # Check if it is an element in xml data
        el = self._xml_data.find(attr)
        if el is not None:
            return el.text

        # Check if it is an attribute in xml data
        val = self._xml_data.get(attr)
        if val is not None:
            return val
        else:
            raise Exception('No field named %s!' % attr)

    def get(self):
        response = self._rest_end_point.get(self.get_href())
        if response.status_code != 200:
            raise Exception(response.text)

        r = response.text
        # Skip the <?xml> line to avoid encoding errors in lxml
        start = r.index('?><') + 2
        xml_data = etree.fromstring(r[start:])

        return self.__class__(self._type, self._rest_end_point, xml_data)

    def put(self, new_val_obj = None):
        if new_val_obj is not None:
            x = new_val_obj.form_xml()
        else:
            x = self.form_xml()

        response = self._rest_end_point.put(
                            self.get_href(),
                            {'content-type': self._media_type},
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
        if self._use_uri_for_delete:
            url = self.uri
        else:
            url = self.get_href()
        response = self._rest_end_point.delete(url)
        if response.status_code != 204:
            raise Exception(response.text)

    def get_href(self):
        href = self._xml_data.get('href')
        if href is not None:
            return href
        else:
            return self._service_url + "/" + self._collection_name + "/" + str(self.id)

    def form_xml(self):
        e = etree.Element(self._xml_name)
        attributes = {}
        if self._attrs_dict is not None:
            attributes = self._attrs_dict
        else:
            attributes = self.__dict__

        for key, value in attributes.iteritems():
            if key.startswith('_'):
                continue

            if key == 'href':
                e.attrib[key] = str(value)
            else:
                etree.SubElement(e, key).text = str(value)

        return e

    def __str__(self):
        if self._xml_data is not None:
            return etree.tostring(self._xml_data)
        return pformat(self, depth=6)