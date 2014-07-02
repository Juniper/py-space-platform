'''
Created on 23-Jun-2014

@author: rjoyce
'''

from lxml import etree

from jnpr.space.platform.core import util

class Collection(object):
    """Encapsulates a collection of Space Resources"""

    def __init__(self, parent, name, meta_object):
        self._parent = parent
        self._rest_end_point = parent._rest_end_point
        self._name = name
        self._meta_object = meta_object
        self._xml_name = meta_object['xml_name']
        self._media_type = meta_object['media_type']
        if 'resource_type' in meta_object:
            self._resource_type = meta_object['resource_type']
        else:
            self._resource_type = None
        if 'url' in meta_object:
            self._href = meta_object['url']

    def get_href(self):
        if hasattr(self, '_href') and self._href is not None:
            return self._href
        else:
            return self._parent.get_href() + "/" + util.make_xml_name(self._name)

    def get(self, filter_=None):
        url = self.get_href()
        if filter_ is not None:
            url = url + self._stringify_filter(filter_)

        resource_list = []
        response = self._rest_end_point.get(url)
        if response.status_code != 200:
            if response.status_code == 204:
                return []
            raise Exception(response.text)

        r = response.text
        # Skip the <?xml> line to avoid encoding errors in lxml
        start = r.index('?><') + 2
        root = etree.fromstring(r[start:])

        for child in root:
            resource_list.append(self._create_resource(child))

        return resource_list

    def _create_resource(self, xml_data):
        if self._resource_type:
            from jnpr.space.platform.core.resource import Resource
            return Resource(type_name=self._resource_type,
                                 rest_end_point=self._rest_end_point,
                                 xml_data=xml_data)
        else:
            from jnpr.space.platform.core import xmlutil
            s = etree.tostring(xml_data)
            return xmlutil.xml2obj(s)

    def post(self, new_obj):
        x = None
        if isinstance(new_obj, list):
            media_type = self._media_type
            x = etree.Element(self._name)
            for o in new_obj:
                x.append(o.form_xml())
        else:
            media_type = new_obj._media_type
            x = new_obj.form_xml()

        response = self._rest_end_point.post(self.get_href(),
                                             {'content-type': media_type},
                                             etree.tostring(x))
        if (response.status_code != 202) and (response.status_code != 200):
            raise Exception(response.text)

        if not isinstance(new_obj, list):
            r = response.text
            # Skip the <?xml> line to avoid encoding errors in lxml
            start = r.index('?><') + 2
            root = etree.fromstring(r[start:])
            new_obj._xml_data = root
            new_obj._rest_end_point = self._rest_end_point

        return new_obj


    def _stringify_filter(self, filter_):
        if isinstance(filter_, basestring):
            return ''.join(['?filter=(', filter_, ')'])

        if isinstance(filter_, dict):
            filter_list = ['?filter=(']
            index = 1
            for key, value in filter_.iteritems():
                if (index < len(filter_)):
                    filter_list.extend(["(", key, " eq '", str(value), "') and "])
                else:
                    filter_list.extend(["(", key, " eq '", str(value), "')"])
                index += 1
            filter_list.append(')')
            return ''.join(filter_list)