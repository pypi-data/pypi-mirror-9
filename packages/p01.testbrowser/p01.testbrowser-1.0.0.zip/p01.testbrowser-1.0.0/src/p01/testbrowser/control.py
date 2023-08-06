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

import webtest
import webtest.forms
import webtest.utils

import p01.testbrowser.app
import p01.testbrowser.exceptions
from p01.testbrowser.utils import SetattrErrorsMixin


###############################################################################
#
# helper methods

def normalizeWhitespace(string):
    return ' '.join(string.split())


def controlFormTupleRepr(wtcontrol):
    return wtcontrol


def disambiguate(intermediate, msg, index, choice_repr=None, available=None):
    if intermediate:
        if index is None:
            if len(intermediate) > 1:
                if choice_repr:
                    msg += ' matches:' + ''.join([
                                '\n  %s' % choice_repr(choice)
                                for choice in intermediate])
                raise p01.testbrowser.exceptions.AmbiguityError(msg)
            else:
                return intermediate[0]
        else:
            try:
                return intermediate[index]
            except IndexError:
                msg = '%s\nIndex %d out of range, available choices are 0...%d' % (
                            msg, index, len(intermediate) - 1)
                if choice_repr:
                    msg += ''.join(['\n  %d: %s' % (n, choice_repr(choice))
                                    for n, choice in enumerate(intermediate)])
    else:
        if available:
            msg += '\nAvailable items:' + ''.join([
                '\n  %s' % choice_repr(choice)
                for choice in available])
        elif available is not None: # empty list
            msg += '\nThere are no form items in the HTML'
    raise LookupError(msg)


def onlyOne(items, description):
    total = sum([bool(i) for i in items])
    if total == 0 or total > 1:
        raise ValueError(
            "Supply one and only one of %s as arguments" % description)


def zeroOrOne(items, description):
    if sum([bool(i) for i in items]) > 1:
        raise ValueError(
            "Supply no more than one of %s as arguments" % description)


def getControl(controls, label=None, value=None, index=None):
    onlyOne([label, value], '"label" and "value"')
    if label is not None:
        options = [c for c in controls
                   if any(isMatching(l, label) for l in c.labels)]
        msg = 'label %r' % label
    elif value is not None:
        options = [c for c in controls if isMatching(c.value, value)]
        msg = 'value %r' % value
    return disambiguate(options, msg, index, controlFormTupleRepr,
        available=controls)


def getControlLabels(celem, html):
    labels = []
    # In case celem is contained in label element, use its text as a label
    if celem.parent.name == 'label':
        labels.append(normalizeWhitespace(celem.parent.text))
    # find all labels, connected by 'for' attribute
    cid = celem.attrs.get('id')
    if cid:
        forlbls = html.select('label[for=%s]' % cid)
        labels.extend([normalizeWhitespace(l.text) for l in forlbls])
    return [l for l in labels if l is not None]


RegexType = type(re.compile(''))

def isMatching(string, expr):
    """Determine whether ``expr`` matches to ``string``

    ``expr`` can be None, plain text or regular expression.

      * If ``expr`` is ``None``, ``string`` is considered matching
      * If ``expr`` is plain text, its equality to ``string`` will be checked
      * If ``expr`` is regexp, regexp matching agains ``string`` will
        be performed
    """
    if expr is None:
        return True

    if isinstance(expr, RegexType):
        return expr.match(normalizeWhitespace(string))
    else:
        return normalizeWhitespace(expr) in normalizeWhitespace(string)


###############################################################################
#
# mixin class

class ClickMixin(object):
    """Click activity mixin"""

    def doClickActivity(self):
        if self.attrs.get('id'):
            msg = 'CLICK %s#%s' % (self.tag, self.attrs.get('id'))
        elif self.attrs.get('name'):
            msg = 'CLICK %s[name="%s"]' % (self.tag, self.attrs.get('name'))
        else:
            msg = 'CLICK undefined'
        self.browser.doAddActivity(msg)


class HistoryPushStateMixin(object):
    """Hispotry pushState mixin"""

    def setUpPushStateCondition(self):
        # setup history processing based on data-j01-history
        isPushState = self.attrs.get('data-j01-history')
        if isPushState in ['1', 'true', 'push']:
            self.browser.isPushState = True
        elif isPushState in ['0', 'false']:
            self.browser.isPushState = False


###############################################################################
#
# control base class

class ControlBase(SetattrErrorsMixin):

    def __init__(self, browser, elem):
        self.browser = browser
        self._counter = self.browser._counter
        self._elem = elem

    @property
    def attrs(self):
        s = self.browser.toStr
        data = {}
        for k, v in self._elem.attrs.items():
            if isinstance(v, (tuple, list)):
                # list of css class etc. are lists
                v = ','.join(v)
            data[s(k)] = s(v)
        return data

    def render(self, prettify=False):
        if prettify:
            return self._elem
        else:
            return self.__repr__()


###############################################################################
#
# controls

