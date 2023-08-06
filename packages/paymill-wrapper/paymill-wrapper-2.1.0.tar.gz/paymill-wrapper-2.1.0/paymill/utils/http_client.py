# coding=utf-8
__author__ = 'yalnazov'
from requests import Session
from ..utils import abstract_http_client
from .pm_error import PMError
import logging
# these two lines enable debugging at httplib level (requests->urllib3->httplib)
# you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# the only thing missing will be the response.body which is not logged.
from six.moves import http_client
http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()  # you need to initialize logging, otherwise you will not see anything from requests
logging.getLogger().setLevel(logging.INFO)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.ERROR)
requests_log.propagate = True


class HTTPClient(abstract_http_client.AbstractHTTPClient):
    def __init__(self, base_url, user_name, user_pass=''):
        """Initialize a new paymill interface connection. Requires a private key."""
        self.base_url = base_url
        self.session = Session()
        self.session.auth = (user_name, "")
        self.session.verify = False
        self.operations = dict(GET=self.get, POST=self.post, PUT=self.put, DELETE=self.delete)
        #for internal usage
        self.response = None

    def __call__(self, request_type, params, url, return_type):
        try:
            return self.operations[request_type](params, url, return_type)
        except ValueError as v:
            # JSON encoding failed
            #=>PAYMILL API sent us an error, without JSON data
            if self.response is not None:
                raise PMError(self.response.content, self.response.status_code)
            else:
                raise PMError()

    def put(self, params, url, return_type):
        return self._check_reponse(self.session.put(self.base_url + url, params,
                                                    hooks=dict(response=self._request_callback)).json(), return_type)

    def post(self, params, url, return_type):
        json = self.session.post(self.base_url + url, params, hooks=dict(response=self._request_callback)).json()
        return self._check_reponse(json, return_type)

    def delete(self, params, url, return_type):
        return self._check_reponse(self.session.delete(self.base_url + url, params=params,
                                                       hooks=dict(response=self._request_callback)).json(), return_type)

    def get(self, params, url, return_type):
        return self._check_reponse(self.session.get(self.base_url + url, params=params,
                                                    hooks=dict(response=self._request_callback)).json(), return_type)

    def _request_callback(self, r, *args, **kwargs):
        self.response = r

    def _check_reponse(self, json_data, return_type):
        if 'data' in json_data:
            #success
            if isinstance(json_data['data'], dict):
                return return_type(json_data['data'])
            else:
                return return_type(json_data)
        else:
            #error
            raise PMError(json_data, self.response.status_code)
