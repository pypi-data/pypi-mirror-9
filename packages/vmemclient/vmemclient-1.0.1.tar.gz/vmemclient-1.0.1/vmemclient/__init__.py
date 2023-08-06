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

import os
import sys
import inspect
import urllib2

# Set the path of vmemclient for child modules
_BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Get our library version
__version__ = 'unknown'
with open(os.path.join(_BASE_PATH, 'data', 'version.dat'), 'r') as fd:
    __version__ = fd.read().strip()

# Require python 2.6.0
# Use hexversion for arithmatic comparison versus major-minor-micro tuple
if sys.hexversion <= 0x02060000:
    raise ImportError('Requires python 2.6 or later ' +
                      '(running {0}.{1}.{2})'.format(*sys.version_info))


def open(host, user='admin', password='', proto='https',
         version=1, debug=False, http_fallback=True,
         keepalive=False, logger=None):
    """Opens up a REST connection with the given Violin appliance.

    This will first login to the given host, then access that host's version
    node registration.  Depending on what the host identifies itself as, an
    object compatible with that particular version will be returned.

    If there are any problems (such as auth failure or inaccessible hostname),
    then None will be returned.

    Arguments:
        host          -- Name or IP address of the host to connect to
        user          -- Username to login with
        password      -- Password for the user
        proto         -- Either 'http' or 'https'
        version       -- Reserved for future use
        debug         -- Enable/disable debugging to stdout (bool)
        http_fallback -- If proto is https and https fails, fallback to http
        keepalive     -- Attempt to reconnect on session loss
        logger        -- Where to send logs (default: sys.stdout)

    Returns:
        An authenticated REST connection to the appliance.  If there are any
        connection problems, then None is returned.

    """
    # Build up protocols to attempt
    protocols_to_try = []
    if proto.lower() == 'https':
        protocols_to_try.append('https')
    if proto.lower() == 'http' or http_fallback:
        protocols_to_try.append('http')

    # Verify the logger
    log_fd = None
    if logger is None:
        log_fd = sys.stdout
    elif (hasattr(logger, 'write') and callable(logger.write) and
          hasattr(logger, 'flush') and callable(logger.flush)):
        log_fd = logger
    else:
        raise ValueError('logger needs callable "write" and "flush" methods')

    # Discover the Violin appliance supplied
    for current_protocol in protocols_to_try:
        try:
            stream = urllib2.urlopen('{0}://{1}'.format(
                                     current_protocol, host))
        except urllib2.URLError as e:
            if debug:
                log_fd.write('{0}: {1}'.format(current_protocol, e))
                log_fd.flush()
        else:
            try:
                html = stream.read()
            except Exception as e:
                if debug:
                    log_fd.write('{0} (read): {1}'.format(
                                 current_protocol, e))
                    log_fd.flush()
                try:
                    stream.close()
                except Exception:
                    pass
            else:
                opener = None
                if 'viewport' in html:
                    opener = _open_json_gateway
                elif 'template' in html:
                    opener = _open_xml_gateway
                elif 'Violin Concerto Console' in html:
                    opener = _open_concerto_json_gateway_1
                elif '<a href="concerto/">concerto/</a>' in html:
                    opener = _open_concerto_json_gateway_2
                stream.close()
                if opener:
                    try:
                        return opener(host, user, password, current_protocol,
                                      version, debug, keepalive, log_fd)
                    except IndexError as e:
                        log_fd.write('Failed to get authenticated session ' +
                                     'and/or retrieve the ' +
                                     'version ({0}): {1}'.format(
                                     e.__class__.__name__, e))
                        log_fd.flush()
                        return None

    # Nothing worked
    return None


def _get_session_and_version(cls_type, host, user, password, debug,
                             proto, keepalive, log_fd, port):
    """Internal function to get a session and its version.

    A tuple is returned from this fuction.

    """
    session = cls_type(host, user, password, debug, proto,
                       True, keepalive, log_fd, port)
    return (session, session._get_version_info())


def _open_concerto_json_gateway_1(host, user, password, proto,
                             version, debug, keepalive, log_fd):
    """JSON REST connection for older Violin concerto device types.

    """
    from vmemclient.concerto import concerto
    from vmemclient.core.session import ConcertoJsonSession
    session, version_info = _get_session_and_version(ConcertoJsonSession,
            host, user, password, debug, proto, keepalive, log_fd, 10075)

    return __getDeviceFor(version_info, session, concerto, debug)


def _open_concerto_json_gateway_2(host, user, password, proto,
                             version, debug, keepalive, log_fd):
    """JSON REST connection for newer Violin concerto device types.

    """
    from vmemclient.concerto import concerto
    from vmemclient.core.session import ConcertoJsonSession
    session, version_info = _get_session_and_version(ConcertoJsonSession,
            host, user, password, debug, proto, keepalive, log_fd, 80)

    return __getDeviceFor(version_info, session, concerto, debug)


def _open_json_gateway(host, user, password, proto,
                       version, debug, keepalive, log_fd):
    """JSON REST connection for Symphony.

    """
    raise NotImplementedError('Violin Symphony devices are unsupported')


def _open_xml_gateway(host, user, password, proto,
                      version, debug, keepalive, log_fd):
    """Get the traditional tallmaple REST connection.

    """
    from vmemclient.core.session import XGSession
    session, version_info = _get_session_and_version(XGSession, host, user,
                                                     password, debug, proto,
                                                     keepalive, log_fd, None)

    if version_info['type'] in ('A',):
        # ACM
        from vmemclient.varray import varray
        return __getDeviceFor(version_info, session, varray, debug)
    elif version_info['type'] in ('G', 'V'):
        # MG
        from vmemclient.vshare import vshare
        return __getDeviceFor(version_info, session, vshare, debug)

    msg = 'Unknown version host_type: {0}'
    raise Exception(msg.format(version_info['type']))


def __getDeviceFor(version_info, session, moduleToSearch, debug):
    """Returns a device object.

    If there's a problem, an Exception is raised.

    """
    version_as_tuple = __to_version_tuple(version_info['version'])
    supported_versions = {}

    for name, obj in inspect.getmembers(moduleToSearch):
        if (inspect.isclass(obj) and name.find(
                moduleToSearch.CLASS_NAMES) > -1):
            if isinstance(obj._versions, basestring):
                supported_versions[__to_version_tuple(obj._versions)] = obj
            elif isinstance(obj._versions, list):
                for x in obj._versions:
                    supported_versions[__to_version_tuple(x)] = obj
            else:
                raise Exception('Unknown version type' +
                                '%s ' % (obj.versions.__class__,) +
                                'encountered in ' +
                                'class %s.' % (name,))

    # Find the newest object for the discovered version
    for x in reversed(sorted(supported_versions.keys())):
        if version_as_tuple >= x:
            return supported_versions[x](session, version_info)
    else:
        session.close()
        raise Exception('No matching connection class for {0}'.format(
                        version_info))


def __to_version_tuple(version):
    """Turns a dotted version string into a tuple for comparison's sake.

    """
    return tuple(int(x) for x in version.split('.'))
