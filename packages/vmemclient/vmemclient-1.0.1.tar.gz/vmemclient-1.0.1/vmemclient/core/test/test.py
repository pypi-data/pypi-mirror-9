#!/usr/bin/env python

# =============================================================================
# Copyright 2012-2013 Violin Memory, Inc.. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY VIOLIN MEMORY, INC ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL VIOLIN MEMORY, INC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Violin Memory, Inc.
# =============================================================================

"""
Unit test framework

Note we overload the test host's urllib2 with our own fake implementation
so we can do self-contained testing. This is accomplished by having a
file named urllib2.py in the same directory as this test script. This works
because python looks first for modules in the same directory as the script
that executed python (ie. us).

"""

# In order to get our session module we need to modify the module search path
# We insert rather than append to ensure we do not use any installed version
# of session on our host system.
import sys

# TODO(jbowen): This only works if we run from the current directory
#       really need to add path relative to this file not working dir
sys.path.insert(1, "../../../")
from vxg.core.node import XGNode
from vxg.core.error import *
from vxg.core.request import XGRequest
from vxg.core.session import XGSession

from cStringIO import StringIO

host = "TEST"
user = "admin"
pwd = ""

test_no = 0
test_stdout = None
test = ""


def print_test_info():

    global test_no, test, test_stdout

    sys.stdout = sys.__stdout__

    print "-----------------------------------------"
    print " Test failure"
    print "-----------------------------------------"

    if test_stdout is not None:
        print test_stdout.getvalue()
        test_stdout.close()

    print "-----------------------------------------"
    print "Test: #%d %s" % (test_no, test)


def new_test(name):
    global test_no, test, test_stdout

    if test_stdout is not None:
        test_stdout.close()
    sys.stdout = test_stdout = StringIO()

    test_no += 1
    test = name


def find_node_by_name(node_list, name):
    for child in node_list:
        if child.node_name == name:
            return child
    return None


def lookup(node_dict, name):
    try:
        return node_dict[name]
    except KeyError:
        raise Assertion("Key '%s' not in dict." % (name))


def find_node_by_id(node_list, node_id):
    for child in node_list:
        if child.node_id == node_id:
            return child
    return None

# ===========================
# Start of tests
# ===========================

