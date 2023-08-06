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


class FormatManager01(restobject.SessionNamespace):
    def format_array(self, percentage, volumeid=None):
        """Format the array.

        Arguments:
            percentage -- uint8
            volumeid   -- uint32

        """

        nodes = []
        nodes.append(XGNode('percentage', 'uint8', percentage))
        if volumeid:
            nodes.append(XGNode('volumeid', 'uint32', volumeid))

        return self.parent.basic.perform_action('/array/actions' +
                                                '/format', nodes)
