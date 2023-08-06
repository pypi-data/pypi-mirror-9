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
"""Webtest browser
"""
__docformat__ = "reStructuredText"

import sys
import re
import time
import json
import io
import os
import webbrowser
import tempfile
import wsgiproxy.proxies
from contextlib import contextmanager

import lxml.etree
import lxml.html

from bs4 import BeautifulSoup
from six.moves import urllib_robotparser

from zope.interface import implementer
from zope.cachedescriptors.property import Lazy

from p01.testbrowser import interfaces
from p01.testbrowser._compat import httpclient
from p01.testbrowser._compat import PYTHON2
from p01.testbrowser._compat import urllib_request
from p01.testbrowser._compat import urlparse
import p01.testbrowser.cookies
import p01.testbrowser.html2text
import p01.testbrowser.xpath

import webtest
import webtest.forms
import webtest.utils

import p01.testbrowser.app
import p01.testbrowser.control
import p01.testbrowser.exceptions
from p01.testbrowser.control import disambiguate
from p01.testbrowser.control import controlFormTupleRepr
from p01.testbrowser.control import zeroOrOne
from p01.testbrowser.control import isMatching
from p01.testbrowser.utils import SetattrErrorsMixin


###############################################################################
#
# container for controls outside form tag

class ControlsWithoutForm(webtest.forms.Form):
    """Dummy control container for all controls outside a form"""

    def __init__(self, response, text, parser_features='html.parser'):
        self.response = response
        # remove all form tags
        self.html = BeautifulSoup(text, parser_features)
        for tag in self.html.select('form'):
            tag.extract()
        self.text = self.html.prettify()
        self.action = None
        self.method = None
        self.id = None
        self.enctype = None
        self._parse_fields()

    def submit(self, name=None, index=None, value=None, **args):
        """Can't submit this form without a form tag"""
        raise p01.testbrowser.exceptions.BrowserStateError(
            "Can't submit a control without a form tag")

    def upload_fields(self):
        """Return a list of file field tuples"""
        return []


###############################################################################
#
# timer