@implementer(interfaces.ILink)
class Link(ClickMixin, ControlBase):

    def __init__(self, browser, elem):
        super(Link, self).__init__(browser, elem)
        self._enable_setattr_errors = True

    @property
    def url(self):
        # could be an anchor without href or an a tag with onclick
        url = self._elem.get('href', '')
        return self.browser._absoluteUrl(url)

    @property
    def text(self):
        txt = normalizeWhitespace(self._elem.text)
        return self.browser.toStr(txt)

    @property
    def tag(self):
        return str(self._elem.name)

    def click(self):
        self.doClickActivity()
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        self.browser.doRequest('GET', self.url)
        self.browser.doDocumentReady()

    def __repr__(self):
        if self.attrs.get('name'):
            nStr = " name='%s'" % self.attrs.get('name')
        else:
            nStr = ''
        if self.attrs.get('id'):
            idStr = " id='%s'" % self.attrs.get('id')
        else:
            idStr = ''
        return "<%s%s%s text='%s' url='%s'>" % (self.__class__.__name__,
            nStr, idStr, normalizeWhitespace(self.text), self.url)


@implementer(interfaces.IControl)
class Control(ControlBase):

    _enable_setattr_errors = False

    def __init__(self, browser, form, control, elem):
        super(Control, self).__init__(browser, elem)
        self._form = form
        self._control = control
        self._counter = self.browser._counter

        # disable addition of further attributes
        self._enable_setattr_errors = True

    @property
    def disabled(self):
        return 'disabled' in self._control.attrs

    @property
    def type(self):
        typeattr = self._control.attrs.get('type', None)
        if typeattr is None:
            # try to figure out type by tag
            if self._control.tag == 'textarea':
                return 'textarea'
            else:
                # By default, inputs are of 'text' type
                return 'text'
        return self.browser.toStr(typeattr)

    @property
    def name(self):
        if self._control.name is None:
            return None
        return self.browser.toStr(self._control.name)

    @property
    def tag(self):
        return str(self._elem.name)

    @property
    def multiple(self):
        return 'multiple' in self._control.attrs

    @apply
    def value():
        def fget(self):
            if self.type == 'file':
                if not self._control.value:
                    return None
            if self.type == 'image':
                if not self._control.value:
                    return ''
            if isinstance(self._control, webtest.forms.Submit):
                return self.browser.toStr(self._control.value_if_submitted())
            val = self._control.value
            if val is None:
                return None
            return self.browser.toStr(val)
        def fset(self, value):
            if self._counter != self.browser._counter:
                raise p01.testbrowser.exceptions.ExpiredError
            if self.type == 'file':
                self.add_file(value, content_type=None, filename=None)
            else:
                self._control.value = value
        return property(fget, fset)

    def add_file(self, file, content_type, filename):
        if self.type != 'file':
            raise TypeError("Can't call add_file on %s controls"
                            % self.mech_control.type)

        if isinstance(file, io.IOBase):
            contents = file.read()
        elif hasattr(file, 'getvalue'):
            contents = file.getvalue()
        else:
            contents = file

        self._form[self.name] = webtest.forms.Upload(filename or '', contents,
                                                     content_type)

    def clear(self):
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        self.value = None

    @Lazy
    def labels(self):
        return [self.browser.toStr(l)
                for l in getControlLabels(self._elem, self._form.html)]

    @property
    def controls(self):
        return []

    def __repr__(self):
        if self.attrs.get('name'):
            nStr = " name='%s'" % self.attrs.get('name')
        else:
            nStr = ''
        if self.attrs.get('id'):
            idStr = " id='%s'" % self.attrs.get('id')
        else:
            idStr = ''
        if not (nStr or idStr):
            # use html contents as representation
            cStr = ''.join([str(e).strip() for e in self._elem.contents
                            if str(e) and str(e).replace('\n', '').strip()])
            cStr = cStr.replace('\n', '')
            cStr = cStr.strip()
            if cStr:
                cStr = " html='%s'" % cStr
        else:
            cStr = ''
        return "<%s%s%s%s>" % (
            self.__class__.__name__, nStr, idStr, cStr)


@implementer(interfaces.ITextAreaControl)
class TextAreaControl(Control):
    """Textarea control"""


class InputControlBase(Control):
    """Input control base class"""


@implementer(interfaces.IFileControl)
class FileControl(InputControlBase):
    """Input control type="file"""


@implementer(interfaces.IPasswordControl)
class PasswordControl(InputControlBase):
    """Input control type="password"""


@implementer(interfaces.IHiddenControl)
class HiddenControl(InputControlBase):
    """Input control type="hidden"""


@implementer(interfaces.ITextControl)
class TextControl(InputControlBase):
    """HTML5 input control type="text"""


@implementer(interfaces.IEMailControl)
class EMailControl(InputControlBase):
    """HTML5 input control type="email"""


@implementer(interfaces.IDateControl)
class DateControl(InputControlBase):
    """HTML5 input control type="date"""


@implementer(interfaces.IDatetimeControl)
class DatetimeControl(InputControlBase):
    """HTML5 input control type="datetime"""


