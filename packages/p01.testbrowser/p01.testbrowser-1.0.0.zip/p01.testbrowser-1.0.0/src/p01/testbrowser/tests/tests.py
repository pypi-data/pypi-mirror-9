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

import sys
import doctest
import unittest

import p01.testbrowser.ftests.wsgitestapp
import p01.testbrowser.tests.helper



def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../README.txt',
            checker=p01.testbrowser.tests.helper.checker,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        doctest.DocFileSuite('../cookies.txt',
            checker=p01.testbrowser.tests.helper.checker,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        doctest.DocFileSuite('checker.txt', encoding='utf-8',
            checker=p01.testbrowser.tests.helper.checker,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        doctest.DocFileSuite('fixed-bugs.txt',
            checker=p01.testbrowser.tests.helper.checker,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        doctest.DocFileSuite('../xpath.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