class PystoneTimer(object):
    start_time = 0
    end_time = 0
    _pystones_per_second = None

    @property
    def pystonesPerSecond(self):
        """How many pystones are equivalent to one second on this machine"""

        # deferred import as workaround for Zope 2 testrunner issue:
        # http://www.zope.org/Collectors/Zope/2268
        from test import pystone
        if self._pystones_per_second == None:
            self._pystones_per_second = pystone.pystones(pystone.LOOPS//10)[1]
        return self._pystones_per_second

    def _getTime(self):
        if sys.platform.startswith('win'):
            # Windows' time.clock gives us high-resolution wall-time
            return time.clock()
        else:
            # everyone else uses time.time
            return time.time()

    def start(self):
        """Begin a timing period"""
        self.start_time = self._getTime()
        self.end_time = None

    def stop(self):
        """End a timing period"""
        self.end_time = self._getTime()

    @property
    def elapsedSeconds(self):
        """Elapsed time from calling `start` to calling `stop` or present time

        If `stop` has been called, the timing period stopped then, otherwise
        the end is the current time.
        """
        if self.end_time is None:
            end_time = self._getTime()
        else:
            end_time = self.end_time
        return end_time - self.start_time

    @property
    def elapsedPystones(self):
        """Elapsed pystones in timing period

        See elapsed_seconds for definition of timing period.
        """
        return self.elapsedSeconds * self.pystonesPerSecond


    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()


###############################################################################
#
# avticity

class RelativeURLMixin(object):
    """Relative url mixin class"""

    browser = None

    def getRelativURL(self, url):
        # get relative url for given url
        if url and self.browser is not None:
            bURL = self.browser._getBaseUrl()
            parsed = urlparse.urlparse(bURL)
            baseURL = '%s://%s' % (parsed.scheme, parsed.netloc)
            if url == baseURL:
                url = '/'
            else:
                url = url.replace(baseURL, '')
        return url

    def simplify(self, content):
        # replace all kind of relative url in a string
        if content and self.browser is not None:
            bURL = self.browser._getBaseUrl()
            parsed = urlparse.urlparse(bURL)
            baseURL = '%s://%s' % (parsed.scheme, parsed.netloc)
            baseAndSpace = '%s ' % baseURL
            baseAndSpaceWithSlash = '%s/ ' % baseURL
            if content.endswith(baseURL):
                # one more special case if message ends with base url but
                # has no space at the end
                # e.g. <open http://127.0.0.1:8080>
                content = content[:-len(baseURL)]
                content += '/'
            content = content.replace(baseAndSpaceWithSlash, '/ ')
            content = content.replace(baseAndSpace, '/ ')
            content = content.replace(baseURL, '')
        return content


class Activity(RelativeURLMixin):
    """Generic activity supporting a mesage and kw args.

    You can simply use a representation string as message and optional
    include any keyword data which can get represented as string. We will
    render the given message inclding the optional data.

    """

    def __init__(self, msg, **data):
        self.msg = msg
        self.data = data

    def render(self, prettify=False):
        """Represent activity"""
        data = {}
        for k, v in self.data.items():
            try:
                # convert to string
                v = '%s' % v
            except Exception, e:
                # mark as failed
                v = 'NOSTRING'
            data[k] = v
        msg = self.msg % data
        return '<%s>' % self.simplify(msg)

    def __repr__(self):
        return self.render(prettify=False)


class DocumentReadyActivity(object):
    """Document ready activity"""

    def __init__(self, browser):
        self._dom = browser._dom

    def render(self, prettify=False):
        """Represent activity"""
        return '<DOCUMENT ready %s>' % len(self._dom)

    def __repr__(self):
        return self.render(prettify=False)


class RequestActivity(object):
    """RequestActivity entry"""

    def __init__(self, response, dom, title=None):
        self.response = response
        self.dom = dom
        self.title = title

    def render(self, prettify=False):
        """Represent activity"""
        # request
        if self.response.request.path:
            path = ' %s' % self.response.request.path
        else:
            path = ' /'
        if self.response.request.content_type:
            # POST request
            ct = ' %s' % self.response.request.content_type
        else:
            # GET request
            ct = ''
        # response
        if self.response.content_type:
            rct = ' %s' % self.response.content_type
        else:
            rct = ''
        if self.response.body:
            body = ' %s' % len(self.response.body)
        else:
            body = ' no body'
        # return request/response representation
        req = '%s%s%s' % (self.response.request.method, path, ct)
        resp =  '%s%s%s' %(self.response.status, rct, body)
        if prettify and len(req + resp) > 70:
            space = ' ' * (len(self.response.request.method) + 2)
            resp = '\n%s%s' % (space, resp)
        else:
            resp = ' %s' % resp
        if prettify:
            return '<%s%s>' % (req, resp)
        else:
            return '<%s%s>' % (req, resp)

    def __repr__(self):
        return self.render(prettify=False)


class HistoryPushStateActivity(RelativeURLMixin):
    """Browser history push state cactivity"""

    browser = None

    def __init__(self, data):
        # pushState url and title attributes
        self.url = data.get('url')
        self.title =  data.get('title')
        # j01.jsonrpc.js state data
        self.cbURL =  data.get('cbURL')
        self.method =  data.get('method')
        self.params =  data.get('params')
        self.onSuccess =  data.get('onSuccess')
        self.onError =  data.get('onError')
        self.onTimeout =  data.get('onTimeout')

    def render(self, prettify=False):
        """Represent activity"""
        if self.cbURL:
            if self.params:
                params = ' params:%s' % json.dumps(self.params)
            else:
                params = ''
            cbURL = self.getRelativURL(self.cbURL)
            url = ' %s %s %s' % (self.method, cbURL, params)
        elif self.url:
            url = ' %s' % self.getRelativURL(self.url)
        else:
            url = ' missing url'
        return '<PUSH STATE%s>' % url

    def __repr__(self):
        return self.render(prettify=False)


class HistoryPopStateActivity(RelativeURLMixin):
    """Browser history pop state cactivity"""

    browser = None

    def __init__(self, state=None):
        self.state = state

    def render(self, prettify=False):
        """Represent activity"""
        if self.state:
            if self.state.cbURL:
                if self.state.params:
                    params = ' params:%s' % json.dumps(self.state.params)
                else:
                    params = ''
                cbURL = self.getRelativURL(self.state.cbURL)
                url = ' %s %s%s' % (self.state.method, cbURL, params)
            elif self.state.url:
                url = ' url:%s' % self.getRelativURL(self.state.url)
            else:
                url = ' missing url'
        else:
            url = ''
        return '<POP STATE%s>' % url

    def __repr__(self):
        return self.render(prettify=False)


class Activities(object):
    """Request/response acvitities"""

    def __init__(self, browser):
        self.browser = browser
        # last in first out
        self._data = []

    def clear(self):
        del self._data[:]

    def doAddActivity(self, activity, **data):
        """Add given activity"""
        if isinstance(activity, basestring):
            # add generic activity based on given pattern
            activity = Activity(activity, **data)
        activity.browser = self.browser
        self._data.append(activity)

    def doDocumentReady(self):
        obj = DocumentReadyActivity(self.browser)
        self.doAddActivity(obj)

    # testing helper
    def getActivities(self, prettify=True):
        """Get the activity history"""
        if prettify:
            for entry in self._data:
                print entry.render(prettify=True)
        else:
            return self._data

    def __repr__(self):
        return '<%s len=%s>' % (self.__class__.__name__, len(self._data))


class ActivitiesMixin(object):
    """Activites mixin class"""

    activities = None

    def __init__(self):
        # setup activities
        super(ActivitiesMixin, self).__init__()
        self.activities = Activities(self)

    def doAddActivity(self, activity, **data):
        self.activities.doAddActivity(activity, **data)

    def doDocumentReady(self):
        self.activities.doDocumentReady()

    def getActivities(self, prettify=True):
        return self.activities.getActivities(prettify)


###############################################################################
#
# history

class HistoryEntry(object):
    """History entry"""

    def __init__(self, response, dom, state=None, title=None, url=None):
        self.response = response
        self.dom = dom
        self.state = state
        self.title = title
        self.url = url

    def render(self, prettify=False):
        """Represent activity"""
        # request
        if self.response.request.path:
            path = ' %s' % self.response.request.path
        else:
            path = ' /'
        if self.response.request.content_type:
            # POST request
            ct = ' %s' % self.response.request.content_type
        else:
            # GET request
            ct = ''
        # response
        if self.response.content_type:
            rct = ' %s' % self.response.content_type
        else:
            rct = ''
        if self.response.body:
            body = ' %s' % len(self.response.body)
        else:
            body = ' no body'
        # return request/response representation
        req = '%s%s%s' % (self.response.request.method, path, ct)
        resp =  '%s%s%s' %(self.response.status, rct, body)
        if prettify and len(req + resp) > 70:
            space = ' ' * (len(self.response.request.method) + 2)
            resp = '\n%s%s' % (space, resp)
        else:
            resp = ' %s' % resp
        if prettify:
            return '<%s%s>' % (req, resp)
        else:
            return '<%s%s>' % (req, resp)

    def __repr__(self):
        return self.render(prettify=False)


class J01HistoryState(object):
    """History state implementation like given in j01.history.js"""

    def __init__(self, data):
        # pushState url and title attributes
        self.url = data.get('url')
        self.title =  data.get('title')
        # j01.jsonrpc.js state data
        self.cbURL =  data.get('cbURL')
        self.method =  data.get('method')
        self.params =  data.get('params')
        self.onSuccess =  data.get('onSuccess')
        self.onError =  data.get('onError')
        self.onTimeout =  data.get('onTimeout')
        self.timestamp = time.time()


class HTML5History(object):
    """HTML5 history simulation

    Note: this implementaiton provides the javascript history concept
    implemented as j01.history.js from the j01.jsonrpc package.
    This loosly implementes the HTML5 browser history api and offers
    processing jsonrpc requests on pop state events which are simulated
    with the history back and go and onpopstate methods.

    You can simple call browser.goBack or browser.goForward for navigate
    with the history api.

    The methods pushState and replaceState are only internal used and
    you probably don't need them for testing.

    The j01.history.js implementation will make sure, that if we load an
    initial page, that the loaded page get added to the history. This allows us
    to navigate allways back to the initial page. This implementation
    will only add a reponse to the history before processing the next request.
    This is because we can access the current response at any and add them
    to the history before make a new request. This is not possible in the
    javascript api.

    HEADSUP: In WebKit browsers, a popstate event would be triggered after
    document's onload event, but Firefox and IE do not have this behavior.
    The j01.history.js implementation will block such to early fired events.

    """

    def __init__(self, browser):
        super(HTML5History, self).__init__()
        self.browser = browser
        # last in first out
        self._data = []

    # helpers
    def _add(self, entry):
        self._data.append(entry)

    def clear(self):
        del self._data[:]

    # testing helper
    def getHistory(self, prettify=True):
        """Get the history"""
        if prettify:
            for entry in self._data:
                print entry.render(prettify=True)
        else:
            return self._data

    # html5 api
    def pushState(self, response, dom, state=None, title=None, url=None):
        """Add history entry after each response"""
        if response is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "Already at start of history")
        # setup state
        entry = HistoryEntry(response, dom, state, title, url)
        self._add(entry)

    def replaceState(self, state, title, url):
        """Replace current (lastest) history entry"""
        # get current (latest) history entry
        try:
            old = self._data.pop()
        except IndexError:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "Already at start of history")
        # set old response as current response
        self.browser.doResponse(old.response)
        # create and add new history entry
        entry = HistoryEntry(old.response, old.dom, state, title, url)
        self._add(old)

    # browser back/forward buttons
    def back(self, n):
        """Go back in history"""
        counter = n
        if n < 1:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "History back method requires a counter larger then: %s" % n)
        entry = None
        while n > 0:
            try:
                entry = self._data.pop()
            except IndexError:
                raise p01.testbrowser.exceptions.BrowserStateError(
                    "Already at start of history")
            n -= 1
        if entry is not None:
            # add activity
            msg = 'back %s' % counter
            self.browser.doAddActivity(msg)
            # start pop state
            self.browser.onPopState(entry)
            self.browser.doDocumentReady()
        else:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "Internal browser history setup error, history entry is None")

    def go(self, n):
        """Go forward in history"""
        raise NotImplemented("Going forward in history is not supported yet")
        #self.browser.doDocumentReady()

    def __repr__(self):
        return '<%s len=%s>' % (self.__class__.__name__, len(self._data))


