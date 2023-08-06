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

import weakref

"""
[Naming of top-level objects and namespaces]

Changes between version A and B of a Violin appliance will necessitate a new
versioned namespace, and a new object that uses that updated namespace.  All
objects start with <identifier>01, and future objects should inherit from
that object and make changes as needed.

New support will be added with a new <feature>Manager01 class, which will
should be put in the appropriate object where that feature exists.

Updating support for an existing feature requires a few steps:
  1) Create a new <feature>Manager<num> class in the appropriate file.  The
     number to use is +1 the largest <feature>Manager<num> in that file.

     For example, if we're updating support for LUNs, and the highest Manager
     class in the file is LunManager04, then we should name our new
     class LunManager05:

        class LunManager05(LunManager04):
            ...

  2) Create a new top level object in the appropriate directory.  It should
     inherit from appropriate parent object (calling the parent's
     __init__() function), be +1 the largest top level object in that file,
     and then swap in the updated namespace.

     For our example, if the top level object is the VShare top level object,
     and the highest current VShare object is numbered 04, but the appropriate
     parent to inherit from is actually the VShare02 object, then we would
     define our new VShare object as so:

        class VShare05(VShare02):
            def __init__(self, ....):
                super(VShare05, self).__init__(....)
                self.lun = LUN.LunManager05(self)

  3) Finally, define the versions for which your new object is
     valid.  The "_versions" class constant, which can be either a basestring
     or a list of basestrings, such as '5.2.0', '6.3.1.4', or '7.50.8628'.

     For our example, if our new object is valid for VShare versions above
     6.3.5, then this would be our final VShare05 definition:

        class VShare05(VShare02):
            _versions = '6.3.5'

            def __init__(self, ....):
                super(VShare05, self).__init__(....)
                self.lun = LUN.LunManager05(self)

"""

class RestObject(object):
    """This class is the parent class for vmemclient.open() objects.

    """
    def __init__(self, session, version_info):
        self.basic = session
        self.close = self.basic.close
        self.open = self.basic.open
        self._version_info = version_info

    def __del__(self):
        """Close connections on object deletion.

        """
        try:
            self.basic.close()
        except Exception:
            pass

    def __enter__(self):
        """Implements: "with vmemclient.open(...) as foo:"

        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Closing context manager for: "with vmemclient.open(...) as foo:"

        """
        self.__del__()

    @property
    def debug(self):
        '''If debug messages are turned on or not.'''
        return self.basic.debug

    @debug.setter
    def debug(self, value):
        '''Update the debug setting.'''
        self.basic.debug = bool(value)

    @property
    def closed(self):
        '''If the connection is believed open or not.'''
        return self.basic.closed

    def __repr__(self):
        values = ['{0}'.format(self.__class__.__name__),
                  'host:{0}'.format(self.basic.host),
                  'user:{0}'.format(self.basic.user),
                  'password:{0}'.format(self.basic.password),
                  'proto:{0}'.format(self.basic.proto),
                  ]
        return '<{0}>'.format(' '.join(values))


class SessionNamespace(object):
    """Stores the parent object such that children namespaces can access it.

    """
    def __init__(self, parent):
        self._parent = weakref.ref(parent)

    @property
    def parent(self):
        return self._parent()
