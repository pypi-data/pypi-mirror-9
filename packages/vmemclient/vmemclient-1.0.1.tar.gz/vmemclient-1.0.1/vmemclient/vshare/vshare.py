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
from vmemclient.vshare import igroup as IGROUP
from vmemclient.vshare import iscsi as ISCSI
from vmemclient.vshare import lun as LUN
from vmemclient.vshare import snapshot as SNAPSHOT

CLASS_NAMES = 'VShare'


class VShare01(RestObject):
    object_type = 'tallmaple-mg'
    _versions = '5.0.2'

    def __init__(self, session, version_info):
        super(VShare01, self).__init__(session, version_info)
        self.basic = session
        self.lun = LUN.LUNManager01(self)

    @property
    def version(self):
        return self._version_info['type'] + self._version_info['version']


class VShare02(VShare01):
    _versions = '5.1.0'

    def __init__(self, session, version_info):
        super(VShare02, self).__init__(session, version_info)
        self.lun = LUN.LUNManager02(self)


class VShare03(VShare02):
    _versions = '5.2.0'

    def __init__(self, session, version_info):
        super(VShare03, self).__init__(session, version_info)
        self.lun = LUN.LUNManager03(self)
        self.igroup = IGROUP.IGroupManager01(self)
        self.iscsi = ISCSI.ISCSIManager01(self)


class VShare04(VShare03):
    _versions = '6.0.0'

    def __init__(self, session, version_info):
        super(VShare04, self).__init__(session, version_info)
        self.lun = LUN.LUNManager04(self)
        self.igroup = IGROUP.IGroupManager02(self)
        self.snapshot = SNAPSHOT.SnapshotManager01(self)

class VShare05(VShare04):
    _versions = '6.3.2.2'

    def __init__(self, session, version_info):
        super(VShare05, self).__init__(session, version_info)
        self.lun = LUN.LUNManager05(self)
