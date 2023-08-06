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
"""Testing helper
$Id: testing.py 4161 2015-02-17 11:32:01Z roger.ineichen $
"""

import re
import sys
import StringIO
import httplib
import xmlrpclib
import os.path

import transaction
from webtest import TestRequest

import zope.component.eventtesting
from zope.component import hooks
from zope.configuration import config
from zope.configuration import xmlconfig
try:
    from zope.testing.cleanup import cleanUp
except ImportError:
    def cleanUp():
        pass

from z3c.json.proxy import JSONRPCProxy
from z3c.json.transport import Transport
from z3c.json.exceptions import ProtocolError
from z3c.jsonrpc.publisher import JSON_RPC_VERSION

import p01.testbrowser.browser
from p01.testbrowser._compat import base64_encodebytes


###############################################################################
#
# test browser based on wsgi application setup

_APP_UNDER_TEST = None

class Browser(p01.testbrowser.browser.Browser):
    def __init__(self, url=None, wsgi_app=None):
         if wsgi_app is None:
             wsgi_app = Layer.get_app()
         if wsgi_app is None:
             raise AssertionError(
                "wsgi_app missing or p01.testbrowser.testing.Layer not setup")
         super(Browser, self).__init__(url, wsgi_app)


def getWSGITestBrowser(url=None, wsgi_app=None, handleErrors=True):
    """Get a wsgi application based test browser"""
    if wsgi_app is None:
        global _APP_UNDER_TEST
        if _APP_UNDER_TEST is None:
             raise AssertionError(
                "_APP_UNDER_TEST missing, check p01.testbrowser.testing setup")
        wsgi_app = _APP_UNDER_TEST
    wsgi_app.handleErrors = handleErrors
    browser = Browser(url=url, wsgi_app=wsgi_app)
    browser.handleErrors = handleErrors
    return browser


###############################################################################
#
# JSONRPC proxy based on wsgi application setup
#
# NOTE: the JSONRPCProxy given from getJSONRPCTestProxy requires a
#       wsgi application setup and doens't depend on HTTPCaller setup like the
#       z3c.jsonrpc test proxy setup
#
###############################################################################

class NotInBrowserLayer(Exception):
    """The current test is not running in a layer inheriting from
    BrowserLayer.
    """


class FakeResponse(object):
    """This behave like a Response object returned by HTTPCaller of
    zope.app.testing.functional.
    """

    def __init__(self, response):
        self.response = response

    def getStatus(self):
        return self.response.status_int

    def getStatusString(self):
        return self.response.status

    def getHeader(self, name, default=None):
        return self.response.headers.get(name, default)

    def getHeaders(self):
        return self.response.headerlist

    def getBody(self):
        return self.response.body

    def getOutput(self):
        parts = ['HTTP/1.0 ' + self.response.status]
        parts += map('%s: %s'.__mod__, self.response.headerlist)
        if self.response.body:
            parts += ['', self.response.body]
        return '\n'.join(parts)

    __str__ = getOutput


def http(string, handleErrors=True):
    app = Layer.get_app()
    if app is None:
        raise NotInBrowserLayer(NotInBrowserLayer.__doc__)

    request = TestRequest.from_file(StringIO.StringIO(string))
    request.environ['wsgi.handleErrors'] = handleErrors
    response = request.get_response(app)
    return FakeResponse(response)


class JSONRPCTestTransport(Transport):
    """Test transport using our wsgi app given from layer setup.

    It can be used like a normal transport, including support for basic
    authentication.
    """

    verbose = False
    handleErrors = True

    def request(self, host, handler, request_body, verbose=0):
        request = "POST %s HTTP/1.0\n" % (handler,)
        request += "Content-Length: %i\n" % len(request_body)
        request += "Content-Type: application/json-rpc\n"

        host, extra_headers, x509 = self.get_host_info(host)
        if extra_headers:
            basic = dict(extra_headers)["Authorization"]
            request += "Authorization: %s\n" % basic

        request += "Host: %s\n" % host
        request += "\n" + request_body
        assert isinstance(request_body, bytes)
        assert isinstance(request, bytes)

        response = http(request, handleErrors=self.handleErrors)

        errcode = response.getStatus()
        errmsg = response.getStatusString()
        # This is not the same way that the normal transport deals with the
        # headers.
        headers = response.getHeaders()

        if errcode != 200:
            raise ProtocolError(host + handler, errcode, errmsg, headers)

        return self._parse_response(
            StringIO.StringIO(response.getBody()), sock=None)


def getJSONRPCTestProxy(uri, transport=None, encoding='UTF-8', verbose=None,
    jsonId=None, handleErrors=True, jsonVersion=JSON_RPC_VERSION):
    """A factory that creates a server proxy using the JSONRPCTestTransport"""
    if verbose is None:
        verbose = 0
    if transport is None:
        transport = JSONRPCTestTransport()
    if isinstance(transport, JSONRPCTestTransport):
        transport.handleErrors = handleErrors
    return JSONRPCProxy(uri, transport, encoding, verbose, jsonId, jsonVersion)



