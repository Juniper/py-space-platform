from jinja2 import Environment, PackageLoader
from xmlutil import cleanup, xml2obj
from jnpr.space import rest

class Method(object):
    """
    Represents a **method** that is exposed by Junos Space REST API.
    Some examples of methods are:

    * exec-rpc on a device
      (``/api/space/device-management/devices/{id}/exec-rpc``)

    * change-password on a user account
      (``/api/space/user-management/users/{id}/change-password``)

    """

    def __init__(self, parent, name, mobj):
        """Initializes a Method object.

        :param parent: The parent object of this method.
        :type parent: jnpr.space.collection.Collection or
            jnpr.space.resource.Resource

        :param str name: Name of this method.

        :param meta_object: Meta object for this method.
        :type meta_object: jnpr.space.method.MetaMethod.

        """
        self._parent = parent
        self._rest_end_point = parent._rest_end_point
        self._name = name
        self.meta_object = mobj

    def get_href(self):
        """
        Gets the href for this method. If the meta object has its name set as
        '-', this returns the href of the parent. Otherwise, it concatenates
        the href of the parent object and the name of this method to form the
        href and returns it.

        :returns: The href of this method.

        """
        if self.meta_object.name != '-':
            return '/'.join([self._parent.get_href(), self.meta_object.name])
        else:
            return self._parent.get_href()


    def post(self, task_monitor=None, schedule=None, *args, **kwargs):
        """
        This sends a POST request corresponding to this Method object.

        :param task_monitor: A TaskMonitor object that can be used to monitor
            the progress of the POST request, in case of asynchronous
            invocations. You need to check Junos Space API documentation to
            see if the POST invocation on this resource has asynchronous
            semantics and supply the task_monitor parameter only if it is
            asynchronous. Otherwise, this will default to ``None`` and the
            method will behave with synchronous semantics.
        :type task_monitor: jnpr.space.async.TaskMonitor

        :param str schedule: A string specifying a cron expression for
            scheduling the execution of the request on the Space server side.
            This is applicable only if the POST invocation on this resource
            has asynchronous semantics and you want to schedule the execution.
            Otherwise, this will default to ``None``.

        :param kwargs: Keyword args of the form name=value which will be used
            to substitute variables in a pre-defined template to form the
            request body. The template name is specified inside the meta data
            for this Method object.
        :type kwargs: A variable list of name=value arguments.

        :returns: A Python object constructed from the response body that Space
            returned for the POST method invocation. In the case of asynchronous
            invocation, this will represent a Task object and will contain the
            unique id of the Task executing the POST request in Space.

        :raises: ``jnpr.space.rest.RestException`` if the POST method results in
            an error response. The exception's ``response`` attribute will have
            the full response from Space.

        """
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
        """Performs a GET corresponding to the Method object.

        :returns: A Python object constructed from the response body that Space
            returned for the GET request.

        :raises: ``jnpr.space.rest.RestException`` if the GET results in an
            error response. The exception's ``response`` attribute will have the
            full response from Space.

        """
        response = self._rest_end_point.get(self.get_href())
        if response.status_code != 200:
            raise rest.RestException("GET failed on %s " % self.get_href(),
                                    response)

        r = response.text
        return xml2obj(r)

class MetaMethod(object):
    """
    Encapsulates the meta data for a method.
    """

    def __init__(self, key, values):
        """Initializes a MetaMethod object.

        :param str key: Name of the method.

        :param dict values:  Attribute value settings which form the meta data
            for this method. This is read from the descriptions yml file for
            the corresponding service.

        """
        self.key = key
        self.name = values['name']
        self.request_type = values['request_type'] \
            if ('request_type' in values) else None
        self.response_type = values['response_type'] \
            if 'response_type' in values else None

        if 'request_template' in values:
            env = Environment(loader=PackageLoader('jnpr.space',
                                                   'templates'))
            self.request_template = env.get_template(values['request_template'])
        else:
            self.request_template = None

"""
A dictionary that acts as a cache for meta objects representing methods.
Keys are of the form <service-name>.<method-name>. Values are instances of
jnpr.space.collection.MetaMethod.
"""
_meta_methods = {}

def get_meta_object(app_name, service_name, method_name, values):
    """Looks up the meta object for a method based on its fully qualified
    type name of the form ``<service-name>.<method_name>`` or
    ``<app-name>.<service-name>.<method-name>``.

    :param str app_name: Name of the application.
    :param str service_name: Name of the service.
    :param str method_name: Name of the service.

    :returns: A ``jnpr.space.method.MetaMethod`` object.

    """
    if app_name:
        fullname = '.'.join([app_name, service_name, method_name])
    else:
        fullname = '.'.join([service_name, method_name])

    if fullname in _meta_methods:
        return _meta_methods[fullname]

    m = MetaMethod(method_name, values)
    _meta_methods[fullname] = m
    return m