@implementer(interfaces.IDatetimeLocalControl)
class DatetimeLocalControl(InputControlBase):
    """HTML5 input control type="datetime-local"""


@implementer(interfaces.ITimeControl)
class TimeControl(InputControlBase):
    """HTML5 input control type="time"""


@implementer(interfaces.IWeekControl)
class WeekControl(InputControlBase):
    """HTML5 input control type="week"""


@implementer(interfaces.IMonthControl)
class MonthControl(InputControlBase):
    """HTML5 input control type="month"""


@implementer(interfaces.IColorControl)
class ColorControl(InputControlBase):
    """HTML5 input control type="color"""


@implementer(interfaces.ISearchControl)
class SearchControl(InputControlBase):
    """HTML5 input control type="search"""


@implementer(interfaces.IURLControl)
class URLControl(InputControlBase):
    """HTML5 input control type="url"""


@implementer(interfaces.INumberControl)
class NumberControl(InputControlBase):
    """HTML5 input control type="number"""


@implementer(interfaces.ITelControl)
class TelControl(InputControlBase):
    """HTML5 input control type="tel"""


@implementer(interfaces.ISubmitControl)
class SubmitControl(ClickMixin, Control):
    """Submit control type="submit"""
    """Submit control

    Note: the submit concept depends on encoding given from current response.
    But what happens if the current response was a application/json response?
    But anyway, you should not mix encoding in different response if content
    get injected into the same page. We asume, that any response provides the
    same charset for encoding e.g. utf-8.
    """

    @Lazy
    def labels(self):
        labels = super(SubmitControl, self).labels
        labels.append(self._control.value_if_submitted())
        if self._elem.text:
            labels.append(normalizeWhitespace(self._elem.text))
        return [l for l in labels if l]

    def getEncodedArguments(self, **args):
        # encode unicode strings for the outside world
        if PYTHON2 and self.browser.testapp.use_unicode:
            def toStr(s):
                # six text_type for py2
                if isinstance(s, unicode):
                    return s.encode(self.browser._response.charset)
                return s
            if 'params' in args:
                args['params'] = [tuple(map(toStr, p)) for p in args['params']]
            if 'upload_files' in args:
                args['upload_files'] = [map(toStr, f)
                                        for f in args['upload_files']]
            if 'content_type' in args:
                args['content_type'] = toStr(args['content_type'])
        return args

    def _post(self, form, name=None, index=None, coord=None, **args):
        # A reimplementation of webtest.forms.Form.submit() to allow to insert
        # coords into the request
        method = form.method.upper()
        params = form.submit_fields(name, index=index)
        if coord is not None:
            params.extend([('%s.x' % name, coord[0]),
                           ('%s.y' % name, coord[1])])
        args['params'] = params
        assert method in ('GET', 'POST'), (
            'Only "GET" or "POST" are allowed for method (you gave %r)'
            % method)
        if method != "GET":
            args.setdefault("content_type",  form.enctype)
        url = self.browser._absoluteUrl(form.action)
        args = self.getEncodedArguments(**args)
        if method == 'GET':
            return self.browser.testapp.get(url, **args)
        else:
            return self.browser.testapp.post(url, **args)

    def doSubmit(self, form, coord=None):
        # find index of given control in the form
        url = self.browser._absoluteUrl(form.action)
        index = form.fields[self._control.name].index(self._control)
        make_request = lambda args: self._post(form, self._control.name,
            index, coord=coord, **args)
        self.browser.doProcessRequest(url, make_request)

    def click(self):
        self.doClickActivity()
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        self.doSubmit(self._form)
        self.browser.doDocumentReady()


@implementer(interfaces.IButtonControl)
class ButtonControl(SubmitControl):
    """Button control type="submit"""


@implementer(interfaces.IImageSubmitControl)
class ImageControl(SubmitControl):

    def click(self, coord=(1,1)):
        self.doClickActivity()
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        self.doSubmit(self._form, coord)
        self.browser.doDocumentReady()


@implementer(interfaces.IJSONRPCButtonControl)
class JSONRPCButtonControl(SubmitControl):
    """JSONRPCButton control given from j01.jsonrpc.btn"""

    def doClick(self, form):
        # find index of given control in the form
        url = str(self._control.attrs.get('data-j01-testing-url'))
        fName = self._control.attrs.get('data-j01-testing-form')
        mName = self._control.attrs.get('data-j01-testing-method')
        sName = self._control.attrs.get('data-j01-testing-success')
        eName = self._control.attrs.get('data-j01-testing-error')
        cbDefault = self.browser.j01RenderContent
        onSuccess = self.browser.j01GetCallback(sName, cbDefault)
        onError = self.browser.j01GetCallback(eName, cbDefault)
        # get widget values from releated form
        # (could be another form then the control.form)
        form = self.browser.getForm(name=fName)
        params = self.browser.j01FormToArray(form, self._control.name)
        self.browser.doJSONRPCCall(url, mName, params, onSuccess, onError)

    def click(self):
        self.doClickActivity()
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        self.doClick(self._form)
        self.browser.doDocumentReady()


