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
XML Request / Response Data

This file contains a single list test_requests which contains two-value
tuples of requests and responses in XML format. This is used by the
faked version of urllib2 to produce fake output for the given request.

Note that in the faked version of urllib2, all whitespace (including
newlines and linefeeds) is ignored when comparing test generated
requests with the "canned" requests below.

"""

test_requests = [

# Example 1a  Get the system uptime, XML POST style
#
# Note: Testing against G5.2.0 shows that this request produces a different
#       response from the original document, namely it does not return the
#       node-id system containing node-id system ... it only returns the
#       node-id uptime.

("""
<xg-request>
<query-request>
    <nodes>
        <node>
            <name>/system/uptime</name>
        </node>
    </nodes>
</query-request>
</xg-request>
""", """
<xg-response>
<query-response>
    <return-status>
        <return-code>0</return-code>
        <return-msg></return-msg>
    </return-status>
    <db-revision-id>42</db-revision-id>
    <nodes>
        <node>
            <node-id>system</node-id>
            <node>
                <node-id>uptime</node-id>
                <binding>
                    <name>/system/uptime</name>
                    <type>duration_ms</type>
                    <value>975863616</value>
                </binding>
            </node>
        </node>
    </nodes>
</query-response>
</xg-response>
"""),

# Example 3a:  Get system hostname, full ntp config, and
#                 system uptime, XML POST style
#
# Note: Removed the no-config flag option from the iterate request
#       as we do not support different flags for different node elements
#       within a single request.
("""
<xg-request>
<query-request>
    <nodes>
        <node>
            <name>/system/hostname</name>
        </node>
        <node>
            <subop>iterate</subop>
            <flags>
                <flag>subtree</flag>
                <flag>include-self</flag>
            </flags>
            <name>/ntp</name>
        </node>
        <node>
            <name>/system/uptime</name>
        </node>
    </nodes>
</query-request>
</xg-request>
""", """
<xg-response>
<query-response>
    <return-status>
        <return-code>0</return-code>
        <return-msg/>
    </return-status>
    <db-revision-id>42</db-revision-id>
    <nodes>
        <node>
            <node-id>ntp</node-id>
            <binding>
                <name>/ntp</name>
                <type>string</type>
                <value>/ntp</value>
                <attribs>
                    <attrib>
                        <attribute-id>module_name</attribute-id>
                        <type>string</type>
                        <value>ntp</value>
                    </attrib>
                    <attrib>
                        <attribute-id>module_version</attribute-id>
                        <type>uint32</type>
                        <value>2</value>
                    </attrib>
                </attribs>
            </binding>
            <node>
                <node-id>enable</node-id>
                <binding>
                    <name>/ntp/enable</name>
                    <type>bool</type>
                    <value>true</value>
                </binding>
            </node>
            <node>
                <node-id>server</node-id>
                <node>
                    <node-id>address</node-id>
                    <node>
                        <node-id>10.0.0.1</node-id>
                        <binding>
                            <name>/ntp/server/address/10.0.0.1</name>
                            <type>hostname</type>
                            <value>10.0.0.1</value>
                        </binding>
                        <node>
                            <node-id>enable</node-id>
                            <binding>
                                <name>/ntp/server/address/10.0.0.1/enable</name>
                                <type>bool</type>
                                <value>true</value>
                            </binding>
                        </node>
                        <node>
                            <node-id>prefer</node-id>
                            <binding>
                                <name>/ntp/server/address/10.0.0.1/prefer</name>
                                <type>bool</type>
                                <value>false</value>
                            </binding>
                        </node>
                        <node>
                            <node-id>version</node-id>
                            <binding>
                                <name>/ntp/server/address/10.0.0.1/version</name>
                                <type>uint32</type>
                                <value>4</value>
                            </binding>
                        </node>
                    </node>
                    <node>
                        <node-id>10.1.0.40</node-id>
                        <binding>
                            <name>/ntp/server/address/10.1.0.40</name>
                            <type>hostname</type>
                            <value>10.1.0.40</value>
                        </binding>
                        <node>
                            <node-id>enable</node-id>
                            <binding>
                                <name>/ntp/server/address/10.1.0.40/enable</name>
                                <type>bool</type>
                                <value>true</value>
                            </binding>
                        </node>
                        <node>
                            <node-id>prefer</node-id>
                            <binding>
                                <name>/ntp/server/address/10.1.0.40/prefer</name>
                                <type>bool</type>
                                <value>false</value>
                            </binding>
                        </node>
                        <node>
                            <node-id>version</node-id>
                            <binding>
                                <name>/ntp/server/address/10.1.0.40/version</name>
                                <type>uint32</type>
                                <value>4</value>
                            </binding>
                        </node>
                    </node>
                    <node>
                        <node-id>208.78.244.49</node-id>
                        <binding>
                            <name>/ntp/server/address/208.78.244.49</name>
                            <type>hostname</type>
                            <value>208.78.244.49</value>
                        </binding>
                        <node>
                            <node-id>enable</node-id>
                            <binding>
                                <name>/ntp/server/address/208.78.244.49/enable</name>
                                <type>bool</type>
                                <value>true</value>
                            </binding>
                        </node>
                        <node>
                            <node-id>prefer</node-id>
                            <binding>
                                <name>/ntp/server/address/208.78.244.49/prefer</name>
                                <type>bool</type>
                                <value>false</value>
                            </binding>
                        </node>
                        <node>
                            <node-id>version</node-id>
                            <binding>
                                <name>/ntp/server/address/208.78.244.49/version</name>
                                <type>uint32</type>
                                <value>3</value>
                            </binding>
                        </node>
                    </node>
                </node>
            </node>
        </node>
        <node>
            <node-id>system</node-id>
            <node>
                <node-id>hostname</node-id>
                <binding>
                    <name>/system/hostname</name>
                    <type>hostname</type>
                    <value>tb7</value>
                </binding>
            </node>
            <node>
                <node-id>uptime</node-id>
                <binding>
                    <name>/system/uptime</name>
                    <type>duration_ms</type>
                    <value>976172352</value>
                </binding>
            </node>
        </node>
    </nodes>
