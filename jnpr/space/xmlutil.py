"""
A module with utility functions for XML handling.

"""
from lxml import objectify

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
    return objectify.fromstring(src)

def info(obj):
    url = '/api/info?uri=' + obj.get_href()
    response = obj._rest_end_point.get(url)
    if response.status_code != 200:
        import rest
        raise rest.RestException("GET failed on %s" % url, response)

    obj = xml2obj(response.content)
    info = {}
    methods = {}
    info['methods'] = methods
    for m in obj['http-methods']['http-method']:
        method_name = m.get('type')
        if method_name in methods:
            method = methods[method_name]
        else:
            method = {}
            methods[method_name] = method

        for h in m.headers.header:
            header_name = h.get('type')
            if header_name in method:
                headers = method[header_name]
            else:
                headers = []
                method[header_name] = headers

            for r in h.representations.representation:
                if '+xml' in r.text:
                    headers.append(r.text)

    import yaml
    print yaml.dump(info, indent=4, default_flow_style=False)

if __name__ == '__main__':
    print 'Hello'
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
    print sample
    r = xml2obj(sample)
    print r.status
    from pprint import pprint
    pprint(r)
    pprint (r.netConfReplies.netConfReply.replyMsgData)

    print "New"

    for i in r._attrs:
        pprint(i)