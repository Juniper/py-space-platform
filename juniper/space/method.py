'''
Created on 01-Jul-2014

@author: rjoyce
'''

from jinja2 import Environment, PackageLoader
from xmlutil import cleanup, xml2obj
from juniper.space import rest

class Method(object):

    def __init__(self, parent, name, mobj):
        self._parent = parent
        self._rest_end_point = parent._rest_end_point
        self._name = name
        self.meta_object = mobj

    def get_href(self):
        return '/'.join([self._parent.get_href(), self.meta_object.name])

    def post(self, task_monitor=None, schedule=None, *args, **kwargs):
        url = self.get_href()
        if 'id' in kwargs:
            url = '/'.join([url, kwargs['id']])
        if task_monitor:
            url = '?queue='.join([url, task_monitor.get_queue_url()])
            if schedule:
                url = '&schedule='.join([url, schedule])

        headers = {}
        if self.meta_object.response_type:
            headers['accept'] = self.meta_object.response_type

        if self.meta_object.request_template:
            body = self.meta_object.request_template.render(**kwargs)
            headers['content-type'] = self.meta_object.request_type
        else:
            body = None

        response = self._rest_end_point.post(url,headers,body)
        if (response.status_code != 202) and (response.status_code != 200):
            raise rest.RestException("POST failed on %s " % url, response)

        return xml2obj(cleanup(response.text)) if response.text else None

    def get(self):
        response = self._rest_end_point.get(self.get_href())
        if response.status_code != 200:
            raise rest.RestException("GET failed on %s " % self.get_href(),
                                    response)

        r = response.text
        return xml2obj(r)

class MetaMethod(object):
    def __init__(self, key, values):
        self.key = key
        self.name = values['name']
        self.request_type = values['request_type'] \
            if ('request_type' in values) else None
        self.response_type = values['response_type'] \
            if 'response_type' in values else None

        if 'request_template' in values:
            env = Environment(loader=PackageLoader('juniper.space',
                                                   'templates'))
            self.request_template = env.get_template(values['request_template'])
        else:
            self.request_template = None


_meta_methods = {}

def get_meta_object(method_name, values):
    if method_name in _meta_methods:
        return _meta_methods[method_name]

    m = MetaMethod(method_name, values)
    _meta_methods[method_name] = m
    return m