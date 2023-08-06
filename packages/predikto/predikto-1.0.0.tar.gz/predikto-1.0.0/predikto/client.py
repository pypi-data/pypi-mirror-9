# Copyright 2014-2015 Predikto, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

import logging
from platform import platform, mac_ver, win32_ver, linux_distribution, system
from sys import version_info as vi
import json
import datetime
import time

import requests

from predikto import Auth
from predikto import errors
from predikto import tools


"""
Predikto API Client
"""
__version_info__ = ('1', '0', '0')
_VERSION = '.'.join(__version_info__)
__short_version__ = '.'.join(__version_info__)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class Client(object):
    """The root entry point for SDK functionality.

    Using the client instance, you can access all Predikto data.

    More info in documentation:
    http://docs.predikto.io

    The client contains the following attributes that represent resource lists:

    :py:attr:`reports` -
    :class:`predikto.resources.report.ReportList`

    """
    BASE_URL = 'https://api.predikto.io'

    os_info = platform()
    os_versions = {
        'Linux': "%s (%s)" % (linux_distribution()[0], os_info),
        'Windows': "%s (%s)" % (win32_ver()[0], os_info),
        'Darwin': "%s (%s)" % (mac_ver()[0], os_info),
    }

    USER_AGENT = 'predikto-sdk-python/%s python/%s %s/%s' % (
        _VERSION,
        '%s.%s.%s' % (vi.major, vi.minor, vi.micro),
        system(),
        os_versions.get(system(), ''),
    )

    def __init__(self, configs, **kwargs):

        kwargs = tools.merge_dict(configs or {}, kwargs)

        self.BASE_URL = kwargs.get('base_url') or self.BASE_URL
        self.auth = Auth(**kwargs)

    def request(self, url, method, body=None, headers=None):
        """
        Performs HTTP call and handles response and errors.
        At this point, the header already includes our method and resource
        """
        http_headers = self.build_headers(headers)

        try:
            return self.http_request(url, method, data=json.dumps(body), headers=http_headers)
        except errors.InvalidResource as error:
            return {"error": json.loads(error.content)}

    def http_request(self, url, method, **kwargs):
        """
         Runs the HTTP request. Logs response.
        """
        logging.info('Request[%s]: %s' % (method, url))
        start = datetime.datetime.now()

        response = requests.request(method, url, **kwargs)

        duration = datetime.datetime.now() - start

        logging.info('Response[%d]: %s, Duration: %s.%ss.' % (response.status_code, response.reason, duration.seconds, duration.microseconds))
        debug_id = response.headers.get('X-Predikto-Debug-Id')
        version = response.headers.get('X-Predikto-Version')
        exec_time = response.headers.get('X-Execution-Time')

        logging.debug('Debug ID: %s' % debug_id)
        logging.debug('Server Version: %s' % version)
        logging.debug('Execution Time: %s' % exec_time)

        return self.handle_response(response, response.content.decode('utf-8'))

    def build_headers(self, headers=None):
        """
        HTTP headers contain specific required parameters and the signed policy
        :type headers: dict of headers
        """
        if headers is None:
            headers = {}

        base_headers = {
            "api_key_id": self.auth.api_key_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.USER_AGENT}
        seconds_since_epoch = int(time.time())
        temp_headers = tools.merge_dict(base_headers, headers, {'ts': seconds_since_epoch})
        signature = self.auth.create_signature(temp_headers)

        http_headers = tools.merge_dict(temp_headers, {'signature': signature})

        return http_headers

    def get(self, action, headers=None):
        """
        GET requests
        """
        return self.request(tools.merge_url(self.BASE_URL, action), 'GET', headers=headers or {})

    def post(self, action, params=None, headers=None):
        """
        POST requests
        """
        return self.request(tools.merge_url(self.BASE_URL, action), 'POST', body=params or {}, headers=headers or {})

    def put(self, action, params=None, headers=None):
        """
        PUT requests
        """
        return self.request(tools.merge_url(self.BASE_URL, action), 'PUT', body=params or {}, headers=headers or {})

    def delete(self, action, headers=None):
        """
        DELETE requests
        """
        return self.request(tools.merge_url(self.BASE_URL, action), 'DELETE', headers=headers or {})

    @staticmethod
    def handle_response(response, content):
        status = response.status_code
        if 200 <= status <= 299:
            return json.loads(content) if content else {}
        elif status == 400:
            raise errors.InvalidResource(response, content)
        elif status == 401:
            raise errors.Unauthorized(response, content)
        elif status == 403:
            raise errors.Forbidden(response, content)
        elif status == 404:
            raise errors.ResourceNotFound(response, content)
        elif status == 405:
            raise errors.MethodNotAllowed(response, content)
        elif status == 413:
            raise errors.EntityTooLarge(response, content)
        elif status == 500:
            raise errors.ServerError(response, content)
        else:
            raise errors.RequestError(response, content, "Unknown response: #{response.code}")


__api__ = None


def default():
    global __api__
    return __api__


def set_config(configs=None, **kwargs):
    global __api__
    __api__ = Client(configs or {}, **kwargs)
    return __api__


configure = set_config
