#
# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER
#
# Copyright (c) 2015 Juniper Networks, Inc.
# All rights reserved.
#
# Use is subject to license terms.
#
# Licensed under the Apache License, Version 2.0 (the ?License?); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
A module with utility functions for XML handling.
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from lxml import objectify, etree
import re

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

def remove_junos_group(src):
    """
    Remove XML attribute junos:group from the given string.

    :param str src: Source string

    :returns: String with junos:group occurrences removed.
    """
    return re.sub(r' junos:group=".+"', '', src)

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
