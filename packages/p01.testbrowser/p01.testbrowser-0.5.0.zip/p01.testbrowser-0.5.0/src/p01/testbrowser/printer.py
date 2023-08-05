###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: printer.py 4042 2014-04-19 03:46:00Z roger.ineichen $
"""

import re

import lxml.etree
import lxml.html

import zope.interface
import zope.schema

from p01.testbrowser.html2text import html2text

RE_CHARSET = re.compile('.*;charset=(.*)')
LINKS = re.compile("(<a\s+href=(.*?)</a>)", re.I+re.U+re.M+re.S)
INPUTS = re.compile(r"(<(input|button|textarea|select)(.*?)</\2>)|(<(input|button|textarea|select)(.*?)/>)", re.I+re.U+re.M+re.S)


###############################################################################
#
# etree helper

def eTreeContents(contents, charset=None, xml_strict=False):
    # I'm not using any internal knowledge about testbrowser
    # here, to avoid breakage. Memory usage won't be a problem.
    if xml_strict:
        _etree = lxml.etree.fromstring(
            contents,
            parser=lxml.etree.XMLParser(resolve_entities=False))
    else:
        # This is a workaround against the broken fallback for
        # encoding detection of libxml2.
        # We have a chance of knowing the encoding as Zope states this in
        # the content-type response header.
        content = contents
        #if charset is not None:
        #    content = content.decode(charset)
        _etree = lxml.etree.HTML(content)

    return _etree


def eTreeBrowser(browser):
    content = browser.contents

    try:
        content_type = browser.headers['content-type']
    except AttributeError:
        content_type = 'text/html;charset=UTF-8'

    charset = None
    match = RE_CHARSET.match(content_type)
    if match is not None:
        charset = match.groups()[0]

    tree = eTreeContents(content, charset=charset)
    return tree


def getETree(browserOrContents):
    if isinstance(browserOrContents, basestring):
        return eTreeContents(browserOrContents, charset=None)
    else:
        return eTreeBrowser(browserOrContents)


def getContent(browserOrContents, selector=None):
    if selector is not None:
        tree = getETree(browserOrContents)
        node = tree.xpath(selector)
        if isinstance(node, (list, tuple)):
            content = '\n'.join([lxml.html.tostring(n) for n in node])
        else:
            content = lxml.html.tostring(node)
    else:
        if not isinstance(browserOrContents, basestring):
            content = browserOrContents.contents
    return content


###############################################################################
#
# plain text extraction helpers

def getPlainText(browserOrContents, selector=None, **kw):
    if isinstance(browserOrContents, unicode):
        browserOrContents = browserOrContents.encode('utf8')
    content = getContent(browserOrContents, selector)
    content = content.decode('utf8')
    plain = html2text(content, **kw)
    plain = '\n'.join([x.rstrip() for x in plain.splitlines()])
    plain = plain.replace('\n\n', '\n')
    return plain


def getNodeText(node, addTitle=False):
    if isinstance(node, (list, tuple)):
        return '\n'.join(getNodeText(child, addTitle)
                         for child in node)
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


###############################################################################
#
# print content as (plain) text

def asText(browserOrContents, selector='.//form', strip=False):
    tree = getETree(browserOrContents)
    for node in tree.xpath(selector):
        txt = getNodeText(node)
        if strip:
            while '\n\n' in txt:
                txt = txt.replace('\n\n', '\n')
            txt =txt.strip()
        print txt


def printTableAsText(browserOrContents, selector='.//table[@class="list"]'):
    tree = getETree(browserOrContents)
    node = tree.xpath(selector)
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


def printBodyAsText(browserOrContents):
    asText(browserOrContents, './/body', strip=True)


def printFormStatusAsText(browserOrContents):
    asText(browserOrContents, selector='.//div[@class="status"]')


###############################################################################
#
# print HTML elements

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


def printNodes(browserOrContents, selector=None, strip=False):
    tree = getETree(browserOrContents)
    assert selector is not None

    res = []
    for node in tree.xpath(selector):
        node2String(node, res)
    print '\n'.join(res)


def printSelector(browserOrContents, selector=None):
    printNodes(browserOrContents, selector=selector)


def printBody(browserOrContents):
    printNodes(browserOrContents, selector='.//body')


def printForms(browserOrContents, selector=None):
    content = getContent(browserOrContents, selector)
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
    printNodes(content, selector='|'.join(selector))


def printWidgets(browserOrContents, selector=None):
    content = getContent(browserOrContents, selector)
    selector = [
        './/input[@type="submit"]',
        './/input[@type="text"]',
        './/input[@type="password"]',
        './/input[@type="date"]',
        './/input[@type="hidden"]',
        './/select',
        './/textarea',
        ]
    printNodes(content, selector='|'.join(selector))


def printButtons(browserOrContents, selector=None):
    content = getContent(browserOrContents, selector)
    selector = [
        './/input[@type="submit"]',
        './/input[@type="button"]',
        './/input[@type="reset"]',
        './/button',
        ]
    printNodes(content, selector='|'.join(selector))


def printLinks(browserOrContents, selector=None):
    content = getContent(browserOrContents, selector)
    selector = [
        './/a',
        ]
    printNodes(content, selector='|'.join(selector))


###############################################################################
#
# object state printing

def printFields(obj, fnames=None, iface=None, omit=(), sorting=True):
    if iface is None and fnames is None:
        iface = zope.interface.providedBy(obj).declared[0]
    if iface:
        fnames = zope.schema.getFieldNamesInOrder(iface)
    if sorting:
        fnames = sorted(fnames)
    for fname in fnames:
        if fname in omit:
            continue
        try:
            value = getattr(obj, fname)
        except Exception, e:
            value = repr(e)
        text = u"%s: %s" % (fname, value)
        print text.encode('ascii','replace')


def printSequenceFields(seq, fnames=None, iface=None, omit=()):
    for obj in seq:
        print str(obj)
        print '---------------'
        printFields(obj, fnames=fnames, iface=iface, omit=omit)
