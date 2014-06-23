'''
Created on 23-Jun-2014

@author: rjoyce
'''

from lxml import etree

class Collection(object):
    """Encapsulates a collection of Space Resources"""

    def __init__(self, rest_end_point, name, href, parent):
        self._rest_end_point = rest_end_point
        self._name = name
        self._href = href
        self._parent = parent

    def get_href(self):
        if self._href is not None:
            return self._href
        else:
            return self._parent.get_href() + "/" + self._name

    def get(self, filter_=None):
        url = self.get_href()
        if filter_ is not None:
            url = url + self._stringify_filter(filter_)

        resource_list = []
        response = self._rest_end_point.get(url)
        if response.status_code != 200:
            raise Exception(response.text)

        r = response.text
        # Skip the <?xml> line to avoid encoding errors in lxml
        start = r.index('?><') + 2
        root = etree.fromstring(r[start:])

        for child in root:
            resource_list.append(self._create_resource(child))

        return resource_list

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
            new_obj._data = root
            new_obj._rest_end_point = self._rest_end_point

        return new_obj


    def _stringify_filter(self, filter_):
        if isinstance(filter_, basestring):
            return '?filter=(' + filter_ + ')'

        if isinstance(filter_, dict):
            filter_str = '?filter=('
            index = 1
            for key, value in filter_.iteritems():
                cond = "(" + key + " eq '" + str(value) + "')"
                if (index < len(filter_)):
                    filter_str += cond + ' and '
                else:
                    filter_str += cond
                index += 1
            filter_str += ')'
            return filter_str