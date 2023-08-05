###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Testing

$Id: testing.py 3934 2014-03-17 07:38:52Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import z3c.form.testing


def setupFormDefaults():
    z3c.form.testing.setupFormDefaults()


def setUp(test=None):
    z3c.form.testing.setUp(test)
    setupFormDefaults()


def tearDown(test=None):
    z3c.form.testing.tearDown(test)