</query-response>
</xg-response>
"""),

# Example 4) Set system hostname
#
("""
<xg-request>
<set-request>
    <nodes>
        <node>
            <name>/system/hostname</name>
            <type>hostname</type>
            <value>*myinvalidhostname*</value>
        </node>
    </nodes>
</set-request>
</xg-request>
""", """
<xg-response>
<set-response>
    <return-status>
        <return-code>1</return-code>
        <return-msg>Value must be a hostname.  Hostnames may contain letters, numbers,
periods ('.'), and hyphens ('-'), but may not begin with a hyphen.
</return-msg>
    </return-status>
    <db-revision-id>44</db-revision-id>
</set-response>
</xg-response>
"""),

# Example 5) Add a new NTP server, 10.1.0.40
#
("""
<xg-request>
<set-request>
    <nodes>
        <node>
            <name>/ntp/server/address/10.1.0.40</name>
            <type>hostname</type>
            <value>10.1.0.40</value>
        </node>
    </nodes>
</set-request>
</xg-request>
""", """
<xg-response>
<set-response>
    <return-status>
        <return-code>0</return-code>
        <return-msg/>
    </return-status>
    <db-revision-id>45</db-revision-id>
</set-response>
</xg-response>
"""),

# Example 8) Reverse a string (action) (demo example, not in
#            the base product)

("""
<xg-request>
<action-request>
    <action-name>/demo/echod/actions/reverse_string_nb_async
    </action-name>
    <nodes>
        <node>
            <name>string</name>
            <type>string</type>
            <value>abcdef</value>
        </node>
    </nodes>
</action-request>
</xg-request>
""", """
<xg-response>
<action-response>
    <return-status>
        <return-code>0</return-code>
        <return-msg>Thank you for letting us reverse 'abcdef' to 'fedcba' for you.
</return-msg>
    </return-status>
    <nodes>
        <node>
            <node-id>reversed_string</node-id>
            <binding>
                <name>reversed_string</name>
                <type>string</type>
                <value>fedcba</value>
            </binding>
        </node>
    </nodes>
</action-response>
</xg-response>
"""),

# Example 9) Send an event (demo example, not in the base product)
#
("""
<xg-request>
<event-request>
    <event-name>/demo/echod/notify/prefixchange
    </event-name>
    <nodes>
        <node>
            <name>/demo/echod/config/prefix</name>
            <type>string</type>
            <value>newprefix</value>
        </node>
    </nodes>
</event-request>
</xg-request>
""", """
<xg-response>
<event-response>
    <return-status>
        <return-code>0</return-code>
        <return-msg/>
    </return-status>
</event-response>
</xg-response>
"""),

# Request Example 10) Send invalid XML
#
("""
<xg-request>
    <foo/>
</xg-request>
""", """
<xg-response>
<xg-status>
    <status-code>1</status-code>
    <status-msg>Unknown xg request node: foo
XML gateway request: internal error</status-msg>
</xg-status>
</xg-response>
----------
"""),

# ======================================================================

# The following are artificial responses for testing certain corner cases

# Query request with no nodes returned
#
("""
<xg-request>
<query-request>
<nodes>
  <node>
    <name>/test/return/no/nodes</name>
  </node>
</nodes>
</query-request>
</xg-request>
""", """
<?xml version="1.0" encoding="UTF-8"?>
<xg-response>
  <query-response>
    <return-status>
      <return-code>0</return-code>
      <return-msg></return-msg>
    </return-status>
    <db-revision-id>137</db-revision-id>
  </query-response>
