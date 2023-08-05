###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Tests
$Id: tests.py 3934 2014-03-17 07:38:52Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import unittest
import doctest

import j01.form.testing


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../README.txt'),
        doctest.DocFileSuite('checker.txt'),
        # widgets
        doctest.DocFileSuite('dictionary.txt',
            setUp=j01.form.testing.setUp, tearDown=j01.form.testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('password.txt',
            setUp=j01.form.testing.setUp, tearDown=j01.form.testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
