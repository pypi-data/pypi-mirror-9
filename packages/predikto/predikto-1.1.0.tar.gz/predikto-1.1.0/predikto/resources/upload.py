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
from predikto.resources.base import One, S3Upload, List


class Upload(One, S3Upload):
    """
    Upload class wrapping the REST /upload endpoint. Upload.one() fetches the params needed to complete the upload in S3Upload

    Usage::

        >>> upload_upload = Upload.s3upload(<bucket_name>, <file_path>)
        >>> upload_one = Upload.one()
    """
    path = "/upload"
    resource = "upload"


Upload.convert_resources['upload'] = Upload


class Bucket(List):
    """
    Lists current buckets that accept uploads... Upload Locations.

    Usage::

        >>> bucket_list = Bucket.list()
    """
    path = "/buckets"
    resource = "buckets"


Upload.convert_resources['upload'] = Upload
Bucket.convert_resources['buckets'] = Bucket