class HTML5HistoryMixin(object):
    """HTML5 history mixin class

    This history implementation simulates the j01.history.js concept. The
    most important thing to know about the j01.history.js concept is that we
    load the page content with j01LoadContent method. This means we can make
    sure that we don't show outdated content for any page.
    """

    # html5 like history
    history = None
    isPushState = None
    isOnPopState = None

    def __init__(self):
        super(HTML5HistoryMixin, self).__init__()
        # setup history
        self.history = HTML5History(self)

    # j01.jsonrpc.js history api
    def j01PushState(self, response, dom, title):
        """Push state handler simulating j01.history.js implementation

        This method knows what's to do if we add a jsonrpc response to the
        history. This method simulates the j01.jsonrpc.js concept given from
        j01.jsonrpc.
        """
        # condition
        if response is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "No response given for push state")
        if self.isPushState is False:
            # marked for skip, reset skip marker
            self.isPushState = None
            return
        if response.content_type.endswith(('+json', '/json')):
            # this simulates a real browser history javacsript pushState call
            data = self.getJSONRPCResult(response)
            if isinstance(data, dict) and data.get('state') is not None:
                # only a dict result can contain a state, some other jsonrpc
                # method return a simple content string etc. This means we
                # can't process a history state
                # override given title and url
                title = data.get('stateTitle')
                url = data.get('stateURL')
                # setup state based on given state data
                sData = data['state']
                state = J01HistoryState(sData)
                # push state to history
                self.history.pushState(response, dom, state, title, url)
                # add history activity
                obj = HistoryPushStateActivity(sData)
                self.doAddActivity(obj)
        else:
            # this is not a real browser history javascript pushState call
            # but we add all our request/respone to the history
            state = None
            url = response.location
            # push state to history
            self.history.pushState(response, dom, state, title, url)

    def j01PopState(self, state=None):
        """Pop state handler simulating j01.history.js implementation

        This method knows how to process a history state pop'ed from the
        history by calling history.back(count) or browser.goBack(count).
        """
        if state is None:
            # no state given
            return
        # add marker for prevent adding a poping state to get added to the
        # history as a new entry because a poping state is only a
        # re-construction of a page dom and not a new loaded page
        self.isPushState = False
        if state.cbURL:
            # process jsonrpc using the method defined in state
            params = state.params
            if params is None:
                params = self.j01URLToArray(state.cbURL)
            onSuccess = self.j01GetCallback(state.onSuccess)
            onError = self.j01GetCallback(state.onError)
            self.doJSONRPCCall(state.cbURL, state.method, params, onSuccess,
                onError)
        elif state.url:
            # process simple get request. The response state cbURL must
            # explicit set to None for force such a use case.
            self.doRequest('GET', state.url)

    def onPopState(self, entry):
        """Process on pop state handling"""
        # reset response and dom with data given from history entry before
        # processing state. This sounds a bit curios but it is required if we
        # go back more then one page in history which is not possible with
        # the real browser history api. Just make sure we have the right
        # condition for apply the state. In other words this is not relevant
        # and will apply the same data as we already have if you just go one
        # page back.

        # add pop state activity
        obj = HistoryPopStateActivity(entry.state)
        self.doAddActivity(obj)
        # add isOnPopState marker before procesing
        self.isOnPopState = True
        self.doResponse(entry.response)
        self._dom = entry.dom
        # process state
        if entry.state is not None:
            self.j01PopState(entry.state)
        else:
            msg = 'response replaced'
            self.doAddActivity(msg)
        # rest isOnPopState marker
        self.isOnPopState = None

    # testing helper
    def getHistory(self, prettify=True):
        """Returns the history entry items usable for introspection"""
        return self.history.getHistory(prettify)


###############################################################################
#
# j01.jsonrpc methods and callback handler

