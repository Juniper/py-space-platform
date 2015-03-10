from jinja2 import Environment, PackageLoader
from xmlutil import cleanup, xml2obj
from jnpr.space import rest, base

class Method(base._SpaceBase):
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
        self._meta_object = mobj

    def get_href(self):
        """
        Gets the href for this method. If the meta object has its name set as
        '-', this returns the href of the parent. Otherwise, it concatenates
        the href of the parent object and the name of this method to form the
        href and returns it.

        :returns: The href of this method.

        """
        if self._meta_object.name != '-':
            return '/'.join([self._parent.get_href(), self._meta_object.name])
        else:
            return self._parent.get_href()

    def post(self, accept=None, content_type=None, request_body=None,
             task_monitor=None, schedule=None, *args, **kwargs):
        """
        This sends a POST request corresponding to this Method object.

        :param str accept: This can be used to supply a media-type that must
            be used as the Accept header in the request. This defaults to
            ``None`` and in this case SpaceEZ will use the media-type modeled
            in the description file.

        :param str content_type: This can be used to supply a media-type that must
            be used as the Content-Type header in the request. This defaults to
            ``None`` and in this case SpaceEZ will use the media-type modeled
            in the description file.

        :param str request_body: This can be used to supply a string that must
            be used as the request body in the request. This defaults to
            ``None`` and in this case SpaceEZ will create the request body
            using the modeled template, replacing variables with kwargs.

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
        if content_type is not None:
            headers['content-type'] = content_type
        else:
            if self._meta_object.request_template:
                headers['content-type'] = self._meta_object.get_request_type(None)

        if accept is not None:
            headers['accept'] = accept
        else:
            headers['accept'] = self._meta_object.get_response_type(None)

        if request_body is not None:
            body = request_body
        elif self._meta_object.request_template:
            body = self._meta_object.request_template.render(**kwargs)
        else:
            body = None

        response = self._rest_end_point.post(url, headers, body)
        if (response.status_code != 202) and (response.status_code != 200):
            raise rest.RestException("POST failed on %s " % url, response)

        try:
            return xml2obj(cleanup(response.content)) if response.content else None
        except:
            raise rest.RestException("Failed to parse XML response for %s " % url, response)

    def get(self, accept=None):
        """Performs a GET corresponding to the Method object.

        :param str accept: This can be used to supply a media-type that must
            be used as the Accept header in the GET request. This defaults to
            ``None`` and in this case SpaceEZ will use the media-type modeled
            in the description file.

        :returns: A Python object constructed from the response body that Space
            returned for the GET request.

        :raises: ``jnpr.space.rest.RestException`` if the GET results in an
            error response. The exception's ``response`` attribute will have the
            full response from Space.

        """

        if accept is not None:
            mtype = accept
        else:
            mtype = self._meta_object.get_media_type(None)

        if mtype is not None:
            if not self._meta_object.retain_charset_in_accept:
                end = mtype.find(';charset=')
                if end > 0:
                    mtype = mtype[0:end]
            headers = {'accept' : mtype}
        else:
            headers = {}

        response = self._rest_end_point.get(self.get_href(), headers)
        if response.status_code != 200:
            raise rest.RestException("GET failed on %s " % self.get_href(),
                                    response)

        r = response.content
        return xml2obj(r)

    def _describe_details(self):
        rt = self._meta_object.request_template
        if rt is None:
            return

        print '\tFollowing named parameters may be supplied to the post() call:\n',
        with open(rt.filename) as f:
            lines = [line.rstrip() for line in f]
            for line in lines:
                if line.endswith('#}'):
                    break
                elif not line.strip().startswith('{#'):
                    print '\t', line


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
        self.values = values
        self.key = key
        self.name = values['name']
        self.request_type = values['request_type'] \
            if ('request_type' in values) else None
        self.response_type = values['response_type'] \
            if 'response_type' in values else None
        self.media_type = values['media_type'] \
            if ('media_type' in values) else None
        self.retain_charset_in_accept = values['retain_charset_in_accept'] \
            if ('retain_charset_in_accept' in values) else False

        if 'request_template' in values:
            env = Environment(loader=PackageLoader('jnpr.space',
                                                   'templates'))
            self.request_template = env.get_template(values['request_template'])
        else:
            self.request_template = None

    def get_request_type(self, version):
        if isinstance(self.request_type, dict):
            if version is not None:
                return self.request_type[str(version)]
            if len(self.request_type) == 1:
                return self.request_type.itervalues().next()
            else:
                raise Exception("You must specify the required request_type version")
        elif version is None:
            return self.request_type

        raise Exception("Request Type Version %s not defined for '%s' in descriptions!" %
                        (str(version), self.key))

    def get_response_type(self, version):
        if isinstance(self.response_type, dict):
            if version is not None:
                return self.response_type[str(version)]
            if len(self.response_type) == 1:
                return self.response_type.itervalues().next()
            else:
                raise Exception("You must specify the required response_type version")
        elif version is None:
            return self.response_type

        raise Exception("Response Type Version %s not defined for '%s' in descriptions!" %
                        (str(version), self.key))

    def get_media_type(self, version):
        if isinstance(self.media_type, dict):
            if version is not None:
                return self.media_type[str(version)]
            if len(self.media_type) == 1:
                return self.media_type.itervalues().next()
            else:
                raise Exception("You must specify the required media_type version")
        elif version is None:
            return self.media_type

        raise Exception("Media Type Version %s not defined for '%s' in descriptions!" %
                        (str(version), self.key))
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