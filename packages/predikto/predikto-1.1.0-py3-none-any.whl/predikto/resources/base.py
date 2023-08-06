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

import uuid

from predikto.client import default as default_api
from predikto import tools


class Resource(object):
    """Base class for all REST services
    """
    convert_resources = {}

    def __init__(self, attributes=None, api=None, headers=None):
        attributes = attributes or {}
        self.__dict__['api'] = api or default_api()

        super(Resource, self).__setattr__('__data__', {})
        super(Resource, self).__setattr__('error', None)
        super(Resource, self).__setattr__('headers', headers)
        super(Resource, self).__setattr__('header', {})
        super(Resource, self).__setattr__('request_id', None)
        self.merge(attributes)

    def generate_request_id(self):
        """Generate uniq request id
        """
        if self.request_id is None:
            self.request_id = str(uuid.uuid4())
        return self.request_id

    def make_headers(self):
        """
        Generate HTTP header
        """
        return tools.merge_dict(self.header, self.headers,
                                {'Predikto-Request-Id': self.generate_request_id()})

    def __str__(self):
        return self.__data__.__str__()

    def __repr__(self):
        return self.__data__.__str__()

    def __getattr__(self, name):
        return self.__data__.get(name)

    def __setattr__(self, name, value):
        try:
            super(Resource, self).__getattribute__(name)
            super(Resource, self).__setattr__(name, value)
        except AttributeError:
            self.__data__[name] = self.convert(name, value)

    def success(self):
        return self.error is None

    def merge(self, new_attributes):
        for k, v in new_attributes.items():
            setattr(self, k, v)

    def convert(self, name, value):
        """
        Convert attributes to our Resource subclass
        :param name:
        :param value:
        :return:
        """
        if isinstance(value, dict):
            if name == 'data':
                cls = self.convert_resources.get(str(self.headers['resource']), Resource)
            else:
                cls = self.convert_resources.get(name, Resource)
            return cls(value, api=self.api)
        elif isinstance(value, list):
            new_list = []
            for obj in value:
                new_list.append(self.convert(name, obj))
            return new_list
        else:
            return value

    def __getitem__(self, key):
        return self.__data__[key]

    def __setitem__(self, key, value):
        self.__data__[key] = self.convert(key, value)

    def to_dict(self):

        def parse_object(value):
            if isinstance(value, Resource):
                return value.to_dict()
            elif isinstance(value, list):
                new_list = []
                for obj in value:
                    new_list.append(parse_object(obj))
                return new_list
            else:
                return value

        data = {}
        for key in self.__data__:
            data[key] = parse_object(self.__data__[key])
        return data


class One(Resource):
    one_class = Resource

    @classmethod
    def one(cls, resource_id=None, api=None):
        """
        One (by id)
        """
        api = api or default_api()

        if resource_id is None:
            url = tools.merge_url(cls.path)
        else:
            url = tools.merge_url(cls.path, str(resource_id))

        headers = tools.merge_dict({'resource': cls.resource, 'method': 'GET'})

        response = api.get(url, headers=headers)
        return cls.one_class(response, api=api, headers=headers)


class List(Resource):
    list_class = Resource

    @classmethod
    def list(cls, params=None, api=None):
        """
        List a resource
        """
        api = api or default_api()

        if params is None:
            url = cls.path
        else:
            url = tools.join_url_params(cls.path, params)

        headers = tools.merge_dict({'resource': cls.resource, 'method': 'GET'})
        response = api.get(url, headers=headers)
        return cls.list_class(response, api=api, headers=headers)


class Create(Resource):
    def create(self, refresh_token=None, correlation_id=None):
        """
        Create
        """

        headers = {}
        if correlation_id is not None:
            headers = tools.merge_dict(
                self.make_headers(),
                {'Predikto-Application-Correlation-Id': correlation_id, 'Predikto-Client-Metadata-Id': correlation_id}
            )
        else:
            headers = self.make_headers()

        new_attributes = self.api.post(self.path, self.to_dict(), headers, refresh_token)
        self.error = None
        self.merge(new_attributes)
        return self.success()


class Update(Resource):
    """
    Update
    """

    def update(self, attributes=None, refresh_token=None):
        attributes = attributes or self.to_dict()
        url = tools.merge_url(self.path, str(self['id']))
        new_attributes = self.api.put(url, attributes, self.make_headers(), refresh_token)
        self.error = None
        self.merge(new_attributes)
        return self.success()


class Delete(Resource):
    def delete(self):
        """
        Delete
        """
        url = tools.merge_url(self.path, str(self['id']))
        new_attributes = self.api.delete(url)
        self.error = None
        self.merge(new_attributes)
        return self.success()


class S3Upload(Resource):
    """
    S3Upload
    """

    def s3upload(bucket_name=None, file_path=None):
        import predikto
        import requests

        res = predikto.Upload.one(bucket_name)
        upload = res.data[0]

        files = {'file': open(file_path, 'rb')}
        response = requests.request('POST', upload.post_url, files=files,
                                    data={"key": upload.key, "signature": upload.signature,
                                          "policy": upload.policy,
                                          "bucket": upload.bucket.lower(), "AWSAccessKeyId": upload.AWSAccessKeyId
                                          }, headers={"x-amz-acl": "authenticated-read"})
        return response


class Post(Resource):
    def post(self, name, attributes=None, cls=Resource, fieldname='id'):
        """
        Raw post to url with headers
        Usage::
            >>> status.post("execute", {'some_id': '1234'}, status)
        """
        attributes = attributes or {}
        url = tools.merge_url(self.path, str(self[fieldname]), name)
        if not isinstance(attributes, Resource):
            attributes = Resource(attributes, api=self.api)
        new_attributes = self.api.post(url, attributes.to_dict(), attributes.make_headers())
        if isinstance(cls, Resource):
            cls.error = None
            cls.merge(new_attributes)
            return self.success()
        else:
            return cls(new_attributes, api=self.api)