class JSONRPCCallbackMixin(object):
    """JSONRPC callback methods mixin class"""

    def __init__(self):
        super(JSONRPCCallbackMixin, self).__init__()
        self.j01CallbackRegistry = {}
        # j01.jsonrpc.js allbacks
        self.j01RegisterCallback('j01RenderContent', self.j01RenderContent)
        self.j01RegisterCallback('j01RenderContentSuccess',
            self.j01RenderContentSuccess)
        self.j01RegisterCallback('j01RenderContentError',
            self.j01RenderContentError)
        # j01.jsonrpc.js allbacks
        self.j01RegisterCallback('j01DialogRenderContent',
            self.j01DialogRenderContent)
        self.skipDomInjectionError = False

    # callback registry, see: j01.jsonrpc.js
    def j01RegisterCallback(self, cbName, callback, override=False):
        """Register a callback method"""
        if cbName in self.j01CallbackRegistry and not override:
            raise ValueError(
                "callback method %s already exists. "
                "Use j01OverrideCallback instead of j01RegisterCallback "
                "or use override=true" % cbName)
        self.j01CallbackRegistry[cbName] = callback

    def j01OverrideCallback(self, cbName, callback):
        self.j01CallbackRegistry[cbName] = callback

    def j01GetCallback(self, cbName=None, default=None):
        # get callback by name or return default j01RenderContent method
        if default is None:
            default = self.j01RenderContent
        return self.j01CallbackRegistry.get(cbName, default)

    # generic jsonrpc processing
    def doJSONRPCCall(self, url, method, params, onSuccess=None, onError=None):
        # get params from nextURL
        msg = '%s %s' % (method, url)
        self.doAddActivity(msg)
        data = {
            "jsonrpc": "2.0",
            "id": "j01.jsonrpc.testing",
            "method": method,
            "params": params,
            }
        body = json.dumps(data).encode('utf8')
        self.doPostRequest(url, body, 'application/json-rpc')
        # process response (no onSucces, onError support)
        resp = self._response
        data = self.getJSONRPCResult(resp)
        if onSuccess is None:
            # sync request
            return data
        elif data is not None:
            # async request and onSucces is not None
            msg = '%s onSuccess' % onSuccess.__name__
            self.doAddActivity(msg)
            onSuccess(resp)
        elif data is None and onError is not None:
            # error, data is None and onError is not None
            msg = '%s onError' % onError.__name__
            self.doAddActivity(msg)
            onError(resp)

    # global available j01.jsonrpc.js methods
    def j01LoadContent(self, url):
        method = 'j01LoadContent'
        params = self.j01URLToArray(url)
        onSuccess = self.j01RenderContentSuccess
        onError = self.j01RenderContentError
        self.doJSONRPCCall(url, method, params, onSuccess, onError)

    def j01NextURL(self, url):
        msg = 'nextURL %s' % url
        self.doAddActivity(msg)
        self.doRequest('GET', url)

    def j01NextContentURL(self, url):
        msg = 'nextContentURL %s' % url
        self.doAddActivity(msg)
        self.j01LoadContent(url)

    # j01.jsonrpc.js callbacks
    def j01RenderContentSuccess(self, resp, contentTargetExpression=None):
        """Process render content success response

        This method simulates j01RenderContentSuccess method implemented in the
        j01.jsonrpc.js javascript. We process the result in the following
        order:

        - redirect to nextURL if given

        - load content from nextContentURL into dom

        - render content into dom based on contentTargetExpression

        - apply j01PushState based on response.isPushState marker

        """
        if contentTargetExpression is None:
            contentTargetExpression = '#content'
        data = self.getJSONRPCResult(resp)
        if data.get('nextURL'):
            # process nextURL
            nextURL = data['nextURL']
            self.j01NextURL(nextURL)
        elif data.get('nextContentURL'):
            # load content from nextContentURL
            nextContentURL = data['nextContentURL']
            self.j01NextContentURL(nextContentURL)
        elif data.get('content'):
            # inject content into target
            content = data['content']
            cssSelector = data.get('contentTargetExpression')
            if cssSelector is None:
                cssSelector = contentTargetExpression
            self.doReplaceContent(cssSelector, content)

    def j01RenderContentError(self, resp, errorTargetExpression=None):
        """Process render content error response

        This method simulates j01RenderContentError method implemented in the
        j01.jsonrpc.js javascript. We process the result in the following
        order:

        - redirect to nextURL if given

        - render error message into dom based on errorTargetExpression

        """
        # setup data
        if errorTargetExpression is None:
            errorTargetExpression = '#j01Error'
        rData = self.getJSONRPCError(resp)
        data = rData.get('data', {})
        msg = data.get('i18nMessage')
        if msg is None:
            msg = data.get('message')
        # processing
        if data.get('nextURL'):
            # process nextURL
            nextURL = data['nextURL']
            self.j01NextURL(nextURL)
        else:
            cssSelector = data.get('errorTargetExpression',
                errorTargetExpression)
            try:
                self.doReplaceContent(cssSelector, msg)
            except ValueError, e:
                if not self.skipDomInjectionError:
                    raise ValueError(
                        "j01RenderContentError error, "
                        "The error message could not get injected into dom "
                        "because the css selector '%s' is not available" % \
                        cssSelector)

    def j01RenderContent(self, resp):
        """Process render content success or error response"""
        data = self.getJSONRPCResult(resp)
        if data is not None:
            self.j01RenderContentSuccess(resp, '#content')
        else:
            self.j01RenderContentError(resp, '#j01Error')

    def setUpJ01Dialog(self, content):
        """Setup j01Dialog and insert into dom with given content"""
        if self._dom is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "No page loaded for inject content")
        # remove previous dialog from dom
        try:
            self.doRemoveElement('#j01DialogHolder')
        except ValueError:
            # dialog not found, just ignore
            pass
        # insert new dialog holder including dialog content
        j01DialogHolder = '<div id="j01DialogHolder">%s</div>' % content
        soup = BeautifulSoup(self._dom)
        tags = soup.select('body')
        if len(tags) == 1:
            tag = tags[0]
            part = BeautifulSoup(j01DialogHolder, "html.parser")
            tag.append(part)
            # store new content in dom, let response as is
            self._dom = soup.prettify()
        else:
            raise ValueError("Body tag not found for insert j01Dialog")

    def j01Dialog(self, url):
        """Get dialog by url"""
        method = 'j01Dialog'
        params = self.j01URLToArray(url)
        self.doJSONRPCCall(url, method, params)
        # process sync request response
        resp = self._response
        content = self.getJSONRPCResult(resp)
        if content:
            # setup dialog if content is given otherwise ignore like we do
            # in j01.dialog.js
            self.setUpJ01Dialog(content)
            # add activity
            msg = 'j01Dialog setup %s' % len(content)
            self.doAddActivity(msg)
        else:
            # add activity
            msg = 'j01Dialog missing content -> close'
            self.doAddActivity(msg)

    def j01DialogClose(self, url=None):
        if url is not None:
            msg = 'j01DialogClose %s' % url
        else:
            msg = 'j01DialogClose'
        self.doAddActivity(msg)
        self.doRemoveElement('#j01DialogHolder')
        if url is not None:
            # simply redirect to new page
            self.doRequest('GET', url)
        self.doDocumentReady()

    def j01DialogContent(self, url):
        # get params from nextURL
        method = 'j01LoadContent'
        params = self.j01URLToArray(url)
        onSuccess = self.j01DialogRenderContentSuccess
        onError = self.j01DialogRenderContentError
        self.doJSONRPCCall(url, method, params, onSuccess, onError)

    # j01.dialog.js callbacks and global methods
    def j01DialogRenderContentSuccess(self, resp, contentTargetExpression=None):
        """Process dialog render content success response

        This method simulates j01DialogRenderContentSuccess method implemented
        in the j01.dialog.js javascript. We process the result in the following
        order:

        - close dialog and redirect to nextURL if closeDialog=True in result

        - load content from nextURL into dialog if closeDialog=False in result

        - render result.content into page dom if closeDialog=True

          - use #content as default id if no contentTargetExpression is given

        - close dialog if closeDialog=True

        - render result.content into dialog if closeDialog=False

        """
        if contentTargetExpression is None:
            contentTargetExpression = '#content'
        data = self.getJSONRPCResult(resp)
        nextURL = data.get('nextURL')
        content = data.get('content')
        closeDialog = data.get('closeDialog')
        nextURL = data.get('nextURL')

        # handle error
        if nextURL and closeDialog:
            # close dialog and redirect
            self.doRemoveElement('#j01DialogHolder')
            self.j01NextURL(nextURL)
        elif nextURL:
            # load content from nextURL into dialog
            self.j01DialogContent(nextURL)
        elif content and closeDialog:
            # load content into page dom
            cssSelector = data.get('contentTargetExpression')
            if cssSelector is None:
                cssSelector = contentTargetExpression
            self.doReplaceContent(cssSelector, content)
        elif content:
            # load content into dialog
            cssSelector = '#j01DialogContent'
            self.doReplaceContent(cssSelector, content)
        elif closeDialog:
            # close dialog
            self.doRemoveElement('#j01DialogHolder')
        else:
            # no supported use case
            pass

    def j01DialogRenderContentError(self, resp, errorTargetExpression=None):
        """Process dialog render content error response

        This method simulates j01DialogRenderContentError method implemented in
        the j01.jsonrpc.js javascript. We process the result in the following
        order:

        - redirect to nextURL if given

        - render error message into dom using '#j01DialogContent' css selector

        """
        # setup data
        if errorTargetExpression is None:
            errorTargetExpression = '#j01DialogContent'
        rData = self.getJSONRPCError(resp)
        data = rData.get('data', {})
        msg = data.get('i18nMessage')
        if msg is None:
            msg = data.get('message')
        # processing
        if data.get('nextURL'):
            # process nextURL
            nextURL = data['nextURL']
            self.j01NextURL(nextURL)
        else:
            # load content into dialog
            cssSelector = '#j01DialogContent'
            self.doReplaceContent(cssSelector, msg)

    def j01DialogRenderContent(self, resp):
        """Process dialog render content success or error response"""
        data = self.getJSONRPCResult(resp)
        if data is not None:
            self.j01DialogRenderContentSuccess(resp, '#content')
        else:
            self.j01DialogRenderContentError(resp)


