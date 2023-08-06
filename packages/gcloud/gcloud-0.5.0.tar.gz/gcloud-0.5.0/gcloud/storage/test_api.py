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

import unittest2


class Test_lookup_bucket(unittest2.TestCase):

    def _callFUT(self, bucket_name, connection=None):
        from gcloud.storage.api import lookup_bucket
        return lookup_bucket(bucket_name, connection=connection)

    def test_miss(self):
        from gcloud.storage.connection import Connection
        NONESUCH = 'nonesuch'
        conn = Connection()
        URI = '/'.join([
            conn.API_BASE_URL,
            'storage',
            conn.API_VERSION,
            'b',
            'nonesuch?projection=noAcl',
        ])
        http = conn._http = Http(
            {'status': '404', 'content-type': 'application/json'},
            b'{}',
        )
        bucket = self._callFUT(NONESUCH, connection=conn)
        self.assertEqual(bucket, None)
        self.assertEqual(http._called_with['method'], 'GET')
        self.assertEqual(http._called_with['uri'], URI)

    def _lookup_bucket_hit_helper(self, use_default=False):
        from gcloud.storage._testing import _monkey_defaults
        from gcloud.storage.bucket import Bucket
        from gcloud.storage.connection import Connection
        BLOB_NAME = 'blob-name'
        conn = Connection()
        URI = '/'.join([
            conn.API_BASE_URL,
            'storage',
            conn.API_VERSION,
            'b',
            '%s?projection=noAcl' % (BLOB_NAME,),
        ])
        http = conn._http = Http(
            {'status': '200', 'content-type': 'application/json'},
            '{{"name": "{0}"}}'.format(BLOB_NAME).encode('utf-8'),
        )

        if use_default:
            with _monkey_defaults(connection=conn):
                bucket = self._callFUT(BLOB_NAME)
        else:
            bucket = self._callFUT(BLOB_NAME, connection=conn)

        self.assertTrue(isinstance(bucket, Bucket))
        self.assertTrue(bucket.connection is conn)
        self.assertEqual(bucket.name, BLOB_NAME)
        self.assertEqual(http._called_with['method'], 'GET')
        self.assertEqual(http._called_with['uri'], URI)

    def test_hit(self):
        self._lookup_bucket_hit_helper(use_default=False)

    def test_use_default(self):
        self._lookup_bucket_hit_helper(use_default=True)


class Test_list_buckets(unittest2.TestCase):

    def _callFUT(self, *args, **kwargs):
        from gcloud.storage.api import list_buckets
        return list_buckets(*args, **kwargs)

    def test_empty(self):
        from six.moves.urllib.parse import parse_qs
        from six.moves.urllib.parse import urlparse
        from gcloud.storage.connection import Connection
        PROJECT = 'project'
        conn = Connection()
        EXPECTED_QUERY = {
            'project': [PROJECT],
            'projection': ['noAcl'],
        }
        http = conn._http = Http(
            {'status': '200', 'content-type': 'application/json'},
            b'{}',
        )
        buckets = list(self._callFUT(project=PROJECT, connection=conn))
        self.assertEqual(len(buckets), 0)
        self.assertEqual(http._called_with['method'], 'GET')
        self.assertEqual(http._called_with['body'], None)

        BASE_URI = '/'.join([
            conn.API_BASE_URL,
            'storage',
            conn.API_VERSION,
            'b',
        ])
        URI = http._called_with['uri']
        self.assertTrue(URI.startswith(BASE_URI))
        uri_parts = urlparse(URI)
        self.assertEqual(parse_qs(uri_parts.query), EXPECTED_QUERY)

    def _list_buckets_non_empty_helper(self, project, use_default=False):
        from six.moves.urllib.parse import urlencode
        from gcloud._testing import _monkey_defaults as _base_monkey_defaults
        from gcloud.storage._testing import _monkey_defaults
        from gcloud.storage.connection import Connection
        BUCKET_NAME = 'bucket-name'
        conn = Connection()
        query_params = urlencode({'project': project, 'projection': 'noAcl'})
        URI = '/'.join([
            conn.API_BASE_URL,
            'storage',
            conn.API_VERSION,
            'b?%s' % (query_params,),
        ])
        http = conn._http = Http(
            {'status': '200', 'content-type': 'application/json'},
            '{{"items": [{{"name": "{0}"}}]}}'.format(BUCKET_NAME)
            .encode('utf-8'),
        )

        if use_default:
            with _base_monkey_defaults(project=project):
                with _monkey_defaults(connection=conn):
                    buckets = list(self._callFUT())
        else:
            buckets = list(self._callFUT(project=project, connection=conn))

        self.assertEqual(len(buckets), 1)
        self.assertEqual(buckets[0].name, BUCKET_NAME)
        self.assertEqual(http._called_with['method'], 'GET')
        self.assertEqual(http._called_with['uri'], URI)

    def test_non_empty(self):
        self._list_buckets_non_empty_helper('PROJECT', use_default=False)

    def test_non_use_default(self):
        self._list_buckets_non_empty_helper('PROJECT', use_default=True)

    def test_all_arguments(self):
        from six.moves.urllib.parse import parse_qs
        from six.moves.urllib.parse import urlparse
        from gcloud.storage.connection import Connection
        PROJECT = 'foo-bar'
        MAX_RESULTS = 10
        PAGE_TOKEN = 'ABCD'
        PREFIX = 'subfolder'
        PROJECTION = 'full'
        FIELDS = 'items/id,nextPageToken'
        EXPECTED_QUERY = {
            'project': [PROJECT],
            'maxResults': [str(MAX_RESULTS)],
            'pageToken': [PAGE_TOKEN],
            'prefix': [PREFIX],
            'projection': [PROJECTION],
            'fields': [FIELDS],
        }
        CONNECTION = Connection()
        http = CONNECTION._http = Http(
            {'status': '200', 'content-type': 'application/json'},
            '{"items": []}',
        )
        iterator = self._callFUT(
            project=PROJECT,
            max_results=MAX_RESULTS,
            page_token=PAGE_TOKEN,
            prefix=PREFIX,
            projection=PROJECTION,
            fields=FIELDS,
            connection=CONNECTION,
        )
        buckets = list(iterator)
        self.assertEqual(buckets, [])
        self.assertEqual(http._called_with['method'], 'GET')
        self.assertEqual(http._called_with['body'], None)

        BASE_URI = '/'.join([
            CONNECTION.API_BASE_URL,
            'storage',
            CONNECTION.API_VERSION,
            'b'
        ])
        URI = http._called_with['uri']
        self.assertTrue(URI.startswith(BASE_URI))
        uri_parts = urlparse(URI)
        self.assertEqual(parse_qs(uri_parts.query), EXPECTED_QUERY)