try:
    new_test("Login")
    s = XGSession(host, user, pwd, debug=True)
    sys.stdout = sys.__stdout__
    print test_stdout.read()

    # =======================================================================
    new_test("Query /system/uptime (TMS Example 1a) - send_request()")

    node = XGNode("/system/uptime")
    req = XGRequest("query", [node])
    resp = s.send_request(req)

    assert isinstance(resp.nodes, list), "Wrong return type (not a list)."
    assert resp.r_code == 0, "Wrong return code."
    assert resp.nodes is not None, "Nodes list returned as None."
    assert len(resp.nodes) == 1, "Unexpected/missing response nodes."
    assert isinstance(resp.nodes[0], XGNode), "List element not an XGNode."
    assert len(resp.nodes[0].nodes) == 1, \
        "Unexpected/missing response sub-nodes."

    sub_node = resp.nodes[0].nodes[0]
    assert sub_node.name == "/system/uptime", "Invalid node name."
    assert sub_node.node_id == "uptime", "Invalid node ID."
    # duration_ms is currently a string
    assert sub_node.value == "975863616", "Invalid node value."
    assert sub_node.type == "duration_ms", "Invalid node type."

    # =======================================================================
    new_test("Query /system/uptime (TMS Example 1a) - get_nodes()")
    nodes = s.get_nodes(["/system/uptime"])

    assert isinstance(nodes, dict), "get_nodes() did not return dict."
    assert len(nodes) == 1, "Response missing node."

    sub_node = nodes["/system/uptime"]
    assert sub_node.name == "/system/uptime", "Invalid node name."
    assert sub_node.node_id == "uptime", "Invalid node ID."
    # duration_ms is currently a string
    assert sub_node.value == "975863616", "Invalid node value."
    assert sub_node.type == "duration_ms", "Invalid node type."

    # =======================================================================
    new_test("Query /system/uptime (TMS Example 1a) - get_node_values()")

    nodes = s.get_node_values(["/system/uptime"])

    assert isinstance(nodes, dict), "get_node_values() did not return dict."
    assert len(nodes) == 1, "Incorrect node value count."

    assert isinstance(nodes["/system/uptime"], str), "Wrong dict element type."
    # duration_ms is currently a string
    assert nodes["/system/uptime"] == "975863616", "Invalid node value."

    # =======================================================================
    new_test("Multiple query with iteration (TMS Example 3a) - get_nodes()")

    nodes = s.get_nodes(["/system/hostname", "/ntp/***", "/system/uptime"])
    assert isinstance(nodes, dict), "get_nodes() did not return dict."

    ntp_node = lookup(nodes, "/ntp")
    assert ntp_node is not None, "Missing /ntp node."

    ntp_enable_node = lookup(nodes, "/ntp/enable")
    assert ntp_enable_node.value == True, "Wrong /ntp/enable value."
    assert ntp_enable_node.type == "bool", "Wrong /ntp/enable type."

    upt_node = lookup(nodes, "/system/uptime")
    assert upt_node is not None, "Missing /system/uptime node."
    # duration_ms is currently a string
    assert upt_node.value == "976172352", "Invalid /system/uptime value."
    assert upt_node.type == "duration_ms", "Invalid /system/uptime type."

    host_node = lookup(nodes, "/system/hostname")
    assert host_node is not None, "Missing /system/hostname node."
    assert host_node.value == "tb7", "Wrong hostname."
    assert host_node.type == "hostname", "Wrong hostname type."

    # =======================================================================
    new_test("Multiple query with iteration (TMS Example 3a) - "
             "get_node_values()")

    nodes = s.get_node_values(["/system/hostname", "/ntp/***",
                               "/system/uptime"])

    ntp_node = lookup(nodes, "/ntp")
    assert ntp_node is not None, "Missing /ntp node."
    ntp_enable_node = lookup(nodes, "/ntp/enable")
    assert ntp_enable_node == True, "Wrong /ntp/enable value."

    upt_node = lookup(nodes, "/system/uptime")
    # duration_ms is currently a string
    assert upt_node == "976172352", "Invalid /system/uptime value."

    host_node = lookup(nodes, "/system/hostname")
    assert host_node == "tb7", "Wrong hostname."

    # =======================================================================
    new_test("Set system hostname to invalid value (TMS Example 4) - "
             "send_request()")

    set_node = XGNode("/system/hostname", "hostname", "*myinvalidhostname*")
    req = XGRequest("set", [set_node])
    resp = s.send_request(req)

    assert resp.r_code == 1, "Wrong return code."
    assert resp.r_msg.startswith("Value must be a hostname"), \
        "Wrong return message."
    assert resp.db_rev == 44, "Wrong db-revision."

    # =======================================================================
    new_test("Add new NTP server (TMS Example 5)")

    set_node = XGNode("/ntp/server/address/10.1.0.40", "hostname", "10.1.0.40")
    req = XGRequest("set", [set_node])
    resp = s.send_request(req)

    assert resp.r_code == 0, "Wrong return code."
    assert resp.r_msg is None, "Wrong return message."
    assert resp.db_rev == 45, "Wrong db-revision."

    # =======================================================================
    new_test("Send an action (TMS Example 8)")

    node = XGNode("string", "string", "abcdef")
    req = XGRequest("action", [node],
                    action="/demo/echod/actions/reverse_string_nb_async")
    resp = s.send_request(req)

    assert resp.r_code == 0, "Wrong return code."
    assert resp.r_msg.startswith("Thank you for letting us"), \
        "Wrong return message."
    assert len(resp.nodes) == 1, "Wrong node count in response."

    resp_node = resp.nodes[0]
    assert resp_node.node_id == "reversed_string", "Wrong node id in response."
    assert resp_node.name == "reversed_string", "Wrong node name in response."
    assert resp_node.type == "string", "Wrong node type in response."
    assert resp_node.value == "fedcba", "Wrong node value in response."

    # =======================================================================
    new_test("Send an event (TMS Example 9)")

    node = XGNode("/demo/echod/config/prefix", "string", "newprefix")
    req = XGRequest("event", [node], event="/demo/echod/notify/prefixchange")
    resp = s.send_request(req)

    assert resp.r_code == 0, "Wrong return code."
    assert resp.r_msg is None, "Wrong return message."
    assert len(resp.nodes) == 0, "Unexpected node(s) in response."

    # =======================================================================
    new_test("Check system uptime (real traffic) - send_request()")

    node = XGNode("/test/system/uptime")
    req = XGRequest("query", [node])
    resp = s.send_request(req)

    assert resp.r_code == 0, "Wrong return code."
    assert resp.r_msg is None, "Wrong return message."
    assert len(resp.nodes) == 1, "Unexpected node(s) in response."
    assert resp.db_rev == 134, "WRong db-revision."

    resp_node = resp.nodes[0]
    assert resp_node.name == "/system/uptime", "Wrong node name in response."
    assert resp_node.type == "duration_ms", "Wrong node type in response."
    assert resp_node.value == "684884608", "Wrong node value in response."

    # =======================================================================
    new_test("Query with not response nodes - send_request()")

    node = XGNode("/test/return/no/nodes")
    req = XGRequest("query", [node])
    resp = s.send_request(req)

    assert resp.r_code == 0, "Wrong return code."
    assert resp.nodes is not None, "Nodes list returned as None."
    assert len(resp.nodes) == 0, "Unexpected response nodes."

    # =======================================================================
    new_test("Iterative query (real traffic) - send_request()")

    node = XGNode("/test/ntp", flags=["subtree", "include-self"],
                  subop="iterate")
    req = XGRequest("query", [node])
    resp = s.send_request(req)

    assert resp.r_code == 0, "Wrong return code."
    assert resp.r_msg is None, "Wrong return message."
    assert len(resp.nodes) == 21, "Unexpected / missing node(s) in response."
    assert resp.db_rev == 134, "Wrong db-revision."

    # Check attributes of root node
    root_node = resp.nodes[0]
    #print root_node
    assert root_node.name == "/ntp", "Wrong node name in response."
    assert root_node.type == "string", "Wrong node type in response."
    assert root_node.value == "/ntp", "Wrong node value in response."
    assert len(root_node.attrs) == 2, "Unexpected / missing node attributes."
    assert root_node.attrs["module_name"].value == "ntp", \
        "Wrong module_name attribute value."
    assert root_node.attrs["module_name"].type == "string", \
        "Wrong module_name attribute type."
    # attribute values are currently strings regardless of type
    assert root_node.attrs["module_version"].value == "2", \
        "Wrong module_version attribute value."
    assert root_node.attrs["module_version"].type == "uint32", \
        "Wrong module_version attribute type."

    # =======================================================================
    new_test("Using get_node_values with a string as the input")

    node_name = '/system/uptime'
    uptime = s.get_node_values(node_name)
    uptime = uptime[node_name]

    assert uptime == '975863616', "Uptime is incorrect"

# 'except Exception as variable' is valid for python 2.6 but not for 2.5
# use comma syntax for backwards compatibility
except XGError, e:
    print_test_info()
    print "Error: %s" % (e.msg)
    exit(1)

except AssertionError, a:
    print_test_info()
    print "Assertion Failed: %s" % (a.args[0])
    exit(1)


if test_stdout is not None:
    sys.stdout = sys.__stdout__

print "-----------------------------------------"
print " Test results"
print "-----------------------------------------"
print "%d tests passed. No failures." % (test_no)