@implementer(interfaces.IJSONRPCClickButtonControl)
class JSONRPCClickButtonControl(JSONRPCButtonControl):
    """JSONRPCClickButton control given from j01.jsonrpc.btn"""


@implementer(interfaces.IJSONRPCContentButtonControl)
class JSONRPCContentButtonControl(JSONRPCButtonControl):
    """JSONRPCContentButton control given from j01.jsonrpc.btn"""


@implementer(interfaces.ICloseButtonControl)
class CloseButtonControl(SubmitControl):
    """CloseButton given from j01.jsonrpc

    This button will remove content from the dom
    """

    def doClick(self, form):
        # get css expression and remove content from dom
        cssSelector = self._control.attrs.get('data-j01-testing-expression')
        self.browser.doRemoveContent(cssSelector)

    def click(self):
        self.doClickActivity()
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        self.doClick(self._form)
        self.browser.doDocumentReady()


class ClickControlBase(ClickMixin, Control):
    """Click control base class for <a> tag elements with special click handling
    """

    def __init__(self, browser, link):
        self.browser = browser
        self._elem = link
        self._counter = self.browser._counter
        self._enable_setattr_errors = True

    @property
    def url(self):
        url = self._elem.attrs.get('data-j01-testing-url', '')
        return self.browser._absoluteUrl(url)

    @property
    def text(self):
        txt = normalizeWhitespace(self._elem.text)
        return self.browser.toStr(txt)

    @property
    def tag(self):
        return str(self._elem.name)

    def doClick(self):
        raise NotImplemented("Subclass must implement doClick method")

    def click(self):
        self.doClickActivity()
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        self.doClick()
        self.browser.doDocumentReady()

    def __repr__(self):
        if self.attrs.get('id'):
            idStr = " id='%s'" % self.attrs.get('id')
        else:
            idStr = ''
        return "<%s %stext='%s' url='%s'>" % (
            self.__class__.__name__, idStr, normalizeWhitespace(self.text),
                self.url)


@implementer(interfaces.IJSONRPCClickControl)
class JSONRPCClickControl(HistoryPushStateMixin, ClickControlBase):
    """JSONRPC click control"""

    def doClick(self):
        url = str(self._elem.attrs.get('data-j01-testing-url', ''))
        if not url:
            # link without testing data setup
            url = str(self._elem.attrs.get('href'))
        mName = self._elem.attrs.get('data-j01-testing-method',
            'j01LoadContent')
        sName = self._elem.attrs.get('data-j01-testing-success')
        eName = self._elem.attrs.get('data-j01-testing-error')
        cbDefault = self.browser.j01RenderContent
        onSuccess = self.browser.j01GetCallback(sName, cbDefault)
        onError = self.browser.j01GetCallback(eName, cbDefault)
        # get params from url
        params = self.browser.j01URLToArray(url)
        self.setUpPushStateCondition()
        self.browser.doJSONRPCCall(url, mName, params, onSuccess, onError)


# j01.dialog
@implementer(interfaces.IDialogButtonControl)
class DialogButtonControl(JSONRPCButtonControl):
    """DialogButton control given from j01.dialog.btn"""

    def doClick(self):
        url = str(self._elem.attrs.get('data-j01-testing-url', ''))
        if not url:
            # button without testing data setup. Note: this will only work for
            # a default form with name="form"
            url = str(self._elem.attrs.get('href'))
        fName = self._control.attrs.get('data-j01-testing-form', 'form')
        mName = self._control.attrs.get('data-j01-testing-method',
            'j01DialogFormProcessor')
        sName = self._control.attrs.get('data-j01-testing-success')
        eName = self._control.attrs.get('data-j01-testing-error')
        assert mName == 'j01DialogFormProcessor'
        form = self.browser.getForm(name=fName)
        cbDefault = self.browser.j01DialogRenderContent
        onSuccess = self.browser.j01GetCallback(sName, cbDefault)
        onError = self.browser.j01GetCallback(eName, cbDefault)
        params = self.browser.j01FormToArray(form, self._control.name)
        self.browser.doJSONRPCCall(url, mName, params, onSuccess, onError)

    def click(self):
        self.doClickActivity()
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        self.doClick()
        self.browser.doDocumentReady()


@implementer(interfaces.IDialogContentButtonControl)
class DialogContentButtonControl(JSONRPCButtonControl):
    """DialogContentButton control given from j01.dialog.btn"""


@implementer(interfaces.IShowDialogButtonControl)
class ShowDialogButtonControl(JSONRPCButtonControl):
    """ShowDialogButton control given from j01.dialog.btn"""

    def doClick(self):
        url = str(self._control.attrs.get('data-j01-testing-url'))
        self.browser.j01Dialog(url)

    def click(self):
        self.doClickActivity()
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        self.doClick()
        self.browser.doDocumentReady()


