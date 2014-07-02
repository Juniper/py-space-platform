import os

import requests
import logging
import yaml

class Space:
    """Encapsulates a Space REST endpoint"""


    def __init__(self, url, user, passwd):
        self.space_url = url
        self.space_user = user
        self.space_passwd = passwd
        self._logger = logging.getLogger('root')
        self._meta_services = self._init_services()
        self._services = {}

    def __str__(self):
        return ' '.join(['Space <',
                       '@'.join([self.space_user, self.space_url]),
                       '>'])

    def _init_services(self):
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        with open(dir_path + '/services.yml') as f:
            return yaml.load(f)['services']

    def __getattr__(self, attr):
        if attr in self._services:
            return self._services[attr]

        if attr in self._meta_services:
            from jnpr.space.platform.core import service
            value = self._meta_services[attr]
            self._services[attr] = service.Service(self, attr, value)
            return self._services[attr]

        raise AttributeError("No attribute '%s'" % attr)

    def get(self, get_url, headers={}):
        req_url = self.space_url + get_url
        self._logger.debug("GET %s" % req_url)
        self._logger.debug(headers)
        r = requests.get(req_url, auth=(self.space_user, self.space_passwd), headers=headers, verify=False)
        self._logger.debug(r)
        self._logger.debug(r.text)
        return r

    def head(self, get_url, headers={}):
        req_url = self.space_url + get_url
        self._logger.debug("HEAD %s" % req_url)
        self._logger.debug(headers)
        r = requests.head(req_url, auth=(self.space_user, self.space_passwd), headers=headers, verify=False)
        self._logger.debug(r)
        self._logger.debug(r.headers)
        self._logger.debug(r.text)
        return r

    def post(self, post_url, headers, body):
        req_url = self.space_url + post_url
        self._logger.debug("POST %s" % req_url)
        self._logger.debug(headers)
        self._logger.debug(body)
        r = requests.post(req_url, auth=(self.space_user, self.space_passwd), data=body, headers=headers, verify=False)
        self._logger.debug(r)
        self._logger.debug(r.headers)
        self._logger.debug(r.text)
        return r

    def put(self, put_url, headers, body):
        req_url = self.space_url + put_url
        self._logger.debug("PUT %s" % req_url)
        self._logger.debug(headers)
        self._logger.debug(body)
        r = requests.put(req_url, auth=(self.space_user, self.space_passwd), data=body, headers=headers, verify=False)
        self._logger.debug(r)
        self._logger.debug(r.text)
        return r

    def delete(self, delete_url):
        req_url = self.space_url + delete_url
        self._logger.debug("DELETE %s" % req_url)
        r = requests.delete(req_url, auth=(self.space_user, self.space_passwd), verify=False)
        self._logger.debug(r)
        self._logger.debug(r.text)
        return r
