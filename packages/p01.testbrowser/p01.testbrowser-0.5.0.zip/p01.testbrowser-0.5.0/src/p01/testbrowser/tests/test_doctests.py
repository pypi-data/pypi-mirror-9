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

import p01.testbrowser.ftests.wsgitestapp
import p01.testbrowser.tests.helper


def test_suite():
    flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

    suite = doctest.DocFileSuite(
        'README.txt',
        'cookies.txt',
        'fixed-bugs.txt',
        optionflags=flags,
        checker=p01.testbrowser.tests.helper.checker,
        package='p01.testbrowser')

    return suite

# additional_tests is for setuptools "setup.py test" support
additional_tests = test_suite
