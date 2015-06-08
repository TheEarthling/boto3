# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from boto3.s3.transfer import S3Transfer
from boto3 import utils

from botocore.exceptions import ClientError

def inject_s3_transfer_methods(class_attributes, **kwargs):
    utils.inject_attribute(class_attributes, 'upload_file', upload_file)
    utils.inject_attribute(class_attributes, 'download_file', download_file)


def inject_bucket_load(class_attributes, **kwargs):
    utils.inject_attribute(class_attributes, 'load', bucket_load)


def bucket_load(self, *args, **kwargs):
    """Fake s3.Bucket.load method.

    This emulates a bucket load method such that you can use::

        bucket = s3.Bucket('foo')
        bucket.load()
        # Or even just:
        bucket.creation_date

    """
    # We can't actually get the bucket's attributes from a HeadBucket,
    # so we need to use a ListBuckets and search for our bucket.
    response = self.meta.client.list_buckets()
    for bucket_data in response['Buckets']:
        if bucket_data['Name'] == self.name:
            self.meta.data = bucket_data
            break
    else:
        raise ClientError({'Error': {'Code': '404', 'Message': 'NotFound'}},
                          'ListBuckets')


def upload_file(self, Filename, Bucket, Key, ExtraArgs=None,
                Callback=None, Config=None):
    transfer = S3Transfer(self, Config)
    return transfer.upload_file(
        filename=Filename, bucket=Bucket, key=Key,
        extra_args=ExtraArgs, callback=Callback)


def download_file(self, Bucket, Key, Filename, ExtraArgs=None,
                  Callback=None, Config=None):
    transfer = S3Transfer(self, Config)
    return transfer.download_file(
        bucket=Bucket, key=Key, filename=Filename,
        extra_args=ExtraArgs, callback=Callback)
