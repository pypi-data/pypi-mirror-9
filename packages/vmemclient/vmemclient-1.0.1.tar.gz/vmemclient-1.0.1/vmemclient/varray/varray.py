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

from vmemclient.core.restobject import RestObject
from vmemclient.varray import format as FORMAT
from vmemclient.varray import vcm as VCM


CLASS_NAMES = 'VArray'


class VArray01(RestObject):
    object_type = 'tallmaple-acm'
    _versions = '5.1.0'

    def __init__(self, session, version_info):
        super(VArray01, self).__init__(session, version_info)
        self.format = FORMAT.FormatManager01(self)
        self.vcm = VCM.VCMManager01(self)

    @property
    def version(self):
        return self._version_info['type'] + self._version_info['version']
