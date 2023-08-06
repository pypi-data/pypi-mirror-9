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

class XGError(Exception):
    """Generic VXG Error."""
    pass


class ParseError(XGError):
    """Error parsing XML request/response."""
    pass


class TypeError(XGError):
    """Node type mismatch."""
    pass


class AuthenticationError(XGError):
    """Login authentication error."""
    pass


class UnsupportedProtocol(XGError):
    """Unsupported network protocol."""
    pass


class NetworkError(XGError):
    """Network error."""
    pass


class RestActionFailed(XGError):
    """A JSON REST action has failed."""
    pass


class MissingParameterError(XGError):
    """One or more parameters missing from the function invocation."""
    pass


class UnknownPathError(XGError):
    """A JSON REST path specified does not exist."""
    pass


class NoMatchingObjectIdError(XGError):
    """The object_id retrieval failed for the given name."""
    pass


class QueryError(XGError):
    """Problem encountered when attempting a HTTP GET."""
    pass
