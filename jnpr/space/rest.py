from __future__ import print_function
import os
import re

import requests
import logging
import yaml

class Space:
    """Encapsulates a Junos Space cluster and provides access to all RESTful
    web-service APIs provided by Space. An instance of this class is also
    referred to as a *'rest end point'* in this documentation.

    .. note::
        In most cases, you don't directly invoke methods of this class. The
        typical usage pattern is to create an instance of this class and then
        access contained services and collections and invoke methods on them.

    For example, the snippet below creates a Space instance and then performs
    a GET on the ``devices`` collection contained by the ``device-management``
    web service:

        >>> s = rest.Space(url='https://1.1.1.1', user='super', passwd='password')
        >>> devs = s.device_management.devices.get()
    """

    def __init__(self,
                 url,
                 user=None,
                 passwd=None,
                 cert=None,
                 use_session=False,
                 required_node=None,
                 profile_file=None):
        """Creates an instance of this class to represent a Junos Space cluster.

        :param url: URL of the Junos Space cluster using its VIP address.
                    E.g. https://<VIP>
        :type url: str
        :param str user: A valid userid for invoking APIs on this Space cluster.
            Can be omitted if ``cert`` is provided for X.509 certificate based
            authentication to Junos Space.
        :param str passwd: Password for the userid.
        :param tuple cert: X.509 certificate details for authentication.
            This is to be used only to access Junos Space that is configured to
            perform X.509 certificate based authentication. Otherwise, this
            parameter defaults to ``None``. If used, it MUST be a tuple that
            contains (1) the full pathname of the X.509 certificate PEM file;
            and (2) the full pathname of the X.509 certificate key file. It is
            recommended that the key file is unencrypted - otherwise the SSL
            layer will prompt you to enter the passphrase used for encrypting
            key file and this prompt will appear for each SSL connection.
        :param bool use_session: Whether to use a session based login or not.
            It is ``False`` by default.
        :param str required_node: This parameter is used only if ``use_session``
            is set to True. This is used to specify the name of the Junos Space
            node (e.g. space-000c2980f778) in the cluster on which the session
            should be established. This parameter is ``None`` by default.
        :param str profile_file: Full pathname of a file where response times
            for each API call is to be recorded. This parameter is ``None``
            by default.

        :returns:  An instance of this class encapsulating the Junos Space
                   cluster whose **url** was given as a parameter. It can be
                   used to access all APIs provided by Space.
        """
        self.space_url = url

        if user is not None:
            if passwd is None:
                raise ValueError('passwd is mandatory along with user')
            if cert is not None:
                raise ValueError('You must provide only one of user+passwd or cert')
            self.space_user = user
            self.space_passwd = passwd
            self.cert = None
        else:
            if passwd is not None:
                raise ValueError('passwd is valid only along with user')
            if cert is None:
                raise ValueError('You must provide one of user+passwd or cert')
            self.cert = cert
            self.space_user = None
            self.space_passwd = None

        self._logger = logging.getLogger('root')
        self._meta_services = self._init_services()
        self._meta_applications = self._init_applications()
        self._services = {}
        self._applications = {}
        self.use_session = use_session

        if use_session:
            self.login(required_node)

        if profile_file is not None:
            self.profile_file = open(profile_file, 'w')
        else:
            self.profile_file = None

    def __str__(self):
        return ' '.join(['Space <',
                       '@'.join([self.space_user, self.space_url]),
                       '>'])

    def _init_services(self):
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        with open(dir_path + '/descriptions/services.yml') as f:
            return yaml.load(f)['services']

    def _init_applications(self):
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        with open(dir_path + '/descriptions/applications.yml') as f:
            return yaml.load(f)['applications']

    def __getattr__(self, attr):
        """
        This method is overridden in the class so that applications & services
        contained by this instance can be accessed as *normal* Python
        attributes of this object.

        :param str attr: Name of the app or web-service being accessed.

        :returns: ``jnpr.space.service.Service`` or
            ``jnpr.space.application.Application`` being accessed.
        :raises: AttributeError if there is no application or service
            with the given name.

        """
        if attr in self._services:
            return self._services[attr]

        if attr in self._meta_services:
            from jnpr.space import service
            value = self._meta_services[attr]
            self._services[attr] = service.Service(self, attr, value)
            return self._services[attr]

        if attr in self._applications:
            return self._applications[attr]

        if attr in self._meta_applications:
            from jnpr.space import application
            value = self._meta_applications[attr]
            self._applications[attr] = application.Application(self,
                                                               attr, value)
            return self._applications[attr]

        raise AttributeError("No attribute '%s'" % attr)

    def __getitem__(self, attr):
        """
        This method is overridden so that contained elements can be accessed
        using their 'xml names' - e.g. user['first-name']. The implementation
        just calls __getattr__ internally.

        See doc for __getattr__ for more details.
        """

        from jnpr.space import xmlutil
        return self.__getattr__(xmlutil.unmake_xml_name(attr))

    def _log_time(self, op, url, response):
        if self.profile_file is not None:
            url = re.sub(r'\d+', '{id}', url)
            url = re.sub(r',', '_', url)
            num_ms = response.elapsed.seconds * 1000 + \
                     response.elapsed.microseconds / 1000
            print("%s, %s, %d, %d" % (op, url, response.status_code,
                                      num_ms),
                  file=self.profile_file)

    def get(self, url, headers={}):
        """Performs an HTTP GET on the given url. Acts as a wrapper over
        requests.get() function.

        :param str url: URL for performing GET
        :param dict headers: A dict with the headers that need to be sent with
            the GET request. Defaults to ``{}``.

        :returns:  The response object (`requests.Response <http://docs.python-requests.org/en/latest/api/#requests.Response />`_)
                   returned by the GET request.
        """
        req_url = self.space_url + url
        self._logger.debug("GET %s" % req_url)
        self._logger.debug(headers)
        if self.use_session:
            r = self.connection.get_session().get(req_url, headers=headers, verify=False)
        else:
            if self.cert is not None:
                r = requests.get(req_url, cert=self.cert, headers=headers, verify=False)
            else:
                r = requests.get(req_url, auth=(self.space_user, self.space_passwd), headers=headers, verify=False)
        self._logger.debug(r)
        self._logger.debug(r.headers)
        self._logger.debug(r.cookies)
        self._logger.debug(r.text)
        self._log_time('GET', url, r)
        return r

    def head(self, url, headers={}):
        """Performs an HTTP HEAD on the given url. Acts as a wrapper over
        requests.head() function.

        :param str url: URL for performing HEAD
        :param dict headers: A dict with the headers that need to be sent with
            the HEAD request. Defaults to ``{}``.

        :returns:  The response object (`requests.Response <http://docs.python-requests.org/en/latest/api/#requests.Response />`_)
            returned by the HEAD request.
        """
        req_url = self.space_url + url
        self._logger.debug("HEAD %s" % req_url)
        self._logger.debug(headers)
        if self.use_session:
            r = self.connection.get_session().head(req_url, headers=headers, verify=False)
        else:
            if self.cert is not None:
                r = requests.head(req_url, cert=self.cert, headers=headers, verify=False)
            else:
                r = requests.head(req_url, auth=(self.space_user, self.space_passwd), headers=headers, verify=False)
        self._logger.debug(r)
        self._logger.debug(r.headers)
        self._logger.debug(r.cookies)
        self._logger.debug(r.text)
        self._log_time('HEAD', url, r)
        return r

    def post(self, url, headers, body):
        """Performs an HTTP POST on the given url. Acts as a wrapper over
        requests.post() function.

        :param str url: URL for performing POST
        :param dict headers: A dict with the headers that need to be sent with
            the POST request. This is a mandatory parameter.
        :param str body: A string that forms the body of the POST request.
            This is a mandatory parameter.

        :returns:  The response object (`requests.Response <http://docs.python-requests.org/en/latest/api/#requests.Response />`_)
                   returned by the POST request.
        """
        req_url = self.space_url + url
        self._logger.debug("POST %s" % req_url)
        self._logger.debug(headers)
        self._logger.debug(body)
        if self.use_session:
            r = self.connection.get_session().post(req_url, data=body, headers=headers, verify=False)
        else:
            if self.cert is not None:
                r = requests.post(req_url, cert=self.cert, data=body, headers=headers, verify=False)
            else:
                r = requests.post(req_url, auth=(self.space_user, self.space_passwd), data=body, headers=headers, verify=False)
        self._logger.debug(r)
        self._logger.debug(r.headers)
        self._logger.debug(r.cookies)
        self._logger.debug(r.text)
        self._log_time('POST', url, r)
        return r

    def put(self, put_url, headers, body):
        """Performs an HTTP PUT on the given url. Acts as a wrapper over
        requests.put() function.

        :param str url: URL for performing PUT
        :param dict headers: A dict with the headers that need to be sent with
            the PUT request. This is a mandatory parameter.
        :param str body: A string that forms the body of the PUT request.
            This is a mandatory parameter.

        :returns:  The response object (`requests.Response <http://docs.python-requests.org/en/latest/api/#requests.Response />`_)
                   returned by the PUT request.
        """
        req_url = self.space_url + put_url
        self._logger.debug("PUT %s" % req_url)
        self._logger.debug(headers)
        self._logger.debug(body)
        if self.use_session:
            r = self.connection.get_session().put(req_url, data=body, headers=headers, verify=False)
        else:
            if self.cert is not None:
                r = requests.put(req_url, cert=self.cert, data=body, headers=headers, verify=False)
            else:
                r = requests.put(req_url, auth=(self.space_user, self.space_passwd), data=body, headers=headers, verify=False)
        self._logger.debug(r)
        self._logger.debug(r.headers)
        self._logger.debug(r.cookies)
        self._logger.debug(r.text)
        self._log_time('PUT', put_url, r)
        return r

    def delete(self, delete_url):
        """Performs an HTTP DELETE on the given url. Acts as a wrapper over
        requests.delete() function.

        :param str url: URL for performing DELETE

        :returns:  The response object (`requests.Response <http://docs.python-requests.org/en/latest/api/#requests.Response />`_)
                   returned by the POST request.
        """
        req_url = self.space_url + delete_url
        self._logger.debug("DELETE %s" % req_url)
        if self.use_session:
            r = self.connection.get_session().delete(req_url, verify=False)
        else:
            if self.cert is not None:
                r = requests.delete(req_url, cert=self.cert, verify=False)
            else:
                r = requests.delete(req_url, auth=(self.space_user, self.space_passwd), verify=False)
        self._logger.debug(r)
        self._logger.debug(r.headers)
        self._logger.debug(r.cookies)
        self._logger.debug(r.text)
        self._log_time('DELETE', delete_url, r)
        return r

    def logout(self):
        """Logs out the current session being used.
        """
        self.connection.logout()

    def login(self, required_node=None):
        """Logs into Space and creates a session (connection) that is maintained.
        All API calls will use this session and will use the JSESSIONID,
        JSESSIONIDSSO cookies - they will not be individually authenticated.

        :param str required_node: This is used to specify the name of the Junos
            Space node in the cluster on which the session should be established.
            It is ``None`` by default.
        """
        from jnpr.space import connection
        for i in range(10):
            if self.space_user:
                self.connection = connection.Connection(self.space_url,
                                                        self.space_user,
                                                        self.space_passwd)
            else:
                self.connection = connection.Connection(self.space_url,
                                                        cert=self.cert)
            if required_node is not None:
                sid = self.connection.get_session().cookies['JSESSIONID']
                end = sid.rindex(':')
                start = sid.rindex('.') + 1
                node_name = sid[start:end]
                if required_node == node_name:
                    self._logger.debug("Try %d: Got session on %s" % (i, required_node))
                    return
                else:
                    self._logger.debug("Try %d: Got session on %s instead of %s" % (i, node_name, required_node))
                    self.logout()
            else:
                return

        raise Exception('Unable to get a session on %s in 10 attempts' % required_node)


class RestException(Exception):
    """An exception that is raised when a REST API invocation returns a response
    indicating an error. The exception contains the complete response inside.

    Attributes:
        response: The response object (`requests.Response <http://docs.python-requests.org/en/latest/api/#requests.Response />`_) \
                  which resulted in this exception.
    """
    def __init__(self, message, response):
        Exception.__init__(self, message)
        self.response = response