@implementer(interfaces.IDialogCloseButtonControl)
class DialogCloseButtonControl(SubmitControl):
    """DialogCloseButton control given from j01.dialog.btn"""

    def doClick(self):
        # get css expression and remove content from dom
        cssSelector = self._control.attrs.get('data-j01-testing-expression')
        self.browser.doRemoveElement(cssSelector)
        url = self._control.attrs.get('data-j01-testing-url')
        if url is not None:
            # optional, redirect to given url
            self.browser.doRequest('GET', url)

    def click(self):
        self.doClickActivity()
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        self.doClick()
        self.browser.doDocumentReady()


@implementer(interfaces.IDialogLinkControl)
class DialogLinkControl(ClickControlBase):
    """DialogLink control given from j01.dialog.link opening a dialog

    This method is useing the using j01Dialog method and simulates the
    j01.dialog.js methods j01Dialog, j01DialogOn, j01DialogOnClick.
    """

    def doClick(self):
        # get css expression and remove content from dom
        url = self._elem.attrs.get('data-j01-testing-url')
        if url is None:
            url = self._elem.attrs.get('href')
        # open dialog with goven url
        self.browser.j01Dialog(url)


@implementer(interfaces.IItemControl)
class ItemControl(ControlBase):

    def __init__(self, browser, form, parent, elem):
        super(ItemControl, self).__init__(browser, elem)
        self._form = form
        self._parent = parent
        self._counter = self.browser._counter
        self._enable_setattr_errors = True

    @property
    def control(self):
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        return self._parent

    @property
    def _value(self):
        return self._elem.attrs.get('value', self._elem.text)

    @property
    def optionValue(self):
        return self.browser.toStr(self._value)

    @property
    def value(self):
        # internal alias for convenience implementing getControl()
        return self.optionValue

    @property
    def disabled(self):
        return 'disabled' in self._elem.attrs

    @apply
    def selected():
        def fget(self):
            """See p01.testbrowser.interfaces.IControl"""
            return self._value in self._parent.value
        def fset(self, value):
            if self._counter != self.browser._counter:
                raise p01.testbrowser.exceptions.ExpiredError
            if self._parent.multiple:
                values = list(self._parent.value)
                if value:
                    values.append(self._value)
                else:
                    values = [v for v in values if v != self._value]
                self._parent.value = values
            else:
                if value:
                    self._parent.value = self._value
                else:
                    self._parent.value = None
        return property(fget, fset)

    def click(self):
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        self.selected = not self.selected

    @Lazy
    def labels(self):
        labels = [self._elem.attrs.get('label'), self._elem.text]
        return [self.browser.toStr(normalizeWhitespace(lbl))
                for lbl in labels if lbl]

    def __repr__(self):
        raise NotImplemented("Subclass must implement __repr__")


@implementer(interfaces.ISelectControl)
class SelectControl(ItemControl):
    """Select control"""

    def __repr__(self):
        if self.attrs.get('name'):
            nStr = " name='%s'" % self.attrs.get('name')
        else:
            nStr = ''
        if self.selected:
            selected = " selected='selected'"
        else:
            selected = ''
        return "<SelectControl name='%s'%s value=%r%s>" % \
                (self._parent.name, nStr, self.optionValue, selected)


@implementer(interfaces.IRadioControl)
class RadioControl(ItemControl):
    """Radio control"""

    @property
    def optionValue(self):
        return self.browser.toStr(self._elem.attrs.get('value'))

    @Lazy
    def labels(self):
        return [self.browser.toStr(l)
                for l in getControlLabels(self._elem, self._form.html)]

    def __repr__(self):
        if self.attrs.get('id'):
            idStr = " id='%s'" % self.attrs.get('id')
        else:
            idStr = ''
        if self.selected:
            checked = ' checked="checked"'
        else:
            checked = ''
        return "<RadioControl name='%s'%s value=%r%s>" % (
            self._parent.name, idStr, self.optionValue, checked)


@implementer(interfaces.ICheckboxControl)
class CheckboxControl(ItemControl):
    """Checkbox control"""

    _control = None

    def __init__(self, browser, form, parent, wtcontrol, elem):
        super(CheckboxControl, self).__init__(browser, form, parent, elem)
        self._control = wtcontrol

    @property
    def optionValue(self):
        return self.browser.toStr(self._control._value or 'on')

    @apply
    def selected():
        def fget(self):
            """See p01.testbrowser.interfaces.IControl"""
            return self._control.checked
        def fset(self, value):
            if self._counter != self.browser._counter:
                raise p01.testbrowser.exceptions.ExpiredError
            self._control.checked = value
        return property(fget, fset)

    @Lazy
    def labels(self):
        return [self.browser.toStr(l)
                for l in getControlLabels(self._elem, self._form.html)]

    def __repr__(self):
        if self.attrs.get('id'):
            idStr = " id='%s'" % self.attrs.get('id')
        else:
            idStr = ''
        if self.selected:
            checked = " checked='checked'"
        else:
            checked = ''
        return "<CheckboxControl name='%s'%s value=%r%s>" % (
            self._control.name, idStr, self.optionValue, checked)


