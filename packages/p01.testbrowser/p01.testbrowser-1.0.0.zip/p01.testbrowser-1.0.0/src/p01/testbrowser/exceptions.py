##############################################################################
#
# Copyright (c) 2014 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser-like functional doctest interfaces
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
import zope.interface.common.mapping

from p01.testbrowser._compat import urllib_request


class ExpiredError(Exception):
    """The browser page to which this was attached is no longer active"""


class AlreadyExpiredError(ValueError):
    """Already expired error"""


# jsonrpc exceptions
class JSONRPCResponseError(Exception):
    """JSONRPC response (processing) error"""


class AmbiguityError(ValueError):
    """Ambiguity error"""


class BrowserStateError(Exception):
    """Browser state error"""


class LinkNotFoundError(IndexError):
    """Link not found error"""


class HostNotAllowed(Exception):
    """Host not allowed error"""


class RobotExclusionError(urllib_request.HTTPError):
    """Robot exclusion error"""

    def __init__(self, *args):
        super(RobotExclusionError, self).__init__(*args)
