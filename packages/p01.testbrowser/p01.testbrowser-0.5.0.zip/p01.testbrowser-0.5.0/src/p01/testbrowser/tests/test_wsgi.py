# -*- coding: utf-8 -*-
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

import unittest

import p01.testbrowser.wsgi
from p01.testbrowser.ftests.wsgitestapp import WSGITestApplication
from p01.testbrowser.testing import demo_app
from p01.testbrowser._compat import urlencode, url_quote


class SimpleLayer(p01.testbrowser.wsgi.Layer):

    def make_wsgi_app(self):
        return demo_app

SIMPLE_LAYER = SimpleLayer()


class TestBrowser(unittest.TestCase):

    def test_redirect_and_raiseHttpErrors(self):
        app = WSGITestApplication()
        browser = p01.testbrowser.wsgi.Browser(wsgi_app=app)
        browser.raiseHttpErrors = False
        browser.open('http://localhost/redirect.html?to=/not_found.html')
        self.assertEqual(browser.headers['status'], '404 Not Found')
        self.assertEqual(browser.url, 'http://localhost/not_found.html')

    def test_redirect(self):
        app = WSGITestApplication()
        browser = p01.testbrowser.wsgi.Browser(wsgi_app=app)
        # redirecting locally works
        browser.open('http://localhost/redirect.html?%s'
                     % urlencode(dict(to='/set_status.html')))
        self.assertEqual(browser.url, 'http://localhost/set_status.html')
        browser.open('http://localhost/redirect.html?%s'
                     % urlencode(dict(to='/set_status.html', type='301')))
        self.assertEqual(browser.url, 'http://localhost/set_status.html')
        browser.open('http://localhost/redirect.html?%s'
                     % urlencode(dict(to='http://localhost/set_status.html')))
        self.assertEqual(browser.url, 'http://localhost/set_status.html')
        browser.open('http://localhost/redirect.html?%s'
                     % urlencode(dict(to='http://localhost/set_status.html', type='301')))
        self.assertEqual(browser.url, 'http://localhost/set_status.html')
        # non-local redirects raise HostNotAllowed error
        self.assertRaises(p01.testbrowser.wsgi.HostNotAllowed,
                          browser.open,
                          'http://localhost/redirect.html?%s'
                          % urlencode(dict(to='http://www.google.com/')))
        self.assertRaises(p01.testbrowser.wsgi.HostNotAllowed,
                          browser.open,
                          'http://localhost/redirect.html?%s'
                          % urlencode(dict(to='http://www.google.com/', type='301')))

        # we're also automatically redirected on submit
        browser.open('http://localhost/@@/testbrowser/forms.html')
        self.assertEquals(browser.headers.get('status'), '200 OK')
        form = browser.getForm(name='redirect')
        form.submit()
        self.assertEquals(browser.headers.get('status'), '200 OK')
        self.assertEquals(browser.url, 'http://localhost/set_status.html')

## See https://github.com/zopefoundation/zope.testbrowser/pull/4#issuecomment-24302778
##
##  def test_no_redirect(self):
##      app = WSGITestApplication()
##      browser = p01.testbrowser.wsgi.Browser(wsgi_app=app)

##      # tell testbrowser to not handle redirects automatically
##      browser.handleRedirects = False

##      # and tell p01.testbrowser to not raise HTTP errors (everything but
##      # 20x responses is considered an error)
##      browser.raiseHttpErrors = False

##      url = ('http://localhost/redirect.html?%s'
##             % urlencode(dict(to='/set_status.html')))
##      browser.open(url)

##      # see - we're not redirected
##      self.assertEquals(browser.url, url)
##      self.assertEquals(browser.headers.get('status'), '302 Found')

