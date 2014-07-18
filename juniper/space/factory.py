'''
Created on 16-Jul-2014

@author: rjoyce
'''

from juniper.space import resource

def make_resource(type_name, rest_end_point,
                 xml_data=None, attributes=None, parent=None):
    return resource.Resource(type_name,
                             rest_end_point,
                             xml_data,
                             attributes,
                             parent)