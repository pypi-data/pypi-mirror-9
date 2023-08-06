from StringIO import StringIO
from getpass import getpass
import json
import pycurl
import urllib

# more info
# http://dev.targetprocess.com/rest/response_format
# http://md5.tpondemand.com/api/v1/index/meta

class TargetProcess(object):

    API_VERSION = '/api/v1'

    _base_api_url = None
    _username = None
    _password = None

    def __init__(self, username, password, base_api_url):
        self._username = username
        self._password = password
        self._base_api_url = base_api_url

    def _get_base_api_url(self):
        message = ('You must provide your Target Process On-Demand or On-Site'
                   'URL (example: mytargetprocess.tpondemand.com):\n')
        if self._base_api_url is None:
            raise ValueError(message) 
        return self._base_api_url

    def _get_username(self):
        message = ('You must provide your valid username')
        if self._username is None:
            raise ValueError(message) 
        return self._username

    def _get_password(self):
        message = ('You must provide your valid password')
        if self._password is None:
            raise ValueError(message) 
        return self._password

    def _build_url(self, url, params = {}):
        params.setdefault('format', 'json')
        enconded_params = urllib.urlencode(params)
        return '{}?{}'.format(url, enconded_params)

    def _build_url_from_resource(self, resource, params = {}):
        url = self._get_base_api_url() + self.API_VERSION + '/' + resource
        return self._build_url(url, params)

    def _send_request(self, encoded_url):
        output = StringIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, encoded_url)
        curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_NTLM)
        curl.setopt(pycurl.USERPWD, '{}:{}'.format(self._get_username(), self._get_password()))
        curl.setopt(pycurl.WRITEFUNCTION, output.write)
        try:
            curl.perform()
            response = json.loads(output.getvalue())
        except ValueError as error:
            print 'An error has occurred:', error.message
        return response

    def get_resource(self, resource, params = {}):
        # You can access various resources in Target Process REST API
        # http://dev.targetprocess.com/rest/resource
        encoded_url = self._build_url_from_resource(resource, params)
        return self._send_request(encoded_url)