##      # the same should happen on submit (issue #4)
##      browser.open('http://localhost/@@/testbrowser/forms.html')
##      self.assertEquals(browser.headers.get('status'), '200 OK')
##      form = browser.getForm(name='redirect')
##      form.submit()
##      self.assertEquals(browser.headers.get('status'), '302 Found')
##      self.assertEquals(browser.url, url)

    def test_allowed_domains(self):
        browser = p01.testbrowser.wsgi.Browser(wsgi_app=demo_app)
        # external domains are not allowed
        self.assertRaises(p01.testbrowser.wsgi.HostNotAllowed, browser.open, 'http://www.google.com')
        self.assertRaises(p01.testbrowser.wsgi.HostNotAllowed, browser.open, 'https://www.google.com')
        # internal ones are
        browser.open('http://localhost')
        self.assertTrue(browser.contents.startswith('Hello world!\n'))
        browser.open('http://127.0.0.1')
        self.assertTrue(browser.contents.startswith('Hello world!\n'))
        # even if they include port numbers
        browser.open('http://localhost:8080')
        self.assertTrue(browser.contents.startswith('Hello world!\n'))
        browser.open('http://127.0.0.1:8080')
        self.assertTrue(browser.contents.startswith('Hello world!\n'))
        # as are example ones
        browser.open('http://example.com')
        self.assertTrue(browser.contents.startswith('Hello world!\n'))
        browser.open('http://example.net')
        self.assertTrue(browser.contents.startswith('Hello world!\n'))
        # and subdomains of example
        browser.open('http://foo.example.com')
        self.assertTrue(browser.contents.startswith('Hello world!\n'))
        browser.open('http://bar.example.net')
        self.assertTrue(browser.contents.startswith('Hello world!\n'))

    def test_handleErrors(self):
        # http://wsgi.org/wsgi/Specifications/throw_errors
        app = WSGITestApplication()
        browser = p01.testbrowser.wsgi.Browser(wsgi_app=app)
        browser.open('http://localhost/echo_one.html?var=x-wsgiorg.throw_errors')
        self.assertEqual(browser.contents, 'None')
        browser.open('http://localhost/echo_one.html?var=paste.throw_errors')
        self.assertEqual(browser.contents, 'None')
        browser.open('http://localhost/echo_one.html?var=wsgi.handleErrors')
        self.assertEqual(browser.contents, 'True')
        browser.open('http://localhost/echo_one.html?var=HTTP_X_ZOPE_HANDLE_ERRORS')
        self.assertEqual(browser.contents, "'True'")
        browser.handleErrors = False
        browser.open('http://localhost/echo_one.html?var=x-wsgiorg.throw_errors')
        self.assertEqual(browser.contents, 'True')
        browser.open('http://localhost/echo_one.html?var=paste.throw_errors')
        self.assertEqual(browser.contents, 'True')
        browser.open('http://localhost/echo_one.html?var=wsgi.handleErrors')
        self.assertEqual(browser.contents, 'False')
        browser.open('http://localhost/echo_one.html?var=HTTP_X_ZOPE_HANDLE_ERRORS')
        self.assertEqual(browser.contents, 'None')

    def test_non_ascii_urls(self):
        teststr = u'~ひらがな'
        url = "http://localhost/%s" % url_quote(teststr.encode('utf-8'))
        app = WSGITestApplication()
        browser = p01.testbrowser.wsgi.Browser(wsgi_app=app)
        browser.raiseHttpErrors = False
        browser.open(url)
        req = app.request_log[0]
        self.assertEqual(req.url, url)
        self.assertEqual(req.path_info, u'/' + teststr)

    def test_binary_content_type(self):
        # regression during webtest porting
        app = WSGITestApplication()
        browser = p01.testbrowser.wsgi.Browser(wsgi_app=app)
        browser.handleErrors = False
        browser.open('http://localhost/@@/testbrowser/zope3logo.gif')
        self.assertEqual(browser.headers['content-type'], 'image/gif')

class TestWSGILayer(unittest.TestCase):

    def setUp(self):
        # test the layer without depending on zope.testrunner
        SIMPLE_LAYER.setUp()

    def tearDown(self):
        SIMPLE_LAYER.tearDown()

    def test_layer(self):
        """When the layer is setup, the wsgi_app argument is unnecessary"""
        browser = p01.testbrowser.wsgi.Browser()
        browser.open('http://localhost')
        self.assertTrue(browser.contents.startswith('Hello world!\n'))
        # XXX test for authorization header munging is missing

    def test_app_property(self):
        # The layer has a .app property where the application under test is available
        self.assertTrue(SIMPLE_LAYER.get_app() is demo_app)

    def test_there_can_only_be_one(self):
        another_layer = SimpleLayer()
        # The layer has a .app property where the application under test is available
        self.assertRaises(AssertionError, another_layer.setUp)

class TestAuthorizationMiddleware(unittest.TestCase):

    def setUp(self):
        app = WSGITestApplication()
        self.unwrapped_browser = p01.testbrowser.wsgi.Browser(wsgi_app=app)
        app = p01.testbrowser.wsgi.AuthorizationMiddleware(app)
        self.browser = p01.testbrowser.wsgi.Browser(wsgi_app=app)

    def test_unwanted_headers(self):
        #x-powered-by and x-content-type-warning are filtered
        url = 'http://localhost/set_header.html?x-other=another&x-powered-by=zope&x-content-type-warning=bar'
        self.browser.open(url)
        self.assertEqual(self.browser.headers['x-other'], 'another')
        self.assertTrue('x-other' in self.browser.headers)
        self.assertFalse('x-powered-by' in self.browser.headers)
        self.assertFalse('x-content-type-warning' in self.browser.headers)
        # make sure we are actually testing something
        self.unwrapped_browser.open(url)
        self.assertTrue('x-powered-by' in self.unwrapped_browser.headers)
        self.assertTrue('x-content-type-warning' in self.unwrapped_browser.headers)

    def test_authorization(self):
        # Basic authorization headers are encoded in base64
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open('http://localhost/echo_one.html?var=HTTP_AUTHORIZATION')
        self.assertEqual(self.browser.contents, repr('Basic bWdyOm1ncnB3'))
        # this header persists over multiple requests
        self.browser.open('http://localhost/echo_one.html?var=HTTP_AUTHORIZATION')
        self.assertEqual(self.browser.contents, repr('Basic bWdyOm1ncnB3'))

    def test_authorization_persists_over_redirects(self):
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open('http://localhost/redirect.html?to=echo_one.html%3fvar%3dHTTP_AUTHORIZATION')
        self.assertEqual(self.browser.contents, repr('Basic bWdyOm1ncnB3'))

    def test_authorization_other(self):
        # Non-Basic authorization headers are unmolested
        self.browser.addHeader('Authorization', 'Digest foobar')
        self.browser.open('http://localhost/echo_one.html?var=HTTP_AUTHORIZATION')
        self.assertEqual(self.browser.contents, repr('Digest foobar'))
