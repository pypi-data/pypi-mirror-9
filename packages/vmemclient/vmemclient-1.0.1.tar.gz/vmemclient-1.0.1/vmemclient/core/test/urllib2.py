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
Fake implementation of urllib2 for use in unit testing

"""

import string
from xml_data import test_requests

test_host = "TEST"
login_url = ("https://%s/admin/launch?script=rh&template=home&action=login" %
             (test_host))
request_url = "https://%s/admin/launch?script=xg" % (test_host)

responses = {}
# A no-op translate map
tmap = string.maketrans(string.digits, string.digits)

for req in test_requests:
    if req[1][0] == "\n":
        responses[req[0].translate(tmap, string.whitespace)] = req[1][1:]
    else:
        responses[req[0].translate(tmap, string.whitespace)] = req[1]


class HTTPCookieProcessor:

    def __init__(self, cookiejar=None):
        pass


class HTTPResponse:
    """
    A fake implementation of the file-like object returned by urllib2
    open() funcitons.

    """

    def __init__(self, content):
        self.content = content
        self.read_count = 0

    def read(self):
        # To mimic a non-seekable read we track the number of read calls
        # and only return on the first. We could actually accept a size
        # argument and do in-string seeking from last read position but
        # we don't use size in our implemenation.
        if self.read_count == 0:
            return self.content
        else:
            self.read_count += 1
            return ""


class OpenerDirector:

    def __init__(self):
        pass

    def open(self, url, data, timeout=0):
        """
        This is where we do our faking of replies

        """

        if url == login_url:
            return self.fake_login(data)
        elif url == request_url:
            return self.fake_request(data)
        else:
            raise HTTPError("Not Found", 404)

    def fake_login(self, data):
        return HTTPResponse("test 123")

    def fake_request(self, request):
        # strip all the spaces from request

        # TODO(jbowen): should have more resilient pattern matchinf
        # for xmlversion header
        req_stripped = request.translate(tmap, string.whitespace).replace(
            '<?xmlversion="1.0"encoding="UTF-8"?>', '')

        # TODO(jbowen): Need better method of doing this
        # ordering of elements can cause match failures
        # might need to do some XML parsing. Sigh.

        #print "looking for:\n%s" % (req_stripped)
        if req_stripped in responses:
            resp = responses[req_stripped]

            # Get rid of leading blank line (artifact from xml_data.py)
            if resp[0] == "\n":
                return HTTPResponse(resp[1:])
            else:
                return HTTPResponse(resp)

        # We couldn't find a match
        raise UnknownRequest


def build_opener(handler):
    return OpenerDirector()


""" urllib2 exceptions """


class URLError(Exception):

    def __init__(self, reason=""):
        self.reason = reason


class HTTPError(URLError):

    def __init__(self, reason="", code=0):
        self.reason = reason
        self.code = code


""" Our own private exceptions """


class UnknownRequest(Exception):
    pass
