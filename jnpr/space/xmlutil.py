'''
Recipe copied from:
    http://code.activestate.com/recipes/534109-xml-to-python-data-structure/

@author: Wai Yip Tung

'''
import re
import xml.sax.handler

def cleanup(src):
    xml = src.replace('&lt;', '<').replace('&gt;', '>')
    xml = xml.replace('&quot;', '"')
    return xml

def xml2obj(src):
    """
    A simple function to converts XML data into native Python object.
    """

    non_id_char = re.compile('[^_0-9a-zA-Z]')
    def _name_mangle(name):
        return non_id_char.sub('_', name)

    class DataNode(object):
        def __init__(self):
            self._attrs = {}    # XML attributes and child elements
            self.data = None    # child text data
        def __len__(self):
            # treat single element as a list of 1
            return 1
        def __getitem__(self, key):
            if isinstance(key, basestring):
                return self._attrs.get(key,None)
            else:
                return [self][key]
        def __contains__(self, name):
            return self._attrs.has_key(name)
        def __nonzero__(self):
            return bool(self._attrs or self.data)
        def __getattr__(self, name):
            if name.startswith('__'):
                # need to do this for Python special methods???
                raise AttributeError(name)
            return self._attrs.get(name,None)
        def _add_xml_attr(self, name, value):
            if name in self._attrs:
                # multiple attribute of the same name are represented by a list
                children = self._attrs[name]
                if not isinstance(children, list):
                    children = [children]
                    self._attrs[name] = children
                children.append(value)
            else:
                self._attrs[name] = value
        def __str__(self):
            return self.data or ''
        def __repr__(self):
            items = sorted(self._attrs.items())
            if self.data:
                items.append(('data', self.data))
            return u'{%s}' % ', '.join([u'%s:%s' % (k,repr(v)) for k,v in items])

    class TreeBuilder(xml.sax.handler.ContentHandler):
        def __init__(self):
            self.stack = []
            self.root = DataNode()
            self.current = self.root
            self.text_parts = []
        def startElement(self, name, attrs):
            self.stack.append((self.current, self.text_parts))
            self.current = DataNode()
            self.text_parts = []
            # xml attributes --> python attributes
            for k, v in attrs.items():
                self.current._add_xml_attr(_name_mangle(k), v)
        def endElement(self, name):
            text = ''.join(self.text_parts).strip()
            if text:
                self.current.data = text
            if self.current._attrs:
                obj = self.current
            else:
                # a text only node is simply represented by the string
                obj = text or ''
            self.current, self.text_parts = self.stack.pop()
            self.current._add_xml_attr(_name_mangle(name), obj)
        def characters(self, content):
            self.text_parts.append(content)

    builder = TreeBuilder()
    if isinstance(src,basestring):
        xml.sax.parseString(src, builder)
    else:
        xml.sax.parse(src, builder)
    return builder.root._attrs.values()[0]

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