@implementer(interfaces.IListControl)
class ListControl(Control):
    """Select control"""

    def __init__(self, browser, form, control, elem):
        super(ListControl, self).__init__(browser, form, control, elem)
        # HACK: set default value of a list control and then forget about
        # initial default values. Otherwise webtest will not allow to set None
        # as a value of select and radio controls.
        v = control.value
        if v:
            control.value = v
            # Uncheck all the options   Carefully: WebTest used to have
            # 2-tuples here before commit 1031d82e, and 3-tuples since then.
            control.options = [option[:1] + (False,) + option[2:]
                               for option in control.options]

    @property
    def type(self):
        return 'select'

    @apply
    def value():
        def fget(self):
            val = self._control.value
            if val is None:
                return []
            if self.multiple and isinstance(val, (list, tuple)):
                return [self.browser.toStr(v) for v in val]
            else:
                return [self.browser.toStr(val)]
        def fset(self, value):
            if not value:
                # HACK: Force unsetting selected value, by avoiding validity check.
                # Note, that force_value will not work for webtest.forms.Radio
                # controls.
                self._control.selectedIndex = None
            else:
                if not self.multiple and isinstance(value, (list, tuple)):
                    value = value[0]
                self._control.value = value
        return property(fget, fset)

    @apply
    def displayValue():
        def fget(self):
            """See p01.testbrowser.interfaces.IListControl"""
            # not implemented for anything other than select;
            cvalue = self._control.value
            if cvalue is None:
                return []

            if not isinstance(cvalue, list):
                cvalue = [cvalue]

            alltitles = []
            for key, titles in self._getOptions():
                if key in cvalue:
                    alltitles.append(titles[0])
            return alltitles
        def fset(self, value):
            if self._counter != self.browser._counter:
                raise p01.testbrowser.exceptions.ExpiredError

            values = []
            for key, titles in self._getOptions():
                if any(t in value for t in titles):
                    values.append(key)
            self.value = values
        return property(fget, fset)

    @property
    def displayOptions(self):
        """See p01.testbrowser.interfaces.IListControl"""
        return [titles[0] for key, titles in self._getOptions()]

    @property
    def options(self):
        """See p01.testbrowser.interfaces.IListControl"""
        return [key for key, title in self._getOptions()]

    def getControl(self, label=None, value=None, index=None):
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError

        return getControl(self.controls, label, value, index)

    @property
    def controls(self):
        raise NotImplemented("Subclass must implement controls")

    def _getOptions(self):
        return [(c.optionValue, c.labels) for c in self.controls]

    def render(self, prettify=False):
        # no _controls available for prettify
        return self.__repr__()

    def __repr__(self):
        raise NotImplemented("Subclass must implement __repr__ method")


@implementer(interfaces.ISelectListControl)
class SelectListControl(ListControl):
    """List of SelectControl"""

    @property
    def controls(self):
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        ctrls = []
        for elem in self._elem.select('option'):
            ctrls.append(SelectControl(self.browser, self._form, self, elem))
        return ctrls

    def __repr__(self):
        return "<SelectListControl name='%s'>" % self.name


@implementer(interfaces.IListControl)
class RadioListControl(ListControl):
    """List of RadioControl"""

    _elems = None

    def __init__(self, browser, form, control, elems):
        super(RadioListControl, self).__init__(browser, form, control, elems[0])
        self._elems = elems

    @property
    def type(self):
        return 'radio'

    @property
    def controls(self):
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        for opt in self._elems:
            yield RadioControl(self.browser, self._form, self, opt)

    @Lazy
    def labels(self):
        res = []
        # find label, connected by 'for' attribute
        cid = self._elem.attrs.get('id')
        if cid:
            ids = cid.split('-')
            if ids:
                ids.pop(-1)
                fid = '-'.join(ids)
                forlbls = self._form.html.select('label[for=%s]' % fid)
                res = [normalizeWhitespace(l.text) for l in forlbls if l]
        return res

    def click(self):
        """Click toggle (true/false) radio options"""
        value = self.value
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        if len(list(self.controls)) == 2:
            for ctrl  in self.controls:
                # switch selected
                if ctrl.value not in self.value:
                    ctrl.selected = True
                    break
        else:
            raise ValueError(
                'Can only click (toggle) radio list control with 2 radio options')

    def __repr__(self):
        return "<RadioListControl name='%s'>" % self.name


