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
"""Test application
"""
__docformat__ = "reStructuredText"

from six.moves import urllib_robotparser
from p01.testbrowser._compat import urlparse

import webtest

import p01.testbrowser.exceptions


_allowed_2nd_level = set(['example.com', 'example.net', 'example.org']) # RFC 2606

_allowed = set(['localhost', '127.0.0.1'])
_allowed.update(_allowed_2nd_level)


class TestApp(webtest.TestApp):
    """Test browser application"""

    _last_fragment = ""
    restricted = False

    def _assertAllowed(self, url):
        parsed = urlparse.urlparse(url)
        if self.restricted:
            # We are in restricted mode, check host part only
            host = parsed.netloc.partition(':')[0]
            if host in _allowed:
                return
            for dom in _allowed_2nd_level:
                if host.endswith('.%s' % dom):
                    return

            raise p01.testbrowser.exceptions.HostNotAllowed(url)
        else:
            # Unrestricted mode: retrieve robots.txt and check against it
            robotsurl = urlparse.urlunsplit((parsed.scheme, parsed.netloc,
                                             '/robots.txt', '', ''))
            rp = urllib_robotparser.RobotFileParser()
            rp.set_url(robotsurl)
            rp.read()
            if not rp.can_fetch("*", url):
                msg = "request disallowed by robots.txt"
                raise p01.testbrowser.exceptions.RobotExclusionError(url, 403,
                    msg, [], None)

    def do_request(self, req, status, expect_errors):
        self._assertAllowed(req.url)
        response = super(TestApp, self).do_request(req, status,
            expect_errors)
        # Store _last_fragment in response to preserve fragment for history
        # (goBack() will not lose fragment).
        response._last_fragment = self._last_fragment
        return response

    def _remove_fragment(self, url):
        # HACK: we need to preserve fragment part of url, but webtest strips it
        # from url on every request. So we override this protected method,
        # assuming it is called on every request and therefore _last_fragment
        # will not get outdated. ``getRequestUrlWithFragment()`` will
        # reconstruct url with fragment for the last request.
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        self._last_fragment = fragment
        return super(TestApp, self)._remove_fragment(url)

    def getRequestUrlWithFragment(self, response):
        url = response.request.url
        if not self._last_fragment:
            return url
        return "%s#%s" % (url, response._last_fragment)