class Test_get_bucket(unittest2.TestCase):

    def _callFUT(self, bucket_name, connection=None):
        from gcloud.storage.api import get_bucket
        return get_bucket(bucket_name, connection=connection)

    def test_miss(self):
        from gcloud.exceptions import NotFound
        from gcloud.storage.connection import Connection
        NONESUCH = 'nonesuch'
        conn = Connection()
        URI = '/'.join([
            conn.API_BASE_URL,
            'storage',
            conn.API_VERSION,
            'b',
            'nonesuch?projection=noAcl',
        ])
        http = conn._http = Http(
            {'status': '404', 'content-type': 'application/json'},
            b'{}',
        )
        self.assertRaises(NotFound, self._callFUT, NONESUCH, connection=conn)
        self.assertEqual(http._called_with['method'], 'GET')
        self.assertEqual(http._called_with['uri'], URI)

    def _get_bucket_hit_helper(self, use_default=False):
        from gcloud.storage._testing import _monkey_defaults
        from gcloud.storage.bucket import Bucket
        from gcloud.storage.connection import Connection
        BLOB_NAME = 'blob-name'
        conn = Connection()
        URI = '/'.join([
            conn.API_BASE_URL,
            'storage',
            conn.API_VERSION,
            'b',
            '%s?projection=noAcl' % (BLOB_NAME,),
        ])
        http = conn._http = Http(
            {'status': '200', 'content-type': 'application/json'},
            '{{"name": "{0}"}}'.format(BLOB_NAME).encode('utf-8'),
        )

        if use_default:
            with _monkey_defaults(connection=conn):
                bucket = self._callFUT(BLOB_NAME)
        else:
            bucket = self._callFUT(BLOB_NAME, connection=conn)

        self.assertTrue(isinstance(bucket, Bucket))
        self.assertTrue(bucket.connection is conn)
        self.assertEqual(bucket.name, BLOB_NAME)
        self.assertEqual(http._called_with['method'], 'GET')
        self.assertEqual(http._called_with['uri'], URI)

    def test_hit(self):
        self._get_bucket_hit_helper(use_default=False)

    def test_hit_use_default(self):
        self._get_bucket_hit_helper(use_default=True)