@implementer(interfaces.IListControl)
class CheckboxListControl(SetattrErrorsMixin):
    """List of CheckboxControl"""

    def __init__(self, browser, name, ctrlelems):
        self.browser = browser
        self.name = name
        self._counter = self.browser._counter
        self._ctrlelems = ctrlelems
        self._enable_setattr_errors = True

    def clear(self):
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        self.value = []

    @property
    def controls(self):
        return [CheckboxControl(self.browser, c.form, self, c, e, )
                for c, e in self._ctrlelems]

    @property
    def options(self):
        opts = [self._trValue(c.optionValue) for c in self.controls]
        return opts

    @property
    def displayOptions(self):
        return [c.labels[0] for c in self.controls]

    def _trValue(self, value):
        return True if value == 'on' else value

    @apply
    def value():
        def fget(self):
            ctrls = self.controls
            val = [self._trValue(c.optionValue) for c in ctrls if c.selected]
            if len(self._ctrlelems) == 1 and val == [True]:
                return True
            return val
        def fset(self, value):
            ctrls = self.controls
            if isinstance(value, (list, tuple)):
                for ctrl in ctrls:
                    ctrl.selected = ctrl.optionValue in value
            else:
                ctrls[0].selected = value
        return property(fget, fset)

    @apply
    def displayValue():
        def fget(self):
            return [c.labels[0] for c in self.controls if c.selected]
        def fset(self, value):
            for c in self.controls:
                c.selected = any(v in c.labels for v in value)
        return property(fget, fset)

    @property
    def multiple(self):
        return True

    @property
    def disabled(self):
        return all('disabled' in e.attrs for c, e in self._ctrlelems)

    @property
    def type(self):
        return 'checkbox'

    def getControl(self, label=None, value=None, index=None):
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        return getControl(self.controls, label, value, index)

    @Lazy
    def labels(self):
        return []

    def render(self, prettify=False):
        # no _controls available for prettify
        return self.__repr__()

    def __repr__(self):
        return "<CheckboxListControl name='%s'>" % self.name


@implementer(interfaces.IForm)
class Form(SetattrErrorsMixin):
    """HTML Form"""

    def __init__(self, browser, form):
        """Initialize the Form

        browser - a Browser instance
        form - a webtest.Form instance
        """
        self.browser = browser
        self._form = form
        self._counter = self.browser._counter
        self._enable_setattr_errors = True

    @property
    def action(self):
        return self.browser._absoluteUrl(self._form.action)

    @property
    def method(self):
        return str(self._form.method)

    @property
    def enctype(self):
        return str(self._form.enctype)

    @property
    def name(self):
        return str(self._form.html.form.get('name'))

    @property
    def id(self):
        """See p01.testbrowser.interfaces.IForm"""
        return str(self._form.id)

    def _submit(self, **args):
        # A reimplementation of webtest.forms.Form.submit() to allow to insert
        # coords into the request
        form = self._form
        fields = form.submit_fields()
        if form.method.upper() != "GET":
            args.setdefault("content_type",  form.enctype)
        return form.response.goto(form.action, method=form.method,
            params=fields, **args)

    def submit(self, label=None, name=None, index=None, coord=None):
        """See p01.testbrowser.interfaces.IForm"""
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError

        form = self._form
        if label is not None or name is not None:
            controls, msg, available = self.browser._getAllControls(
                label, name, [form])
            controls = [c for c in controls
                        if interfaces.ISubmitControl.providedBy(c)]
            control = disambiguate(controls, msg, index, controlFormTupleRepr,
                available)
            if interfaces.IImageSubmitControl.providedBy(control):
                control.doSubmit(form, coord)
            else:
                control.doSubmit(form)
        else: # JavaScript sort of submit
            if index is not None or coord is not None:
                raise ValueError(
                    'May not use index or coord without a control')
            url = self.browser._absoluteUrl(form.action)
            make_request = lambda args: self._submit(**args)
            self.browser.doProcessRequest(url, make_request)

    def getControl(self, label=None, name=None, index=None):
        """See p01.testbrowser.interfaces.IBrowser"""
        if self._counter != self.browser._counter:
            raise p01.testbrowser.exceptions.ExpiredError
        intermediate, msg, available = self.browser._getAllControls(
                        label, name, [self._form], include_subcontrols=True)
        return disambiguate(intermediate, msg, index,
                            controlFormTupleRepr, available)


###############################################################################
#
# control mixin class


def getNoneFormControl(browser, form, wtcontrol, elem):
    """Returns a custom form control

    The given wtcontrol is a web test control element. Just check if your
    custom condition will fit for handling this control based on this control
    otherwise return None
    """
    return None


def getNoneLinkControl(browser, elem):
    """REturns a custom link control

    The given <a> tag element was already filtered by text, id or url.
    Just check if you custom condition will fit for handling the element based
    on the given (dom) elem.
    """
    return None


def getNoneClickableControl(browser, elem, text=None, url=None):
    """Returns a clickable control or None for matching query

    Check the condition for the given element and return a clickable control.
    The given element was already filtered by id if an id was used as selector.
    """
    return None


###############################################################################
#
# browser control factories

