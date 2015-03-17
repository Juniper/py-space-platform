"""
Defines a few util functions.
"""

def get_class_def(class_name):
    """
    Returns the definition for the given class name.
    """
    parts = class_name.split('.')
    module = ".".join(parts[:-1])
    mdl = __import__(module, globals=globals())
    for comp in parts[1:]:
        mdl = getattr(mdl, comp)
    return mdl

def make_xml_name(attr_name):
    """
    Replaces _ with -
    """
    return attr_name.replace('_', '-')

def unmake_xml_name(attr_name):
    """
    Replaces - with _
    """
    return attr_name.replace('-', '_')