</xg-response>
"""),


# ======================================================================

# The following response-request pairs are taken from actual traffic
# from a Violin G5.1.0 gateway. The request node names have been changed
# when necessary to prevent duplicates with above.

# Request system uptime
#
("""
<xg-request>
<query-request>
<nodes>
  <node>
    <name>/test/system/uptime</name>
  </node>
</nodes>
</query-request>
</xg-request>
""", """
<?xml version="1.0" encoding="UTF-8"?>
<xg-response>
<query-response>
<return-status>
  <return-code>0</return-code>
  <return-msg></return-msg>
</return-status>
<db-revision-id>134</db-revision-id>
<nodes>
  <node>
    <name>/system/uptime</name>
    <type>duration_ms</type>
    <value>684884608</value>
  </node>
</nodes>
</query-response>
</xg-response>
"""),

# s.getNodes(["/ntp/***"])
#
("""
<xg-request>
<query-request>
<nodes>
  <node>
    <subop>iterate</subop>
    <flags>
      <flag>subtree</flag>
      <flag>include-self</flag>
    </flags>
    <name>/test/ntp</name>
  </node>
</nodes>
</query-request>
</xg-request>
""", """
<?xml version="1.0" encoding="UTF-8"?>
<xg-response>
<query-response>
<return-status>
  <return-code>0</return-code>
  <return-msg></return-msg>
</return-status>
<db-revision-id>134</db-revision-id>
<nodes>
  <node>
    <name>/ntp</name>
    <type>string</type>
    <value>/ntp</value>
    <attribs>
      <attrib>
        <attribute-id>module_name</attribute-id>
        <type>string</type>
        <value>ntp</value>
      </attrib>
      <attrib>
        <attribute-id>module_version</attribute-id>
        <type>uint32</type>
        <value>2</value>
      </attrib>
    </attribs>
  </node>
      <node>
        <name>/ntp/enable</name>
        <type>bool</type>
        <value>true</value>
      </node>
      <node>
        <name>/ntp/server/address/10.1.8.5</name>
        <type>hostname</type>
        <value>10.1.8.5</value>
      </node>
      <node>
        <name>/ntp/server/address/10.1.8.5/enable</name>
        <type>bool</type>
        <value>true</value>
      </node>
      <node>
        <name>/ntp/server/address/10.1.8.5/prefer</name>
        <type>bool</type>
        <value>false</value>
      </node>
      <node>
        <name>/ntp/server/address/10.1.8.5/version</name>
        <type>uint32</type>
        <value>4</value>
      </node>
      <node>
        <name>/ntp/state/peer/address/10.1.8.5</name>
        <type>ipv4addr</type>
        <value>10.1.8.5</value>
      </node>
      <node>
        <name>/ntp/state/peer/address/10.1.8.5/delay</name>
        <type>duration_us</type>
        <value>5962</value>
      </node>
      <node>
        <name>/ntp/state/peer/address/10.1.8.5/jitter</name>
        <type>duration_us</type>
        <value>731</value>
      </node>
      <node>
        <name>/ntp/state/peer/address/10.1.8.5/offset</name>
        <type>duration_us</type>
        <value>323</value>
      </node>
      <node>
        <name>/ntp/state/peer/address/10.1.8.5/poll_interval</name>
        <type>duration_sec</type>
        <value>1024</value>
      </node>
      <node>
        <name>/ntp/state/peer/address/10.1.8.5/reachability_register</name>
        <type>uint32</type>
        <value>255</value>
      </node>
      <node>
        <name>/ntp/state/peer/address/10.1.8.5/refid</name>
        <type>string</type>
        <value>130.126.24.53</value>
      </node>
      <node>
        <name>/ntp/state/peer/address/10.1.8.5/stratum</name>
        <type>uint32</type>
        <value>3</value>
      </node>
      <node>
        <name>/ntp/state/peer/address/10.1.8.5/tally_code</name>
        <type>char</type>
        <value>*</value>
      </node>
      <node>
        <name>/ntp/state/peer/address/10.1.8.5/tally_descr</name>
        <type>string</type>
        <value>sys.peer</value>
      </node>
      <node>
        <name>/ntp/state/peer/address/10.1.8.5/type_code</name>
        <type>char</type>
        <value>u</value>
      </node>
      <node>
        <name>/ntp/state/peer/address/10.1.8.5/type_descr</name>
        <type>string</type>
        <value>unicast</value>
      </node>
      <node>
        <name>/ntp/state/peer/address/10.1.8.5/when_last_packet</name>
        <type>duration_sec</type>
        <value>62</value>
      </node>
      <node>
        <name>/ntp/state/system_peer/address</name>
        <type>ipv4addr</type>
        <value>10.1.8.5</value>
      </node>
      <node>
        <name>/ntp/state/system_peer/offset</name>
        <type>duration_us</type>
        <value>323</value>
      </node>
    </nodes>
  </query-response>
</xg-response>
"""),
]
