import requests
import logging
import httplib


class Connection:
    """ Creates a connection to Space Platform mimicking a GUI login.
    This class is **not** thread-safe. It is up to the users of the class to
    ensure thread safety. The ``rest.Space`` class uses this class for
    supporting session-based connections to Junos Space. Thread-safety
    requirements are met by that class.
    """

    def __init__(self,
                 homeurl,
                 username=None,
                 password=None,
                 cert=None,
                 our_ip=None):
        self._logger = logging.getLogger('root')
        self.homeurl = homeurl + '/mainui'
        self.authurl = homeurl + '/mainui/j_security_check';

        if username is not None:
            if password is None:
                raise ValueError('password is mandatory along with username')
            if cert is not None:
                raise ValueError('You must provide only one of username+password or cert')
        else:
            if password is not None:
                raise ValueError('password is valid only along with username')
            if cert is None:
                raise ValueError('You must provide one of username+password or cert')

        self.username = username
        self.password = password
        self.our_ip = our_ip

        self.cert=cert

        self._logger.debug("Connection: Initiating login to %s" % self.homeurl)
        self.login()

    def login(self):
        """ Login to Space """

        self.session = requests.Session()
        s = self.session;
        if self.our_ip is None:
            r = s.get(self.homeurl, cert=self.cert, verify=False)
            #self._logger.debug(r.status_code)
            #self._logger.debug(r.headers)
            #self._logger.debug(r.text)

            # Extract the ipAddr and code variables embbed in the form validation code
            ipAddrStartIdx = r.text.find("var ipAddr = ");
            if (ipAddrStartIdx < 0) :
                self.check_login_status()
                return

            ipAddrEndIdx = r.text.find("\n", ipAddrStartIdx);
            ipAddrLine = r.text[ipAddrStartIdx : ipAddrEndIdx]
            ipAddrItems = ipAddrLine.split("=", 2);
            ipAddr = ipAddrItems[1].strip("'; ").strip();

            #codeStartIdx = r.text.find("var code = ", ipAddrEndIdx);
            #codeEndIdx = r.text.find("\n", codeStartIdx);
            #codeLine = r.text[codeStartIdx : codeEndIdx]
            #codeItems = codeLine.split("=", 2);
            #code = codeItems[1].strip("'; ").strip();'''

            #form_username = self.username + '%' + code + '@' + ipAddr;
        else:
            r = s.get(self.homeurl, cert=self.cert, verify=False)
            ipAddr = self.our_ip

        form_username = self.username + '@' + ipAddr;

        data = {
            "j_screen_username" : self.username,
            "j_username" : form_username,
            "j_password" : self.password
        }

        self._logger.debug(data)
        r = s.post(self.authurl, data=data, cert=self.cert, verify=False)

        #self._logger.debug(r.status_code)
        #self._logger.debug(r.headers)
        #self._logger.debug(r.text)

        self.check_login_status()

    def is_logged_in(self):
        """ Checks if a login has been established """
        if self.session:
            return True
        else:
            return False

    def check_login_status(self):
        """ Check login-status """

        if not self.is_logged_in():
            raise Exception("Not logged in")

        r = self.session.get(self.homeurl, verify=False)
        ipAddrStartIdx = r.text.find("var ipAddr = ");
        if ipAddrStartIdx >= 0:
            raise Exception("Not in a logged-in session.")

    def get_session(self):
        """ Return the HTTP session object  """
        if self.is_logged_in():
            return self.session
        else:
            raise Exception("Not logged in")

    def logout(self):
        """ Logout from Space Server  """
        logout_url = self.homeurl + "/unsecured/logout.jsp"
        r = self.session.get(logout_url, verify=False)
        #self._logger.debug(r.status_code)
        #self._logger.debug(r.headers)
        #self._logger.debug(r.text)

        if r.status_code == 200:
            self.session = None

if __name__ == '__main__':

    httplib.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    c = Connection('https://10.155.78.212', '', '',
                   cert=(
                        '/Users/rjoyce/ssl-cert-test/super.pem',
                        '/Users/rjoyce/ssl-cert-test/super_unencrypted.key'
                        ))
    r = c.session.get("https://10.155.78.212/api/space/user-management/users", verify=False)
    print r.text
    c.logout()