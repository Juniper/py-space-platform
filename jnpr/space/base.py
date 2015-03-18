"""
This module defines a common base class called _SpaceBase from which
other classes (Service, Collection, Resource, Method) inherit common
functionality.
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from builtins import object
import yaml
from jnpr.space import xmlutil

class _SpaceBase(object):
    """
    Common base class for Service, Collection, Resource, and Method to
    contain common methods inherited by these sub-classes.
    """

    def info(self):
        """
        Prints info about this object onto stdout.
        """
        info = self._get_info()
        print('\n', yaml.safe_dump(info, indent=4, default_flow_style=False))

    def describe(self):
        """
        Prints a description of this object onto stdout.
        """
        data = self._describe()
        cname = self.__class__.__name__

        print('\n\t%s at URL: %s' % (cname, data['URL']))
        if len(data['collections']) > 0:
            print('\tContains following collections:')
            for c in data['collections']:
                print('\t\t%s (%s)' % c)

        if len(data['methods']) > 0:
            print('\tContains following methods:')
            for c in data['methods']:
                print('\t\t%s (%s)' % c)

        self._describe_details()

    def _get_info(self):
        url = '/api/info?uri=' + self.get_href()
        response = self._rest_end_point.get(url)
        if response.status_code != 200:
            from . import rest
            raise rest.RestException("GET failed on %s" % url, response)

        obj = xmlutil.xml2obj(xmlutil.get_text_from_response(response))
        """
        Create a dict such as this:
        {
          methods: {
            DELETE: {}
            GET: {
              Accept: [header1, header2]
            }
            PUT: {
              Media-type Combinations: {
                  1: {
                    Accept: header3
                    Content-Type: header4
                  }
                  2: {
                    Accept: header5
                    Content-Type: header6
                  }
              }
            }
            POST: {
              Media-type Combinations: [
                  {
                    Accept: header3
                    Content-Type: header4
                  }
                  {
                    Accept: header5
                    Content-Type: header6
                  }
              ]
            }
          }
        }
        """
        info = {}
        methods = {}
        info['HTTP Methods'] = methods
        for m in obj['http-methods']['http-method']:
            method_name = m.get('type')
            if method_name in methods:
                method = methods[method_name]
            else:
                method = {}
                methods[method_name] = method

            if method_name in ['GET', 'DELETE']:
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

            elif method_name in ['PUT', 'POST', 'PATCH']:
                if 'Media-type Combinations' not in method:
                    combs = []
                    method['Media-type Combinations'] = combs
                else:
                    combs = method['Media-type Combinations']

                comb = {}
                combs.append(comb)
                for h in m.headers.header:
                    header_name = h.get('type')
                    header_val = ''
                    for r in h.representations.representation:
                        if '+xml' in r.text:
                            header_val = r.text
                            break

                    comb[header_name] = header_val

        return info

    def _describe(self):
        data = {'URL': self.get_href()}
        data['collections'] = self._describe_collections()
        data['methods'] = self._describe_methods()
        return data

    def _describe_collections(self):
        result = []
        if 'collections' in self._meta_object.values and \
            self._meta_object.values['collections'] is not None:
            for k, v in self._meta_object.values['collections'].items():
                if 'name' in v:
                    name = v['name']
                elif 'xml_name' in v:
                    name = v['xml_name']
                name = xmlutil.make_xml_name(name)
                url = '/'.join(['...', name])
                result.append((k, url))
        result.sort()
        return result

    def _describe_methods(self):
        result = []
        if 'methods' in self._meta_object.values and \
            self._meta_object.values['methods'] is not None:
            for k, v in self._meta_object.values['methods'].items():
                if 'name' in v:
                    name = v['name']
                elif 'xml_name' in v:
                    name = v['xml_name']
                name = xmlutil.make_xml_name(name)
                url = '/'.join(['...', name])
                result.append((k, url))
        result.sort()
        return result

    def _describe_details(self):
        pass

if __name__ == '__main__':
    from jnpr.space import rest
    s = rest.Space('https://10.204.79.104', 'super', '123Juniper')
    s.configuration_management.describe()

