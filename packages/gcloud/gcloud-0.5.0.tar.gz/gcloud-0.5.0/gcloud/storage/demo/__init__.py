# Copyright 2014 Google Inc. All rights reserved.
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

import os
from gcloud import storage

__all__ = ['create_bucket', 'list_buckets', 'PROJECT_ID']

PROJECT_ID = os.getenv('GCLOUD_TESTS_PROJECT_ID')


def list_buckets(connection):
    return list(storage.list_buckets(project=PROJECT_ID,
                                     connection=connection))


def create_bucket(bucket_name, connection):
    return storage.create_bucket(bucket_name, PROJECT_ID,
                                 connection=connection)