class JSONRPCMixin(object):
    """Supports j01.jsonrpc button processing"""

    # helper methods
    def j01URLToArray(self, url):
        """Rerturns json-rpc params based on url query or an empty dict"""
        if url:
            parsed = urlparse.urlparse(url)
            query = parsed.query
            data = urlparse.parse_qs(query)
            # convert single items to values
            params = {}
            for k, v in urlparse.parse_qs(query).iteritems():
                if k.endswith(':list'):
                    # marked as list
                    params[k] = v
                elif len(v) > 1:
                    # more then one value, keep list
                    params[k] = v
                else:
                    # single value as string
                    params[k] = v[0]
            return params
        else:
            return {}

    def j01FormToArray(self, form, j01FormHandlerName):
        """Rerturns widget values and j01FormHandlerName as json-rpc params

        NOTE: the j01FormHandlerName is the button name without prefixes.
        """
        params = {}
        for name, value in form._form.submit_fields():
            if name.endswith(':list'):
                # ok that's a list
                values = params.setdefault(name, [])
                values.append(value)
            elif name in params:
                # ok that's a list but no :list marker
                values = params[name]
                if not isinstance(values, list):
                    values = [values]
                values.append(value)
                params[name] = values
            else:
                params[name] = value
        # apply handler (button.__name__) name
        params['j01FormHandlerName'] = j01FormHandlerName
        return params

    def doRemoveElement(self, cssSelector):
        """Remove content from the dom"""
        if self._dom is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "No page loaded for remove element")
        soup = BeautifulSoup(self._dom)
        tags = soup.select(cssSelector)
        if len(tags) < 1:
            raise ValueError("No tag found for remove element")
        elif len(tags) > 1:
            raise ValueError("More then one tag found for remove element")
        else:
            tag = tags[0]
            tag.extract()
            # simply store new content in dom
            self._dom = soup.prettify()
            # add activity
            msg = 'DOM remove %s' % cssSelector
            self.doAddActivity(msg)

    def doRemoveContent(self, cssSelector):
        """Remove content from the dom"""
        if self._dom is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "No page loaded for remove content")
        soup = BeautifulSoup(self._dom)
        tags = soup.select(cssSelector)
        if len(tags) < 1:
            raise ValueError("No tag found for remove content")
        elif len(tags) > 1:
            raise ValueError("More then one tag found for remove content")
        else:
            tag = tags[0]
            tag.clear()
            # simply store new content in dom
            self._dom = soup.prettify()
            # add activity
            msg = 'DOM empty %s' % cssSelector
            self.doAddActivity(msg)

    def doReplaceContent(self, cssSelector, content):
        """Replace content in dom

        NOTE: this method is used by j01.jsonrpc.testing for inject
        jsonrpc response.

        NOTE: we can't use the last response because it could be partial
        jsonrpc response data. Use the html content stored in our _dom property
        which is always a real html page content

        """
        if self._dom is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "No page loaded for inject content")
        soup = BeautifulSoup(self._dom)
        tags = soup.select(cssSelector)
        if len(tags) < 1:
            raise ValueError(
                "No tag found by selector '%s' for insert content" % \
                cssSelector)
        elif len(tags) > 1:
            raise ValueError(
                "More then one tag found by selector '%s' for insert content" \
                % cssSelector)
        else:
            tag = tags[0]
            tag.clear()
            part = BeautifulSoup(content, "html.parser")
            tag.append(part)
            # store new content in dom
            # Note: we do NOT store the new content as response. We should
            # implement a html5 browser history which is able to re-call any
            # history based on a given state and some handler methods.
            self._dom = soup.prettify()
            msg = 'DOM replace %s %s' % (cssSelector, len(content))
            self.doAddActivity(msg)

    # helper methods
    def getJSONRPCResponse(self, response=None, skipErrors=False):
        # get json data from webtest response
        if response is None:
            response = self._response
        try:
            # Note: the reponse instance can't load json data for non
            # application/json content types e.g. application/x-javascript
            # or application/x-json will fail. Just load them directly from
            # the test body
            data = json.loads(response.testbody)
        except Exception, e:
            if not skipErrors:
                raise e
        try:
            if not data and not skipErrors:
                # raise server response error
                raise interfaces.JSONRPCResponseError(
                    'Missing json response data')
            else:
                return data
        except Exception, e:
            if not skipErrors:
                raise interfaces.JSONRPCResponseError(self.body)

    def getJSONRPCResult(self, response=None, skipErrors=False):
        """Returns response result or None"""
        try:
            data = self.getJSONRPCResponse(response)
            return data.get('result')
        except Exception, e:
            if not skipErrors:
                raise e

    def getJSONRPCError(self, response=None, skipErrors=False):
        """Returns response error or None"""
        try:
            data = self.getJSONRPCResponse(response, skipErrors)
            return data.get('error')
        except Exception, e:
            if not skipErrors:
                raise e


###############################################################################
#
# helper methods mixin

class BrowserHelperMixin(object):
    """Broser testing helper mixin class"""

    def openInBrowser(self, opener=webbrowser.open):
        """Open the given content in a local web browser"""
        if isinstance(self.contents, unicode):
            contents = self.contents.encode('utf8')
        else:
            contents = self.contents
        fd, fname = tempfile.mkstemp('.html')
        os.write(fd, contents)
        os.close(fd)
        return opener("file://%s" % fname)


###############################################################################
#
# test browser

