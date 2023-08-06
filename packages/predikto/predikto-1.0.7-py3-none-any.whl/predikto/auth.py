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
import hmac
from hashlib import sha1
import base64
from os import environ
from predikto.errors import MissingConfig

class Auth(object):
    """
    All available authentication credentials sources are checked, in this order:

        1. API key `api_key_id` and `api_key_secret` parameters
        2. PREDIKTO_API_KEY_ID and PREDIKTO_API_KEY_SECRET as environmentvariables.

        The `api_key_id` and `api_key_secret` can be accessed as attributes.
    """

    def __init__(self, **kwargs):
        if kwargs.get('api_key_id') is not None and kwargs.get('api_key_secret') is not None:
            self.api_key_id = kwargs["api_key_id"]
            self.api_key_secret = kwargs["api_key_secret"]
            return

        self.api_key_id = environ.get('PREDIKTO_API_KEY_ID')
        self.api_key_secret = environ.get('PREDIKTO_API_KEY_SECRET')

        if self.api_key_id is None or self.api_key_secret is None:
            raise MissingConfig('Missing API key values!')


    def create_signature(self, headers):
        """
        Based on request parameters, creates the signature
        :param headers:
        :return:
        """
        string_to_sign = headers.get('api_key_id') + headers.get('method') + headers.get('resource') + str(headers.get('ts'))

        string_to_sign_b64 = base64.b64encode(string_to_sign.encode('utf-8')).decode('utf-8')
        signature = base64.b64encode(hmac.new(bytes(self.api_key_secret, 'utf-8'), string_to_sign_b64.encode('utf-8'), sha1).digest())

        return signature