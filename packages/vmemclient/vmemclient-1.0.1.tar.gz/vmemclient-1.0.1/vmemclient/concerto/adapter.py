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


class AdapterManager01(restobject.SessionNamespace):
    _ADAPTER_BASE_PATH = '/physicalresource/physicaladapter'

    def get_physical_adapters(self):
        """Gets the physical adapters.

        Returns:
            list of dicts

        Raises:
            error.QueryError

        """
        ans = self.parent.basic.get(self._ADAPTER_BASE_PATH)
        if not ans['success']:
            raise error.QueryError('Failed to get LUN listing')

        try:
            return ans['data']['physical_adapters']
        except (KeyError, AttributeError):
            return []

    def get_adapter_info(self, object_id):
        """Gets information about the given adapter.

        Arguments:
            object_id -- string

        Returns:
            dict

        Raises:
            error.QueryError

        """
        location = '{0}/{1}'.format(self._ADAPTER_BASE_PATH, object_id)
        ans = self.parent.basic.get(location)
        if not ans['success']:
            raise error.QueryError(ans.get('msg', str(ans)))

        return ans['data']

    def get_fc_info(self):
        """Gets FibreChannel object IDs and WWNs.

        The data is returned as a dict, with keys as the object_id of the
        adapter, and values as a list of WWNs associated with that adapter.

        Returns:
            dict

        Raises:
            error.QueryError

        """
        ans = {}

        # Find FC adapters
        # Raises:  QueryError
        for adapter in self.get_physical_adapters():
            if adapter['type'] == 'fc':
                info = self.get_adapter_info(adapter['object_id'])
                value = [x['name'] for x in info.get('alias_wwpn_list', [])]
                ans[adapter['object_id']] = value

        # Done
        return ans
