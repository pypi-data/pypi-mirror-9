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

import re
from wsgiref.simple_server import demo_app as wsgiref_demo_app

import zope.testing.renormalizing


class win32CRLFtransformer(object):
    def sub(self, replacement, text):
        return text.replace(r'\r', '')


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(r'^--\S+\.\S+\.\S+', re.M), '-' * 30),
    (re.compile(r'boundary=\S+\.\S+\.\S+'), 'boundary=' + '-' * 30),
    (re.compile(r'^---{10}.*', re.M), '-' * 30),
    (re.compile(r'boundary=-{10}.*'), 'boundary=' + '-' * 30),
    (re.compile(r'User-agent:\s+\S+'), 'User-agent: Python-urllib/2.4'),
    (re.compile(r'HTTP_USER_AGENT:\s+\S+'),
     'HTTP_USER_AGENT: Python-urllib/2.4'),
    (re.compile(r'Content-[Ll]ength:.*'), 'Content-Length: 123'),
    (re.compile(r'Status: 200.*'), 'Status: 200 OK'),
    (win32CRLFtransformer(), None),
    (re.compile(r'User-Agent: Python-urllib/2.[567]'),
     'User-agent: Python-urllib/2.4'),
    #(re.compile(r'Host: localhost(:80)?'), 'Connection: close'),
    (re.compile(r'Content-Type: '), 'Content-type: '),
    (re.compile(r'Content-Disposition: '), 'Content-disposition: '),
    (re.compile(r'; charset=UTF-8'), ';charset=utf-8'),
    # webtest seems to expire cookies one second before the date set in
    # set_cookie
    (re.compile(
        r"'expires': datetime.datetime\(2029, 12, 31, 23, 59, 59, "
        r"tzinfo=<UTC>\),"),
        "'expires': datetime.datetime(2030, 1, 1, 0, 0, tzinfo=<UTC>),"),

    # python3 formats exceptions differently
    (re.compile(r'p01.testbrowser.exceptions.BrowserStateError'),
        'BrowserStateError'),
    (re.compile(r'p01.testbrowser.exceptions.ExpiredError'), 'ExpiredError'),
    (re.compile(r'p01.testbrowser.exceptions.LinkNotFoundError'),
        'LinkNotFoundError'),
    (re.compile(r'p01.testbrowser.exceptions.AmbiguityError'),
        'AmbiguityError'),
    (re.compile(r'p01.testbrowser.ftests.wsgitestapp.NotFound'), 'NotFound'),
    (re.compile(r'p01.testbrowser.exceptions.AlreadyExpiredError'),
        'AlreadyExpiredError'),
    (re.compile(r'p01.testbrowser.exceptions.RobotExclusionError'),
        'RobotExclusionError'),
    (re.compile(r'urllib.error.HTTPError'), 'HTTPError'),

    # In py3 HTTPMessage class was moved and represented differently
    (re.compile(r'<http.client.HTTPMessage object'),
        '<httplib.HTTPMessage instance'),
    #(re.compile(r''), ''),
    ])


# demo app
def demo_app(environ, start_response):
    """PEP-3333 compatible demo app, that will never return unicode
    """
    refout = wsgiref_demo_app(environ, start_response)
    return [s if isinstance(s, bytes) else s.encode('utf-8') for s in refout]
