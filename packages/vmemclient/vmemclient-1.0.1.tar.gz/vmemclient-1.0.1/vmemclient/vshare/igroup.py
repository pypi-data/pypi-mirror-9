#!/usr/bin/env python

"""
Copyright 2012 - 2015 Violin Memory, Inc..

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

from vmemclient.core import restobject
from vmemclient.core.node import XGNode
from vmemclient.core.error import *


class IGroupManager01(restobject.SessionNamespace):
    def create_igroup(self, igroup):
        """Create an igroup.

        Arguments:
            igroup -- string

        Returns:
            Action result as a dict.

        """
        return self._igroup_create(igroup, False)

    def delete_igroup(self, igroup):
        """Deletes an igroup.

        Arguments:
            igroup -- string

        Returns:
            Action result as a dict.

        """
        return self._igroup_create(igroup, True)

    def add_initiators(self, igroup, initiators):
        """Add initiators to an igroup.

        Arguments:
            igroup     -- string
            initiators -- string (string or list)

        Returns:
            Action result as a dict.

        """
        return self._igroup_modify(igroup, initiators, False)

    def delete_initiators(self, igroup, initiators):
        """Delete initiators to an igroup.

        Arguments:
            igroup     -- string
            initiators -- string (string or list)

        Returns:
            Action result as a dict.

        """
        return self._igroup_modify(igroup, initiators, True)

    # Begin internal functions

    def _igroup_create(self, igroup, delete):
        """Internal work function for:
            create_igroup
            delete_igroup

        """

        nodes = []
        nodes.append(XGNode('igroup', 'string', igroup))
        nodes.append(XGNode('delete', 'bool', delete))
        return self.parent.basic.perform_action('/vshare/actions' +
                                                '/igroup/create', nodes)

    def _igroup_modify(self, igroup, initiators, delete):
        """Internal work function for:
            add_initiators
            delete_initiators

        """
        nodes = []
        nodes.append(XGNode('igroup', 'string', igroup))
        nodes.extend(XGNode.as_node_list('initiators/{0}', 'string',
                                         initiators))
        nodes.append(XGNode('delete', 'bool', delete))

        return self.parent.basic.perform_action('/vshare/actions' +
                                                '/igroup/modify', nodes)


class IGroupManager02(IGroupManager01):
    def rename_igroup(self, old_igroup, new_igroup):
        """Renames an igroup.

        Arguments:
            old_igroup -- string
            new_igroup -- string

        Returns:
            Action result as a dict.

        """
        nodes = []
        nodes.append(XGNode('old_igroup', 'string', old_igroup))
        nodes.append(XGNode('new_igroup', 'string', new_igroup))

        return self.parent.basic.perform_action('/vshare/actions' +
                                                '/igroup/rename', nodes)