class ControlFactoryMixin(object):
    """Control factory mixin"""

    getCustomFormControl = getNoneFormControl
    getCustomLinkControl = getNoneLinkControl
    getCustomClickableControl = getNoneClickableControl

    # clickable controls
    def getJSONRPCClickableControl(self, elem, text=None, url=None):
        typ = elem.get('data-j01-testing-typ')
        eURL = elem.get('data-j01-testing-url')
        if typ == 'JSONRPCClick' and \
            isMatching(elem.text, text) and \
            isMatching(eURL, url):
            return JSONRPCClickControl(self, elem)

    # link controls
    def getJSONRPCLinkControl(self, elem):
        typ = elem.get('data-j01-testing-typ')
        cls = elem.get('class')
        if typ == 'JSONRPCClick':
            return JSONRPCClickControl(self, elem)
        elif typ == 'J01Dialog':
            return DialogLinkControl(self, elem)
        # known css classes, cls is a list of class names or None
        elif cls is not None and 'j01LoadContentLink' in cls:
            return JSONRPCClickControl(self, elem)
        elif cls is not None and 'j01DialogLink' in cls:
            return DialogLinkControl(self, elem)

    # submit controls
    def getJSONRPCFormControl(self, form, wtcontrol, elem):
        typ = wtcontrol.attrs.get('data-j01-testing-typ')
        # j01.jsonrpc buttons
        if typ == 'JSONRPCButton':
            return JSONRPCButtonControl(self, form, wtcontrol, elem)
        elif typ == 'JSONRPCClickButton':
            return JSONRPCClickButtonControl(self, form, wtcontrol, elem)
        elif typ == 'JSONRPCContentButton':
            return JSONRPCContentButtonControl(self, form, wtcontrol, elem)
        elif typ == 'CloseButton':
            return CloseButtonControl(self, form, wtcontrol, elem)
        # j01.dialog buttons
        elif typ == 'DialogButton':
            return DialogButtonControl(self, form, wtcontrol, elem)
        elif typ == 'DialogContentButton':
            return DialogContentButtonControl(self, form, wtcontrol, elem)
        elif typ == 'ShowDialogButton':
            return ShowDialogButtonControl(self, form, wtcontrol, elem)
        elif typ == 'DialogCloseButton':
            return DialogCloseButtonControl(self, form, wtcontrol, elem)

    def getOneFormControl(self, form, wtcontrol, elemindex):
        if isinstance(wtcontrol, webtest.forms.Radio):
            elems = [e for e in elemindex
                     if e.attrs.get('name') == wtcontrol.name]
            return RadioListControl(self, form, wtcontrol, elems)

        elem = elemindex[wtcontrol.pos]
        # if input element, define html5 type e.g. date, email etc.
        if elem.name == 'input':
            ityp = elem.get('type')
        else:
            ityp = None

        if isinstance(wtcontrol, (webtest.forms.Select,
                                  webtest.forms.MultipleSelect)):
            return SelectListControl(self, form, wtcontrol, elem)

        elif isinstance(wtcontrol, webtest.forms.Submit):
            ctrl = self.getCustomFormControl(form, wtcontrol, elem)
            if ctrl is not None:
                return ctrl
            ctrl = self.getJSONRPCFormControl(form, wtcontrol, elem)
            if ctrl is not None:
                return ctrl
            if wtcontrol.attrs.get('type', 'submit') == 'image':
                return ImageControl(self, form, wtcontrol, elem)
            elif elem.name == 'button':
                return ButtonControl(self, form, wtcontrol, elem)
            else:
                return SubmitControl(self, form, wtcontrol, elem)
        # input controls
        elif ityp == 'file':
            return FileControl(self, form, wtcontrol, elem)
        elif ityp == 'hidden':
            return HiddenControl(self, form, wtcontrol, elem)
        elif ityp == 'password':
            return PasswordControl(self, form, wtcontrol, elem)
        elif ityp == 'text':
            return TextControl(self, form, wtcontrol, elem)
        # html5 input controls
        elif ityp == 'email':
            return EMailControl(self, form, wtcontrol, elem)
        elif ityp == 'date':
            return DateControl(self, form, wtcontrol, elem)
        elif ityp == 'datetime':
            return DatetimeControl(self, form, wtcontrol, elem)
        elif ityp == 'datetime-local':
            return DatetimeLocalControl(self, form, wtcontrol, elem)
        elif ityp == 'time':
            return TimeControl(self, form, wtcontrol, elem)
        elif ityp == 'week':
            return WeekControl(self, form, wtcontrol, elem)
        elif ityp == 'month':
            return MonthControl(self, form, wtcontrol, elem)
        elif ityp == 'color':
            return ColorControl(self, form, wtcontrol, elem)
        elif ityp == 'search':
            return SearchControl(self, form, wtcontrol, elem)
        elif ityp == 'url':
            return URLControl(self, form, wtcontrol, elem)
        elif elem.name == 'textarea':
            return TextAreaControl(self, form, wtcontrol, elem)
        else:
            # unknown, new html5 control?
            return Control(self, form, wtcontrol, elem)

    def getFormControls(self, name, wtcontrols, elemindex):
        assert len(wtcontrols) > 0
        first_wtc = wtcontrols[0]
        if isinstance(first_wtc, webtest.forms.Checkbox):
            # checkbox control list
            ctrlelems = [(wtc, elemindex[wtc.pos]) for wtc in wtcontrols]
            controls = [CheckboxListControl(self, name, ctrlelems)]
        else:
            # other controls
            controls = []
            for wtc in wtcontrols:
                ctrl = self.getOneFormControl(wtc.form, wtc, elemindex)
                controls.append(ctrl)

        return controls
