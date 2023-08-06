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

from vmemclient.core.node import coerce_arg
from vmemclient.core.restobject import RestObject
from vmemclient.concerto import lun as LUN
from vmemclient.concerto import client as CLIENT
from vmemclient.concerto import adapter as ADAPTER
from vmemclient.concerto import snapshot as SNAPSHOT
from vmemclient.concerto import pool as POOL


CLASS_NAMES = 'Concerto'


class Concerto01(RestObject):
    object_type = 'concerto'
    _versions = ['7.50.0000', '7.0.0.0000']

    def __init__(self, session, version_info):
        super(Concerto01, self).__init__(session, version_info)
        self.lun = LUN.LUNManager01(self)
        self.pool = POOL.PoolManager01(self)
        self.client = CLIENT.ClientManager01(self)
        self.adapter = ADAPTER.AdapterManager01(self)
        self.snapshot = SNAPSHOT.SnapshotManager01(self)

    @property
    def version(self):
        return 'Version {concerto_version}, Build {build}'.format(
            **self._version_info)

    def build_request_data(self, argument_iterable):
        """Builds a request dict suitable for Concerto 7.x device types.

        Arguments are expected to be four or five element iterables where:
            0: iterable path (iterable of strings)
            1: key (string)
            2: value
            3: style (suitable for core.node.coerce_arg)
            4: allow None (bool, default: False; optional)

        Note:  None values are ommitted from the resulting dict, unless
        the "allow None" flag is set to True.

        Arguments:
            argument_iterable -- iterable

        Returns:
            dict

        Raises:
            ValueError

        """
        answer = {}

        # Build up the request
        for info in argument_iterable:
            if len(info) == 4:
                path, key, value, style = info
                allow_none = False
            else:
                # Raises: ValueError if info isn't of length 5
                path, key, value, style, allow_none = info

            if value is not None or allow_none:
                marker = answer
                for p in path:
                    marker.setdefault(p, {})
                    marker = marker[p]
                if value is None:
                    marker[key] = None
                else:
                    marker[key] = coerce_arg(value, style)

        # Done
        return answer
