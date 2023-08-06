#!/usr/bin/env python

"""
Copyright 2014 - 2015 Violin Memory, Inc..

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


class LUNManager01(restobject.SessionNamespace):
    _LUN_BASE_PATH = '/logicalresource/sanresource'

    def get_luns(self):
        """Gets the LUN listing.

        Returns:
            list of dicts

        Raises:
            error.QueryError

        """
        ans = self.parent.basic.get(self._LUN_BASE_PATH)
        if not ans['success']:
            raise error.QueryError('Failed to get LUN listing')

        try:
            return [x for x in ans['data']['virtual_devices']
                    if x['type'] == 'SAN']
        except (KeyError, AttributeError):
            return []

    def lun_name_to_object_id(self, name):
        """Finds the object_id for the given LUN name.

        Arguments:
            name -- string

        Returns:
            string

        Raises:
            error.QueryError
            error.NoMatchingObjectIdError

        """
        name = str(name)
        # Raises:  QueryError
        ans = self.get_luns()
        for lun in ans:
            if lun['name'] == name:
                return lun['object_id']
        raise error.NoMatchingObjectIdError(name)

    def get_lun_info(self, name=None, object_id=None):
        """Gets detailed info on the specified LUN.

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
            # Raises:  QueryError, NoMatchingObjectIdError
            object_id = self.lun_name_to_object_id(name)

        # Get the LUN info
        location = '{0}/{1}'.format(self._LUN_BASE_PATH, object_id)
        ans = self.parent.basic.get(location)
        if not ans['success']:
            raise error.QueryError(ans.get('msg', str(ans)))

        return ans['data']

    def create_lun(self, name=None, size=None, dedup=None,
                   thin=None, full_size=None):
        """Creates a LUN.

        Arguments:
            name      -- string
            size      -- int
            dedup     -- bool
            thin      -- bool (optional)
            full_size -- int (optional)

        Returns:
            dict

        """
        # Constants
        BASE_KEY = 'params'
        THIN_PATH = 'thinProvisioning'

        # Build request
        location = self._LUN_BASE_PATH
        args = ()
        args += (((BASE_KEY,), 'name', name, 'str'),)
        args += (((BASE_KEY,), 'sizeMB', size, 'int'),)
        args += (((BASE_KEY,), 'dedup', dedup, 'bool'),)
        args += (((BASE_KEY, THIN_PATH), 'enabled', thin, 'bool'),)
        args += (((BASE_KEY, THIN_PATH), 'fullSizeMB', full_size, 'int'),)
        data = self.parent.build_request_data(args)

        # Send request
        return self.parent.basic.post(location, data)

    def rename_lun(self, name=None, new_name=None, object_id=None):
        """Renames a LUN.

        If the object_id is not given, then find it by finding the LUN with
        the name <name>.

        Arguments:
            name      -- string
            new_name  -- string
            object_id -- string (optional)

        Returns:
            dict

        Raises:
            error.QueryError
            error.NoMatchingObjectIdError

        """
        # Constants
        BASE_KEY = 'params'

        # Determine object_id
        if object_id is None:
            # Raises:  QueryError, NoMatchingObjectIdError
            object_id = self.lun_name_to_object_id(name)

        # Build request
        location = '{0}/{1}'.format(self._LUN_BASE_PATH, object_id)
        args = ()
        args += (((BASE_KEY,), 'action', 'update', 'str'),)
        args += (((BASE_KEY,), 'name', new_name, 'str'),)
        data = self.parent.build_request_data(args)

        # Send request
        return self.parent.basic.put(location, data)

    def delete_lun(self, name=None, force=None, object_id=None):
        """Delete's the specified LUN.

        If the object_id is given, use that.  Otherwise, use the LUN name
        to find the appropriate object_id.

        Arguments:
            name      -- string
            force     -- bool
            object_id -- string

        Returns:
            dict

        Raises:
            error.QueryError
            error.NoMatchingObjectIdError

        """
        # Determine object_id
        if object_id is None:
            # Raises:  QueryError, NoMatchingObjectIdError
            object_id = self.lun_name_to_object_id(name)

        # Send request
        location = '{0}/{1}'.format(self._LUN_BASE_PATH, object_id)
        args = ()
        args += (((), 'force', force, 'bool'),)
        data = self.parent.build_request_data(args)

        # Send request
        return self.parent.basic.delete(location, data)

    def _modify_lun_size_using(self, action, name, size, object_id):
        """Internal function for:

            extend_lun
            add_storage_to_lun

        """
        # Constants
        BASE_KEY = 'params'

        # Determine object_id
        if object_id is None:
            # Raises:  QueryError, NoMatchingObjectIdError
            object_id = self.lun_name_to_object_id(name)

        # Sanitize input
        size = 0 if size is None else int(size)

        # Build the request
        location = '{0}/{1}'.format(self._LUN_BASE_PATH, object_id)
        args = ()
        args += (((BASE_KEY,), 'action', action, 'str'),)
        args += (((BASE_KEY,), 'sizeMB', size, 'int'),)
        data = self.parent.build_request_data(args)

        # Send the request
        return self.parent.basic.put(location, data)

    def extend_lun(self, name=None, size=None, object_id=None):
        """Extends the LUN by 'size' MB.

        If the object_id is given, use that.  Otherwise, use the LUN name
        to find the appropriate object_id.

        Arguments:
            name      -- string
            size      -- int
            object_id -- string

        Returns:
            dict

        Raises:
            error.QueryError
            error.NoMatchingObjectIdError

        """
        return self._modify_lun_size_using('expand', name, size, object_id)

    def add_storage_to_lun(self, name=None, size=None, object_id=None):
        """Adds 'size' MB to the LUN's allocated size.

        If the object_id is given, use that.  Otherwise, use the LUN name
        to find the appropriate object_id.

        Arguments:
            name      -- string
            size      -- int
            object_id -- string

        Returns:
            dict

        Raises:
            error.QueryError
            error.NoMatchingObjectIdError

        """
        return self._modify_lun_size_using('addstorage', name, size, object_id)

    def assign_lun_to_client(self, lun_name=None, client_name=None,
                             mode=None, lun_id=None,
                             mg_wwn=None, client_wwn=None,
                             lun_object_id=None, client_object_id=None):
        """Exports a LUN to a FC client.

        Arguments:
            lun_name         -- string
            client_name      -- string
            mode             -- string
            lun_id           -- int
            mg_wwn           -- string
            client_wwn       -- string
            lun_object_id    -- string
            client_object_id -- string

        Returns:
            dict

        Raises:
            error.QueryError
            error.NoMatchingObjectIdError

        """
        # Constants
        BASE_KEY = 'params'
        FC_KEY = 'FC'
        ID_FIELD = 'sanclient_id'

        # Determine all object IDs
        if lun_object_id is None:
            # Raises:  QueryError, NoMatchingObjectIdError
            lun_object_id = self.lun_name_to_object_id(lun_name)
        if client_object_id is None:
            # Raises:  QueryError, NoMatchingObjectIdError
            client_object_id = self.parent.client.client_name_to_object_id(
                    client_name)

        # Build request
        location = '{0}/{1}'.format(self.parent.client._CLIENT_BASE_PATH,
                                    client_object_id)
        args = ()
        args += (((BASE_KEY,), 'action', 'assign', 'str'),)
        args += (((BASE_KEY,), 'virtualDeviceObjectID', lun_object_id, 'str'),)
        args += (((BASE_KEY, FC_KEY,), 'lun', lun_id, 'int'),)
        args += (((BASE_KEY, FC_KEY,), 'initiatorWWPN', client_wwn, 'str'),)
        args += (((BASE_KEY, FC_KEY,), 'targetWWPN', mg_wwn, 'str'),)
        args += (((BASE_KEY, FC_KEY,), 'accessMode', mode, 'str'),)
        data = self.parent.build_request_data(args)

        # Send request
        return self.parent.basic.put(location, data)

    def unassign_client_lun(self, lun_name=None, client_name=None,
                            force=None, no_group=None,
                            lun_object_id=None, client_object_id=None):
        """Unexport the LUN from the given client.

        Arguments:
            lun_name         -- string
            client_name      -- string
            force            -- bool
            no_group         -- bool
            lun_object_id    -- string
            client_object_id -- string

        Returns:
            dict

        Raises:
            error.QueryError
            error.NoMatchingObjectIdError

        """
        # Constants
        BASE_KEY = 'params'

        # Determine all object IDs
        if lun_object_id is None:
            # Raises:  QueryError, NoMatchingObjectIdError
            lun_object_id = self.lun_name_to_object_id(lun_name)
        if client_object_id is None:
            # Raises:  QueryError, NoMatchingObjectIdError
            client_object_id = self.parent.client.client_name_to_object_id(
                    client_name)

        # Build request
        location = '{0}/{1}'.format(self.parent.client._CLIENT_BASE_PATH,
                                    client_object_id)
        args = ()
        args += (((BASE_KEY,), 'action', 'unassign', 'str'),)
        args += (((BASE_KEY,), 'virtualDeviceObjectID', lun_object_id, 'str'),)
        args += (((BASE_KEY,), 'force', force, 'bool'),)
        args += (((BASE_KEY,), 'noGroupClientAssignment', no_group, 'bool'),)
        data = self.parent.build_request_data(args)

        # Send request
        return self.parent.basic.put(location, data)
