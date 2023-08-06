# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Methods for interacting with Google Cloud Storage.

Allows interacting with Cloud Storage via user-friendly objects
rather than via Connection.
"""

from gcloud.exceptions import NotFound
from gcloud.storage._implicit_environ import get_default_connection
from gcloud.storage.bucket import Bucket
from gcloud.storage.iterator import Iterator


def lookup_bucket(bucket_name, connection=None):
    """Get a bucket by name, returning None if not found.

    You can use this if you would rather checking for a None value
    than catching an exception::

      >>> from gcloud import storage
      >>> storage.set_defaults()
      >>> bucket = storage.lookup_bucket('doesnt-exist')
      >>> print bucket
      None
      >>> bucket = storage.lookup_bucket('my-bucket')
      >>> print bucket
      <Bucket: my-bucket>

    :type bucket_name: string
    :param bucket_name: The name of the bucket to get.

    :type connection: :class:`gcloud.storage.connection.Connection` or
                      ``NoneType``
    :param connection: Optional. The connection to use when sending requests.
                       If not provided, falls back to default.

    :rtype: :class:`gcloud.storage.bucket.Bucket`
    :returns: The bucket matching the name provided or None if not found.
    """
    if connection is None:
        connection = get_default_connection()

    try:
        return get_bucket(bucket_name, connection=connection)
    except NotFound:
        return None


def get_all_buckets(connection=None):
    """Get all buckets in the project.

    This will not populate the list of blobs available in each
    bucket.

      >>> from gcloud import storage
      >>> for bucket in storage.get_all_buckets():
      >>>   print bucket

    This implements "storage.buckets.list".

    :type connection: :class:`gcloud.storage.connection.Connection` or
                      ``NoneType``
    :param connection: Optional. The connection to use when sending requests.
                       If not provided, falls back to default.

    :rtype: iterable of :class:`gcloud.storage.bucket.Bucket` objects.
    :returns: All buckets belonging to this project.
    """
    if connection is None:
        connection = get_default_connection()
    return iter(_BucketIterator(connection=connection))


def get_bucket(bucket_name, connection=None):
    """Get a bucket by name.

    If the bucket isn't found, this will raise a
    :class:`gcloud.storage.exceptions.NotFound`.

    For example::

      >>> from gcloud import storage
      >>> from gcloud.exceptions import NotFound
      >>> try:
      >>>   bucket = storage.get_bucket('my-bucket')
      >>> except NotFound:
      >>>   print 'Sorry, that bucket does not exist!'

    This implements "storage.buckets.get".

    :type bucket_name: string
    :param bucket_name: The name of the bucket to get.

    :type connection: :class:`gcloud.storage.connection.Connection` or
                      ``NoneType``
    :param connection: Optional. The connection to use when sending requests.
                       If not provided, falls back to default.

    :rtype: :class:`gcloud.storage.bucket.Bucket`
    :returns: The bucket matching the name provided.
    :raises: :class:`gcloud.exceptions.NotFound`
    """
    if connection is None:
        connection = get_default_connection()

    bucket_path = Bucket.path_helper(bucket_name)
    response = connection.api_request(method='GET', path=bucket_path)
    return Bucket(properties=response, connection=connection)


def create_bucket(bucket_name, connection=None):
    """Create a new bucket.

    For example::

      >>> from gcloud import storage
      >>> storage.set_defaults()
      >>> bucket = storage.create_bucket('my-bucket')
      >>> print bucket
      <Bucket: my-bucket>

    This implements "storage.buckets.insert".

    :type bucket_name: string
    :param bucket_name: The bucket name to create.

    :type connection: :class:`gcloud.storage.connection.Connection` or
                      ``NoneType``
    :param connection: Optional. The connection to use when sending requests.
                       If not provided, falls back to default.

    :rtype: :class:`gcloud.storage.bucket.Bucket`
    :returns: The newly created bucket.
    :raises: :class:`gcloud.exceptions.Conflict` if
             there is a confict (bucket already exists, invalid name, etc.)
    """
    if connection is None:
        connection = get_default_connection()

    response = connection.api_request(method='POST', path='/b',
                                      data={'name': bucket_name})
    return Bucket(properties=response, connection=connection)


class _BucketIterator(Iterator):
    """An iterator listing all buckets.

    You shouldn't have to use this directly, but instead should use the
    helper methods on :class:`gcloud.storage.connection.Connection`
    objects.

    :type connection: :class:`gcloud.storage.connection.Connection`
    :param connection: The connection to use for querying the list of buckets.
    """

    def __init__(self, connection):
        super(_BucketIterator, self).__init__(connection=connection, path='/b')

    def get_items_from_response(self, response):
        """Factory method which yields :class:`.Bucket` items from a response.

        :type response: dict
        :param response: The JSON API response for a page of buckets.
        """
        for item in response.get('items', []):
            yield Bucket(properties=item, connection=self.connection)
