"""
A module with utility functions for XML handling.
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from lxml import objectify, etree

def make_xml_name(attr_name):
    """ Convert an attribute name to its XML equivalent by replacing
    all '_' with '-'. CamelCase names are retained as such.

    :param str attr_name: Name of the attribute

    :returns: Attribute name in XML format.
    """
    return attr_name.replace('_', '-')

def unmake_xml_name(attr_name):
    """ Convert an XML attribute name to its pythonic equivalent by replacing
    all '-' with '_'. CamelCase names are retained as such.

    :param str attr_name: Name of the attribute

    :returns: Attribute name in pythonic format.
    """
    return attr_name.replace('-', '_')

def get_text_from_response(response):
    """
    Returns text from ``Response`` object that will be str (unicode) in
    both python 2 and 3.
    """
    return response.text

def get_xml_obj_from_response(response):
    """
    Returns an XML object (``lxml.Element``) from the text inside the
    ``Response`` object.
    """
    src = get_text_from_response(response)
    start = src.find('?>')
    if start > 0:
        start += 2
    else:
        start = 0
    return etree.fromstring(src[start:])

def cleanup(src):
    """
    Some responses from Space contains escaped form for XML special characters.
    E.g. '&lt;' for '<', etc. This method removes these escaped notations.

    :param str src: Source string

    :returns: String with escaped notations replaced.
    """
    xml = src.replace('&lt;', '<').replace('&gt;', '>')
    xml = xml.replace('&quot;', '"')
    return xml

def xml2obj(src):
    """
    Uses lxml.objectify to parse the given XML string and returns a Python
    object.

    :param str src: Source XML string

    :returns: An instance of ```lxml.objectify.ObjectifiedElement```
    """
    start = src.find('?>')
    if start > 0:
        start += 2
    else:
        start = 0
    return objectify.fromstring(src[start:])

if __name__ == '__main__':
    print('Hello')
    sample = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><netconf><status>Success</status><rpcCommands><rpcCommand>&lt;get-system-information/&gt;</rpcCommand></rpcCommands><netConfReplies><netConfReply><status>Success</status><replyMsgData>&lt;system-information  xmlns:junos=&quot;http://xml.jnpr.net/junos/13.1X49/junos&quot;&gt;
&lt;hardware-model&gt;mx240&lt;/hardware-model&gt;
&lt;os-name&gt;junos&lt;/os-name&gt;
&lt;os-version&gt;13.1X49-D34.4&lt;/os-version&gt;
&lt;serial-number&gt;JN1165A9EAFC&lt;/serial-number&gt;
&lt;host-name&gt;jtme-mx240-03&lt;/host-name&gt;
&lt;/system-information&gt;
</replyMsgData></netConfReply></netConfReplies><deviceFamily>junos</deviceFamily><isCluster>false</isCluster><enableDiscardChanges>false</enableDiscardChanges><netconfConfirmedCommit>false</netconfConfirmedCommit></netconf>
"""
    sample = sample.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    print(sample)
    r = xml2obj(sample)
    print(r.status)
    from pprint import pprint
    pprint(r)
    pprint(r.netConfReplies.netConfReply.replyMsgData)

    print("New")

    for i in r._attrs:
        pprint(i)