###############################################################################
#
# test layer middleware

basicre = re.compile('Basic (.+)?:(.+)?$')

def auth_header(header):
    """This function takes an authorization HTTP header and encode the
    couple user, password into base 64 like the HTTP protocol wants
    it.
    """
    match = basicre.match(header)
    if match:
        u, p = match.group(1, 2)
        if u is None:
            u = ''
        if p is None:
            p = ''
        plain = '%s:%s' % (u, p)
        auth = base64_encodebytes(plain.encode('utf-8'))
        return 'Basic %s' % str(auth.rstrip().decode('latin1'))
    return header


def is_wanted_header(header):
    """Return True if the given HTTP header key is wanted.
    """
    key, value = header
    return key.lower() not in ('x-content-type-warning', 'x-powered-by')


class AuthorizationMiddleware(object):
    """This middleware support Basic auth headers
    - It modifies the HTTP_AUTHORIZATION header to encode user and
      password into base64 if it is Basic authentication.
    """

    def __init__(self, wsgi_stack):
        self.wsgi_stack = wsgi_stack

    def __call__(self, environ, start_response):
        # Handle authorization
        auth_key = 'HTTP_AUTHORIZATION'
        if auth_key in environ:
            environ[auth_key] = auth_header(environ[auth_key])

        # Remove unwanted headers
        def application_start_response(status, headers, exc_info=None):
            headers = [h for h in headers if is_wanted_header(h)]
            start_response(status, headers)

        for entry in self.wsgi_stack(environ, application_start_response):
            yield entry


class TransactionMiddleware(object):
    """This middleware makes the WSGI application compatible with the
    HTTPCaller behavior defined in zope.app.testing.functional.
    It commits the transaction before and synchronises the current transaction
    after the test.

    """
    def __init__(self, getRootFolder, wsgi_app):
        # snyc transaction basedon given getRootFolder lookup
        self.getRootFolder = getRootFolder
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        transaction.commit()
        for entry in self.wsgi_app(environ, start_response):
            yield entry
        self.getRootFolder()._p_jar.sync()


###############################################################################
#
# test layer

class Layer(object):
    """Test layer which sets up WSGI application for use with
    WebTest/testbrowser.

    """

    __bases__ = ()
    __name__ = 'Layer'

    def make_wsgi_app(self):
        # Override this method in subclasses of this layer in order to set up
        # the WSGI application.
        raise NotImplementedError

    @classmethod
    def get_app(cls):
        return _APP_UNDER_TEST

    def cooperative_super(self, method_name):
        # Calling `super` if available
        method = getattr(super(Layer, self), method_name, None)
        if method is not None:
            method()

    def testSetUp(self):
        self.cooperative_super('testSetUp')
        global _APP_UNDER_TEST
        if _APP_UNDER_TEST is not None:
            raise AssertionError("Already Setup")
        _APP_UNDER_TEST = self.make_wsgi_app()

    def testTearDown(self):
        global _APP_UNDER_TEST
        _APP_UNDER_TEST = None
        self.cooperative_super('testTearDown')


###############################################################################
#
# ftesting.zcml test layer

class ZCMLFileLayer(object):
    """ZCML file setup layer without using functional setup.

    This layer doesn't use functional.FunctionalTestSetup which will use the
    Debugger for setup the config.
    """

    __bases__ = ()
    context = None

    def __init__(self, package, name, zcmlFile, features=None):
        self.package = package
        self.__module__ = package.__name__
        self.__name__ = name
        self.zcmlFile = zcmlFile
        if features is None:
            features = []
        self.features = features

    def setUp(self):
        hooks.setHooks()
        context = config.ConfigurationMachine()
        xmlconfig.registerCommonDirectives(context)
        for feature in self.features:
            context.provideFeature(feature)
        self.context = self._load_zcml(context)
        zope.component.provideHandler(
            zope.component.eventtesting.events.append, (None,))

    def tearDown(self):
        # cleanup configuration
        cleanUp()

    def _load_zcml(self, context):
        return xmlconfig.file(self.zcmlFile, package=self.package,
            context=context, execute=True)


def getZCMLFileLayer(pkgName, name, zcml='ftesting.zcml', features=None):
    """Returns the ZCMLLayer based on package, name and zcml file name or path.
    """
    package = sys.modules[pkgName]
    if zcml == 'ftesting.zcml':
        # join with package path, otherwise zcml must provide a full path
        zcml = os.path.join(os.path.dirname(package.__file__), zcml)
    return ZCMLFileLayer(package, name, zcml, features=features,
        )