@implementer(interfaces.IBrowser)
class Browser(p01.testbrowser.control.ControlFactoryMixin, JSONRPCMixin,
    JSONRPCCallbackMixin, ActivitiesMixin, HTML5HistoryMixin,
    BrowserHelperMixin, SetattrErrorsMixin):
    """A web browser

    NOTE: the current history implementation stores each response, This is not
    what we should do. We should implement a html5 brwoser history api and only
    store a state with title and url and process them again if we go back.
    This is not as easy as it sounds because the html5 history api stores
    a state which can be any data and javascript handler can get used for
    processing state changes. This means we don't really know what the
    application is doing. Take a look at the j01/jsonrpc/js/j01.jsonrpc.js
    and try to implement a generic concept for support custom state data
    and methods for preocess them see: callbackName, j01PopState and
    j01PushState as a sample concept we need to provide.

    The current implementation uses the following internal response values:

    _response, contains the latest response for any request

    _raw, contains the latest non html response.body

    _dom, contains the latest html response.body

    _title, contains the latest html title from response.body

    Note, this internal private attributes will probably change in the future
    if we implement a better history concept.

    Note: our test browser supports controls outside a form tag. But this
    doesn't mean that they can get submitted without javascript involved.
    We just make sure that we can access controls located outside a form tag
    using a dummy control container called ControlsWithoutForm.

    """

    # hold the initial response content as dom for future ajax injection
    _json = None
    _raw = None
    _forms = None
    _title = None
    # private, read and write via _dom
    __dom = None
    # lxml
    _etree = None

    # _contents seems not get used in this implementation
    _contents = None
    _controls = None
    _counter = 0
    _response = None
    _req_headers = None
    _req_content_type = None

    def __init__(self, url=None, wsgi_app=None, getFormControl=None,
        getLinkControl=None, getClickableControl=None):
        super(Browser, self).__init__()
        self.timer = PystoneTimer()
        self.raiseHttpErrors = True
        self.handleErrors = True
        if wsgi_app is None:
            proxy = wsgiproxy.proxies.TransparentProxy()
            self.testapp = p01.testbrowser.app.TestApp(proxy)
        else:
            self.testapp = p01.testbrowser.app.TestApp(wsgi_app)
            self.testapp.restricted = True
        self._req_headers = {}
        self._enable_setattr_errors = True
        if getFormControl is not None:
            self.getCustomFormControl = getFormControl
        if getLinkControl is not None:
            self.getCustomLinkControl = getLinkControl
        if getClickableControl is not None:
            self.getCustomClickableControl = getClickableControl
        self._controls = {}
        self.__dom = None
        if url is not None:
            self.doRequest('GET', url)
            self.doDocumentReady()

    @property
    def url(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        if self._response is None:
            return None
        return self.testapp.getRequestUrlWithFragment(self._response)

    @property
    def isHtml(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        return self._response and 'html' in self._response.content_type

    @property
    def lastRequestPystones(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        return self.timer.elapsedPystones

    @property
    def lastRequestSeconds(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        return self.timer.elapsedSeconds

    def getTitle(self):
        """Return title from current text/html response"""
        if self.isHtml:
            titles = self._html.find_all('title')
            if titles:
                return self.toStr(titles[0].text)

    @property
    def title(self):
        # get title given from latest text/html response, see doProcessRequest
        return self._title

    def doRedirect(self, url, response):
        """Process redirect without _response caching"""
        # infinite loops protection
        remaining = 100
        while 300 <= response.status_int < 400 and remaining:
            remaining -= 1
            url = urlparse.urljoin(url, response.headers['location'])
            # add activity
            msg = 'redirect %s' % url
            self.doAddActivity(msg)
            # process redirect
            with self._preparedRequest(url) as reqargs:
                response = self.testapp.get(url, **reqargs)
        assert remaining > 0, "redirects chain looks infinite"
        return response

    def doCheckStatus(self):
        # if the headers don't have a status, I suppose there can't be an error
        if 'Status' in self.headers:
            code, msg = self.headers['Status'].split(' ', 1)
            code = int(code)
            if self.raiseHttpErrors and code >= 400:
                raise urllib_request.HTTPError(self.url, code, msg, [], None)

    def getStatus(self):
        # if the headers don't have a status, I suppose there can't be an error
        if 'Status' in self.headers:
            code, msg = self.headers['Status'].split(' ', 1)
            return int(code)
        else:
            # no status header means success
            return 200

    def doResponse(self, response):
        """Set response after processing or history back

        NOTE: this method knows what's to do if we get a json response
        """
        # setup response and make charset available for encoding
        self._response = response
        # reset raw content on each request/response
        self._raw = None
        self._json = None
        if response.body and response.content_type in ['text/html']:
            # store real html content as dom
            self._dom = self.toStr(response.body)
        elif response.body:
            # store response body as raw content
            self._raw = response.body
            if response.content_type.endswith((
                '/json', '+json', '/x-json', '/javascript', '/x-javascript')):
                # store response body as json content. Note, the response can't
                # load json data for non 'application/json' headers. just load
                # them here
                self._json = json.loads(response.testbody)

    @apply
    def _dom():
        def fget(self):
            return self.__dom
        def fset(self, value):
            self.__dom = value
            # reset parsed forms on dom change
            self._forms = None
            # set title based on new _dom content
            self._title = self.getTitle()
            # reset lxml etree
            self._etree = None
        return property(fget, fset)

    def _changed(self):
        self._counter += 1
        self._contents = None
        self._controls = {}
        for k in self._req_headers.keys():
            # remove headers but keep Authorization and Accept-Language
            if k not in ['Authorization', 'Accept-Language']:
                del self._req_headers[k]
        self._req_content_type = None
        # reset skip push state marker
        self.isPushState = None

    @contextmanager
    def _preparedRequest(self, url):
        self.timer.start()

        headers = {}
        if self.url:
            headers['Referer'] = self.url

        if self._req_content_type:
            headers['Content-Type'] = self._req_content_type

        headers['Connection'] = 'close'
        headers['Host'] = urlparse.urlparse(url).netloc
        headers['User-Agent'] = 'Python-urllib/2.7'

        headers.update(self._req_headers)

        extra_environ = {}
        if self.handleErrors:
            extra_environ['paste.throw_errors'] = None
            extra_environ['wsgi.handleErrors'] = True
            headers['X-zope-handle-errors'] = 'True'
        else:
            extra_environ['paste.throw_errors'] = True
            extra_environ['wsgi.handleErrors'] = False
            extra_environ['x-wsgiorg.throw_errors'] = True
            headers.pop('X-zope-handle-errors', None)

        kwargs = {'headers': sorted(headers.items()),
                  'extra_environ': extra_environ,
                  'expect_errors': True}

        yield kwargs

        self._changed()
        self.timer.stop()

    def doProcessRequest(self, url, make_request):
        with self._preparedRequest(url) as reqargs:
            # add previous response to history
            if self._response is not None:
                # only if an initial request was made
                self.j01PushState(self._response, self._dom, self._title)
            # process request
            resp = make_request(reqargs)
            # process redirect if any
            resp = self.doRedirect(url, resp)
            # apply response
            self.doResponse(resp)
            # check status
            self.doCheckStatus()
            # add activity
            activity = RequestActivity(resp, self._dom, self._title)
            self.doAddActivity(activity)

    def addHeader(self, key, value):
        """See p01.testbrowser.interfaces.IBrowser"""
        if (self.url and
            key.lower() in ('cookie', 'cookie2') and
            self.cookies.header):
            raise ValueError('cookies are already set in `cookies` attribute')
        self._req_headers[key] = value

    def doRequest(self, method, url, data=None, headers=None):
        """Proces a request based on given request method"""
        method = method.upper()
        url = self._absoluteUrl(url)
        if headers is not None:
            for k, v in headers.items():
                self.addHeader(k, v)
        if method == 'GET':
            make_request = lambda args: self.testapp.get(url, **args)
        elif method == 'HEAD':
            make_request = lambda args: self.testapp.head(url, **args)
        elif method == 'OPTIONS':
            make_request = lambda args: self.testapp.options(url, **args)
        elif method == 'POST':
            assert data is not None
            make_request = lambda args: self.testapp.post(url, data, **args)
        elif method == 'PATCH':
            assert data is not None
            make_request = lambda args: self.testapp.patch(url, data, **args)
        elif method == 'PUT':
            assert data is not None
            make_request = lambda args: self.testapp.put(url, data, **args)
        else:
            if data is None:
                params = webtest.utils.NoDefault
            else:
                params = data
            make_request = lambda args: self.testapp._gen_request(method, url,
                params, **args)
        self.doProcessRequest(url, make_request)

    def doGetRequest(self, url):
        """See p01.testbrowser.interfaces.IBrowser"""
        self.doRequest('GET', url)

    def doPostRequest(self, url, data, content_type=None):
        if content_type is not None:
            self._req_content_type = content_type
        self.doRequest('POST', url, data)

    def request(self, method, url, data=None, headers=None):
        """Generic request handling including document ready handling"""
        msg = 'request %s %s' % (method.upper(), url)
        self.doAddActivity(msg)
        self.doRequest(method, url, data=data, headers=headers)
        self.doDocumentReady()

    def get(self, url):
        """GET request including document ready handling"""
        msg = 'get %s' % url
        self.doAddActivity(msg)
        self.doGetRequest(url)
        self.doDocumentReady()

    def post(self, url, data, content_type=None):
        """POST request including document ready handling"""
        msg = 'post %s' % url
        self.doAddActivity(msg)
        self.doPostRequest(url, data, content_type=content_type)
        self.doDocumentReady()

    def open(self, url, data=None):
        """Generic GET or POST request depending on given data including
        document ready handling
        """
        msg = 'open %s' % url
        self.doAddActivity(msg)
        if data is not None:
            method = 'POST'
        else:
            method = 'GET'
        self.doRequest(method, url, data)
        self.doDocumentReady()

    def reload(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        msg = 'reload %s' % self.url
        self.doAddActivity(msg)
        if self._response is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "No URL has yet been .open()ed")
        req = self._response.request
        with self._preparedRequest(self.url):
            resp = self.testapp.request(req)
            self.doResponse(resp)
        self.doDocumentReady()

    def goBack(self, count=1):
        """See p01.testbrowser.interfaces.IBrowser"""
        self.history.back(count)

    def goForward(self, count=1):
        """See p01.testbrowser.interfaces.IBrowser"""
        self.history.go(count)

    # browser content data
    @property
    def _html(self):
        # internal used adhoc parsed dom as BeautifulSoup
        return BeautifulSoup(self._dom, 'html.parser')

    @property
    def raw(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        # returns the raw response.body data
        return self._raw

    @property
    def json(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        # returns the encoded response.body data
        return self._json

    @property
    def body(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        # return the current (latest) encoded response body
        if self._response is not None:
            return self.toStr(self._response.body)
        else:
            return None

    @property
    def contents(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        # return the html stored in the _dom instead of the response.body
        # because the response.body could be partial jsonrpc content
        # NOTE: this means we can't use contents as server response because
        # the jsonrpc respoonse is not returned. Use the raw or json method
        # for access the jsonrpc response.body
        return self._dom

    @property
    def soup(self):
        """Returns the current self._dom as BeautifulSoup using a html.parser"""
        return self._html

    @property
    def headers(self):
        """See p01.testbrowser.interfaces.IBrowser"""
        resptxt = []
        resptxt.append('Status: %s' % self._response.status)
        for h, v in sorted(self._response.headers.items()):
            resptxt.append(str("%s: %s" % (h, v)))

        inp = '\n'.join(resptxt)
        stream = io.BytesIO(inp.encode('latin1'))
        if PYTHON2:
            return httpclient.HTTPMessage(stream)
        else:
            return httpclient.parse_headers(stream)

    @property
    def cookies(self):
        if self.url is None:
            raise RuntimeError("No request found")
        return p01.testbrowser.cookies.Cookies(self.testapp, self.url,
            self._req_headers)

    # links
    def getLink(self, text=None, url=None, id=None, index=0):
        """See p01.testbrowser.interfaces.IBrowser"""
        qa = 'a' if id is None else 'a#%s' % id
        qarea = 'area' if id is None else 'area#%s' % id
        html = self._html
        links = html.select(qa)
        links.extend(html.select(qarea))

        # find matching elements
        matching = []
        for elem in links:
            if (isMatching(elem.text, text) and
                isMatching(elem.get('href', ''), url)):
                matching.append(elem)

        if index >= len(matching):
            raise p01.testbrowser.exceptions.LinkNotFoundError()
        elem = matching[index]

        # setup link control
        link = self.getCustomLinkControl(elem)
        if link is None:
            link = self.getJSONRPCLinkControl(elem)
        if link is None:
            link = p01.testbrowser.control.Link(self, elem)
        return link

    def follow(self, *args, **kw):
        """Select a link and follow it."""
        self.getLink(*args, **kw).click()

    # clickable
    def getClickable(self, text=None, url=None, id=None, index=0):
        """See p01.testbrowser.interfaces.IBrowser"""
        # filter by id
        html = self._html
        if id is not None:
            selector = '#%s' % id
            elements = html.select(selector)
        else:
            elements = html

        # lookup clickables
        clickables = []
        for elem in elements:
            # check custom clickable control
            clickable = self.getCustomClickableControl(elem, text, url)
            if clickable is not None:
                clickables.append(clickable)
                continue
            # check available jsonrpc clickable control
            clickable = self.getJSONRPCClickableControl(elem, text, url)
            if clickable is not None:
                clickables.append(clickable)

        # return by index
        if index >= len(clickables):
            raise p01.testbrowser.exceptions.LinkNotFoundError()
        return clickables[index]

    def getForm(self, id=None, name=None, action=None, index=None):
        """See p01.testbrowser.interfaces.IBrowser"""
        zeroOrOne([id, name, action], '"id", "name", and "action"')
        forms = []
        allforms = self._getAllResponseForms()
        for form in allforms:
            if not form.html.form:
                # that's our dummy control container form we do not allow to
                # get them as form
                continue
            if ((id is not None and form.id == id) or
                (name is not None and form.html.form.get('name') == name) or
                (action is not None and re.search(action, form.action)) or
                id == name == action == None):
                forms.append(form)
        if index is None and not any([id, name, action]):
            if len(forms) == 1:
                index = 0
            else:
                raise ValueError(
                    'if no other arguments are given, index is required.')
        form = disambiguate(forms, '', index)
        return p01.testbrowser.control.Form(self, form)

    def getControl(self, label=None, name=None, index=None):
        """See p01.testbrowser.interfaces.IBrowser"""
        intermediate, msg, available = self._getAllControls(
            label, name, self._getAllResponseForms(),
            include_subcontrols=True)
        control = disambiguate(intermediate, msg,
            index, controlFormTupleRepr, available)
        return control

    def getControls(self, render=False, prettify=False):
        """Return all available controls for current _dom"""
        forms = self._getAllResponseForms()
        include_subcontrols = True
        controls = self._findAllControls(forms, include_subcontrols)
        if render:
            for entry in controls:
                print entry.render(prettify=prettify)
        else:
            return controls

    def getControlsOutsideForm(self, render=False, prettify=False):
        """Return all available controls outside a form"""
        # first ensure forms and get our dummy form
        forms = self._getAllResponseForms()
        forms = [self._forms[None]]
        include_subcontrols = True
        controls = self._findAllControls(forms, include_subcontrols)
        if render:
            for entry in controls:
                print entry.render(prettify=prettify)
        else:
            return controls

    def getLinks(self, render=False, prettify=False):
        """Return all available links for current _dom"""
        # include a and area elements
        qa = 'a'
        qarea = 'area'
        html = self._html
        links = self.soup.select(qa)
        links.extend(html.select(qarea))
        controls = []
        for elem in links:
            # setup link control
            ctrl = self.getCustomLinkControl(elem)
            if ctrl is None:
                ctrl = self.getJSONRPCLinkControl(elem)
            if ctrl is None:
                ctrl = p01.testbrowser.control.Link(self, elem)
            controls.append(ctrl)
        if render:
            for entry in controls:
                print entry.render(prettify=prettify)
        else:
            return controls

    @property
    def controls(self):
        return self.getControls(render=False, prettify=False)

    def _getAllResponseForms(self):
        """Return set of response forms in the order they appear in the dom"""
        if self._forms is None:
            self._forms = {}
            form_texts = [str(f) for f in self._html('form')]
            for i, text in enumerate(form_texts):
                # ATTENTION: the form uses self._response, but luckily the
                # response is only used for submit the form with response.goto
                # But we don't use form.goto for submit the form
                form = webtest.forms.Form(self._response, text, 'html.parser')
                self._forms[i] = form
                if form.id:
                    self._forms[form.id] = form

            # add dummy control container for controls outside a form
            text = self._dom
            self._forms[None] = ControlsWithoutForm(self._response, text)

        idxkeys = [k for k in self._forms.keys() if isinstance(k, int)]
        # return forms with ids and append our non form control container form
        forms = [self._forms[k] for k in sorted(idxkeys)]
        forms.append(self._forms[None])
        return forms

    # internal control helpers
    def _getAllControls(self, label, name, forms, include_subcontrols=False):
        p01.testbrowser.control.onlyOne([label, name], '"label" and "name"')
        forms = list(forms) # might be an iterator, and we need to iterate twice
        available = None
        if label is not None:
            res = self._findByLabel(label, forms, include_subcontrols)
            msg = 'label %r' % label
        elif name is not None:
            include_subcontrols = False
            res = self._findByName(name, forms)
            msg = 'name %r' % name
        if not res:
            available = list(self._findAllControls(forms, include_subcontrols))
        return res, msg, available

    def _findByLabel(self, label, forms, include_subcontrols=False):
        # forms are iterable of mech_forms
        label = ' '.join(label.split())
        matches = re.compile(r'(^|\b|\W)%s(\b|\W|$)' % re.escape(label)).search
        found = []
        for wtcontrol in self._findAllControls(forms, include_subcontrols):
            for l in wtcontrol.labels:
                if matches(l):
                    found.append(wtcontrol)
                    break
        return found

    def _indexControls(self, form=None):
        # Unfortunately, webtest will remove all 'name' attributes from
        # form.html after parsing. But we need them (at least to locate labels
        # for radio buttons). So we are forced to reparse part of html, to
        # extract elements.
        soup = BeautifulSoup(form.text)
        tags = ('input', 'select', 'textarea', 'button')
        return soup.find_all(tags)

    def _findByName(self, name, forms):
        return [c for c in self._findAllControls(forms) if c.name == name]

    def _findAllControls(self, forms, include_subcontrols=False):
        res = []
        for f in forms:
            if f not in self._controls:
                fc = []
                allelems = self._indexControls(f)
                already_processed = set()
                for cname, wtcontrol in f.field_order:
                    # we need to group checkboxes by name, but leave
                    # the other controls in the original order,
                    # even if the name repeats
                    if isinstance(wtcontrol, webtest.forms.Checkbox):
                        if cname in already_processed:
                            continue
                        already_processed.add(cname)
                        wtcontrols = f.fields[cname]
                    else:
                        wtcontrols = [wtcontrol]
                    for c in self.getFormControls(cname, wtcontrols, allelems):
                        fc.append((c, False))
                        for subcontrol in c.controls:
                            fc.append((subcontrol, True))
                self._controls[f] = fc
            controls = [c for c, subcontrol in self._controls[f]
                        if not subcontrol or include_subcontrols]
            res.extend(controls)
        return res

    # internal request/response helper methods
    def _getBaseUrl(self):
        # Look for <base href> tag and use it as base, if it exists
        url = self._response.request.url
        if b"<base" not in self._response.body:
            return url

        # we suspect there is a base tag in body, try to find href there
        html = self._html
        if not html.head:
            return url
        base = html.head.base
        if not base:
            return url
        return base['href'] or url

    def _absoluteUrl(self, url):
        absolute = url.startswith('http://') or url.startswith('https://')
        if absolute:
            return str(url)

        if self._response is None:
            raise p01.testbrowser.exceptions.BrowserStateError(
                "Can't fetch relative reference: not viewing any document")

        return str(urlparse.urljoin(self._getBaseUrl(), url))

    def toStr(self, s):
        """Convert possibly unicode object to native string using response
        charset"""
        if not self._response.charset:
            return s
        if s is None:
            return None
        if PYTHON2 and not isinstance(s, bytes):
            return s.encode(self._response.charset)
        if not PYTHON2 and isinstance(s, bytes):
            return s.decode(self._response.charset)
        return s

    # lxml API
    @property
    def etree(self):
        if self._etree is not None:
            return self._etree
        if self._dom is not None:
            encoding = 'utf-8'
            parser = lxml.etree.HTMLParser(encoding=encoding,
                remove_blank_text=True, remove_comments=True, recover=True)
            self._etree = lxml.etree.fromstring(self._dom, parser=parser)
        return self._etree

    # xpath
    def extract(self, xpath, strip=False, rv=False):
        """Extract content from current _dom by given xpath"""
        if isinstance(self._dom, unicode):
            content = self._dom.encode('utf8')
        else:
            content = self._dom
        xs = p01.testbrowser.xpath.getXPathSelector(content)
        txt = xs.extract(xpath, strip=strip)
        txt = '\n'.join([x.rstrip() for x in txt.splitlines()
                         if x.rstrip().replace('\n', '')])
        if rv:
            return txt
        else:
            print txt

    # text
    def asText(self, xpath='.//body', rv=False):
        """Output current _dom as text by given xpath"""
        if isinstance(self._dom, unicode):
            content = self._dom.encode('utf8')
        else:
            content = self._dom
        res = []
        xs = p01.testbrowser.xpath.getXPathSelector(content)
        for item in xs.xpath(xpath):
            res.append(getNodeText(item))
        txt = '\n'.join(res)
        while '\n\n' in txt:
            txt = txt.replace('\n\n', '\n')
        txt = '\n'.join([x.strip() for x in txt.splitlines()
                         if x.strip().replace('\n', '')])
        if rv:
            return txt
        else:
            print txt

    def asPlainText(self, xpath=None, rv=False, **kw):
        """Output current _dom as text by given xpath"""
        if isinstance(self._dom, unicode):
            content = self._dom.encode('utf8')
        else:
            content = self._dom
        if xpath is not None:
            xs = p01.testbrowser.xpath.getXPathSelector(content)
            content = xs.extract(xpath)
        else:
            conten = self._dom
        txt = p01.testbrowser.html2text.html2text(content, **kw)
        txt = '\n'.join([x.rstrip() for x in txt.splitlines()])
        txt = txt.replace('\n\n', '\n')
        if rv:
            return txt
        else:
            print txt

    def asTable(self, xpath='.//table'):
        if isinstance(self._dom, unicode):
            content = self._dom.encode('utf8')
        else:
            content = self._dom
        xs = p01.testbrowser.xpath.getXPathSelector(content)
        node = xs.xpath(xpath)
        if isinstance(node, (list, tuple)):
            for item in node:
                print "Table:"
                rows = item.xpath('.//tr')
                for row in rows:
                    print map(getNodeText, row.xpath('./th|./td'))
        else:
            rows = node.xpath('.//tr')
            for row in rows:
                print map(getNodeText, row.xpath('./th|./td'))

    # node 2 string
    def node2String(self, xpath, strip=False):
        if isinstance(self._dom, unicode):
            content = self._dom.encode('utf8')
        else:
            content = self._dom
        res = []
        xs = p01.testbrowser.xpath.getXPathSelector(content)
        for node in xs.xpath(xpath):
            node2String(node, res)
        print '\n'.join(res)

    def form2String(self, selector=None):
        selector = [
            # widgets
            './/input[@type="text"]',
            './/input[@type="email"]',
            './/input[@type="url"]',
            './/input[@type="password"]',
            './/input[@type="date"]',
            './/input[@type="datetime"]',
            './/input[@type="datetime-local"]',
            './/input[@type="hidden"]',
            './/select',
            './/textarea',
            # status
            './/div[@class="status"]',
            # buttons
            './/input[@type="submit"]',
            './/input[@type="button"]',
            './/input[@type="reset"]',
            './/button',
            ]
        self.asNodes(selector='|'.join(selector))

    def widget2String(self, selector=None):
        selector = [
            './/input[@type="submit"]',
            './/input[@type="text"]',
            './/input[@type="password"]',
            './/input[@type="date"]',
            './/input[@type="hidden"]',
            './/select',
            './/textarea',
            ]
        self.asNodes(selector='|'.join(selector))

    def button2String(self, selector=None):
        selector = [
            './/input[@type="submit"]',
            './/input[@type="button"]',
            './/input[@type="reset"]',
            './/button',
            ]
        self.asNodes(selector='|'.join(selector))

    def link2String(self, selector=None):
        selector = [
            './/a',
            ]
        self.asNodes(selector='|'.join(selector))

    # grep
    def grep(self, pattern, rv=False):
        P = re.compile(pattern)
        res = []
        for line in self._dom.splitlines():
            if P.search(line):
                  res.append(line)
        txt = ''.join(res)
        if rv:
            return txt
        else:
            print txt

    def __contains__(self, value):
        return value in self.contents


def node2String(node, res):
    if isinstance(node, (list, tuple)):
        for item in node:
            node2String(item, res)
    else:
        txt = lxml.etree.tostring(node, pretty_print=True)
        txt = txt.strip()
        while '\n\n' in txt:
            txt = txt.replace('\n\n', '\n')
        if txt:
            res.append(txt)


def getNodeText(node, addTitle=False):
    if isinstance(node, (list, tuple)):
        tags = [getNodeText(child, addTitle).strip() for child in node]
        return '\n'.join()
    text = []
    if node is None:
        return None
    if node.tag == 'script':
        return ''
    if node.tag == 'br':
        return '\n'
    if node.tag == 'input':
        if addTitle:
            #title = node.get('title') or node.get('name') or ''
            title = node.get('name') or ''
            title += ' '
        else:
            title = ''
        if node.get('type') == 'checkbox':
            chk = node.get('checked')
            return title +('[x]' if chk is not None else '[ ]')
        if node.get('type') == 'hidden':
            return ''
        else:
            return '%s[%s]' % (title, node.get('value') or '')
    if node.tag == 'textarea':
        if addTitle:
            #title = node.get('title') or node.get('name') or ''
            title = node.get('name') or ''
            title += ' '
            text.append(title)
    if node.tag == 'select':
        if addTitle:
            #title = node.get('title') or node.get('name') or ''
            title = node.get('name') or ''
            title += ' '
        else:
            title = ''
        option = node.find('option[@selected]')
        return '%s[%s]' % (title, option.text if option is not None else '[    ]')
    if node.tag == 'li':
        text.append('*')

    if node.text:
        text.append(node.text)
    for n, child in enumerate(node):
        s = getNodeText(child, addTitle)
        if s:
            text.append(s)
        if child.tail:
            text.append(child.tail)
    text = ' '.join(text).strip()
    # 'foo<br>bar' ends up as 'foo \nbar' due to the algorithm used above
    text = text.replace(' \n', '\n').replace('\n ', '\n')
    if u'\xA0' in text:
        # don't just .replace, that'll sprinkle my tests with u''
        text = text.replace(u'\xA0', ' ') # nbsp -> space
    if node.tag == 'li':
        text += '\n'
    return text
