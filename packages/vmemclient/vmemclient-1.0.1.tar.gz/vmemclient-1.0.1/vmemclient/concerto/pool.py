#!/usr/bin/env python

"""
Copyright 2015 Violin Memory, Inc..

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

from vmemclient.core import error
from vmemclient.core import restobject


class PoolManager01(restobject.SessionNamespace):
    _STORAGE_POOL_BASE_PATH = '/physicalresource/storagepool'

    def get_storage_pools(self):
        """Gets the storage pools.

        Returns:
            list

        """
        ans = self.parent.basic.get(self._STORAGE_POOL_BASE_PATH)
        if not ans['success']:
            raise error.QueryError('Failed to get storage pools')
        try:
            return [x for x in ans['data']['storage_pools']
                    if x['object_id']]
        except (KeyError, AttributeError):
            return []

    def storage_pool_name_to_object_id(self, name):
        """Finds the object_id for the given storage pool.

        Arguments:
            name -- string

        Returns:
            string

        Raises:
            error.QueryError
            error.NoMatchingObjectIdError

        """
        name = str(name)

        # Raises: QueryError
        ans = self.get_storage_pools()

        # Find the object_id
        for pool in ans:
            if pool['name'] == name:
                return pool['object_id']
        raise error.NoMatchingObjectIdError(name)

    def get_storage_pool_info(self, name=None, object_id=None):
        """Gets detailed info on the specified client object_id.

        Arguments:
            name      -- string
            object_id -- string

        Returns:
            dict

        Raises:
            error.QueryError
            error.NoMatchingObjectIdError

        """
        # Determine the object_id
        if object_id is None:
            # Raises: QueryError, NoMatchingObjectIdError
            object_id = self.storage_pool_name_to_object_id(name)

        # Get the storage pool info
        location = '{0}/{1}'.format(self._STORAGE_POOL_BASE_PATH, object_id)
        ans = self.parent.basic.get(location)
        if not ans['success']:
            raise error.QueryError(ans.get('msg', str(ans)))

        return ans['data']