class Test_create_bucket(unittest2.TestCase):

    def _callFUT(self, bucket_name, project=None, connection=None):
        from gcloud.storage.api import create_bucket
        return create_bucket(bucket_name, project=project,
                             connection=connection)

    def _create_bucket_success_helper(self, project, use_default=False):
        from gcloud._testing import _monkey_defaults as _base_monkey_defaults
        from gcloud.storage._testing import _monkey_defaults
        from gcloud.storage.connection import Connection
        from gcloud.storage.bucket import Bucket
        BLOB_NAME = 'blob-name'
        conn = Connection()
        URI = '/'.join([
            conn.API_BASE_URL,
            'storage',
            conn.API_VERSION,
            'b?project=%s' % project,
            ])
        http = conn._http = Http(
            {'status': '200', 'content-type': 'application/json'},
            '{{"name": "{0}"}}'.format(BLOB_NAME).encode('utf-8'),
        )

        if use_default:
            with _base_monkey_defaults(project=project):
                with _monkey_defaults(connection=conn):
                    bucket = self._callFUT(BLOB_NAME)
        else:
            bucket = self._callFUT(BLOB_NAME, project=project, connection=conn)

        self.assertTrue(isinstance(bucket, Bucket))
        self.assertTrue(bucket.connection is conn)
        self.assertEqual(bucket.name, BLOB_NAME)
        self.assertEqual(http._called_with['method'], 'POST')
        self.assertEqual(http._called_with['uri'], URI)

    def test_success(self):
        self._create_bucket_success_helper('PROJECT', use_default=False)

    def test_success_use_default(self):
        self._create_bucket_success_helper('PROJECT', use_default=True)


class Test__BucketIterator(unittest2.TestCase):

    def _getTargetClass(self):
        from gcloud.storage.api import _BucketIterator
        return _BucketIterator

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor(self):
        connection = object()
        iterator = self._makeOne(connection)
        self.assertTrue(iterator.connection is connection)
        self.assertEqual(iterator.path, '/b')
        self.assertEqual(iterator.page_number, 0)
        self.assertEqual(iterator.next_page_token, None)

    def test_get_items_from_response_empty(self):
        connection = object()
        iterator = self._makeOne(connection)
        self.assertEqual(list(iterator.get_items_from_response({})), [])

    def test_get_items_from_response_non_empty(self):
        from gcloud.storage.bucket import Bucket
        BLOB_NAME = 'blob-name'
        response = {'items': [{'name': BLOB_NAME}]}
        connection = object()
        iterator = self._makeOne(connection)
        buckets = list(iterator.get_items_from_response(response))
        self.assertEqual(len(buckets), 1)
        bucket = buckets[0]
        self.assertTrue(isinstance(bucket, Bucket))
        self.assertTrue(bucket.connection is connection)
        self.assertEqual(bucket.name, BLOB_NAME)


class Test__require_connection(unittest2.TestCase):

    def _callFUT(self, connection=None):
        from gcloud.storage.api import _require_connection
        return _require_connection(connection=connection)

    def _monkey(self, connection):
        from gcloud.storage._testing import _monkey_defaults
        return _monkey_defaults(connection=connection)

    def test_implicit_unset(self):
        with self._monkey(None):
            with self.assertRaises(EnvironmentError):
                self._callFUT()

    def test_implicit_unset_w_existing_batch(self):
        CONNECTION = object()
        with self._monkey(None):
            with _NoCommitBatch(connection=CONNECTION):
                self.assertEqual(self._callFUT(), CONNECTION)

    def test_implicit_unset_passed_explicitly(self):
        CONNECTION = object()
        with self._monkey(None):
            self.assertTrue(self._callFUT(CONNECTION) is CONNECTION)

    def test_implicit_set(self):
        IMPLICIT_CONNECTION = object()
        with self._monkey(IMPLICIT_CONNECTION):
            self.assertTrue(self._callFUT() is IMPLICIT_CONNECTION)

    def test_implicit_set_passed_explicitly(self):
        IMPLICIT_CONNECTION = object()
        CONNECTION = object()
        with self._monkey(IMPLICIT_CONNECTION):
            self.assertTrue(self._callFUT(CONNECTION) is CONNECTION)


class Http(object):

    _called_with = None

    def __init__(self, headers, content):
        from httplib2 import Response
        self._response = Response(headers)
        self._content = content

    def request(self, **kw):
        self._called_with = kw
        return self._response, self._content


class _NoCommitBatch(object):

    def __init__(self, connection):
        self._connection = connection

    def __enter__(self):
        from gcloud.storage.batch import _BATCHES
        _BATCHES.push(self._connection)
        return self._connection

    def __exit__(self, *args):
        from gcloud.storage.batch import _BATCHES
        _BATCHES.pop()
