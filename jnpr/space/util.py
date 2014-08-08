'''
Created on 30-Jun-2014

@author: rjoyce
'''

def get_class_def(class_name):
    parts = class_name.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module, globals=globals())
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m

def make_xml_name(attr_name):
    return attr_name.replace('_', '-')

def unmake_xml_name(attr_name):
    return attr_name.replace('-', '_')