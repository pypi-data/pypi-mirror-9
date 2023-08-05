###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Exceptions

$Id: exceptions.py 3979 2014-03-25 10:59:26Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.schema

_ = zope.i18nmessageid.MessageFactory('p01')


# password confirmation
class PasswordComparsionError(zope.schema.ValidationError):
    __doc__ = _("""Password doesn't compare with confirmation value""")
