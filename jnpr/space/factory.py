'''
Created on 16-Jul-2014

@author: rjoyce
'''

from lxml import etree
from jnpr.space import rest, resource, util

def make_resource(type_name, rest_end_point,
                 xml_data=None, attributes=None, parent=None):
    return resource.Resource(type_name,
                             rest_end_point,
                             xml_data,
                             attributes,
                             parent)

def fetch_resource(rest_end_point, href):
    response = rest_end_point.get(href)
    if response.status_code != 200:
        raise rest.RestException("GET failed on %s" % href, response)

    media_type = response.headers['content-type']
    end = media_type.index('+')
    parts = media_type[:end].split('.')
    service_ = parts[len(parts)-2]
    type_ = parts[len(parts)-1]

    type_name = util.unmake_xml_name('.'.join([service_, type_]))
    xml_data = etree.fromstring(response.content)
    return make_resource(type_name, rest_end_point, xml_data)
