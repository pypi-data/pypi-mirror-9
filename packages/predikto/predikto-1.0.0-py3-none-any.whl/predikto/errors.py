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

class RequestError(Exception):
    def __init__(self, response, content=None, message=None):
        self.response = response
        self.content = content
        self.message = message

    def __str__(self):
        message = "ERROR!"
        if hasattr(self.response, 'status_code'):
            message += " HTTP Status: %s." % (self.response.status_code)
        if hasattr(self.response, 'message'):
            message += " Message: %s." % (self.response.message)
        if self.content is not None:
            message += " Error: " + str(self.content)
        return message


class MissingConfig(Exception):
    pass


class ClientError(RequestError):
    """
    Base
    """
    pass


class InvalidResource(ClientError):
    """
    400
    """
    pass


class Unauthorized(ClientError):
    """
    401
    """
    pass


class Forbidden(ClientError):
    """
    403
    """
    pass


class ResourceNotFound(ClientError):
    """
    404
    """
    pass


class EntityTooLarge(ClientError):
    """
    413
    """
    pass


class ServerError(RequestError):
    """
    500
    """
    pass


class MethodNotAllowed(ClientError):
    """
    405
    """

    def allowed_methods(self):
        return self.response['Allow']
