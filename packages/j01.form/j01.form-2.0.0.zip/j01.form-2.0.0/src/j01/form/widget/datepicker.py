##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
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
"""
$Id: datepicker.py 3934 2014-03-17 07:38:52Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface

import z3c.form.widget

import j01.datepicker.widget

from j01.form import interfaces


# date widget
class DatePickerWidget(j01.datepicker.widget.DatePickerWidget):
    """Upload widget implementation."""

    zope.interface.implementsOnly(interfaces.IDatePickerWidget)

    klass = u'datepicker-control form-control'
    css = u'datepicker'


def getDatePickerWidget(field, request):
    """IFieldWidget factory for ItemsWidget."""
    return z3c.form.widget.FieldWidget(field, DatePickerWidget(request))


def getStartDatePickerWidget(field, request):
    """IFieldWidget factory for ItemsWidget."""
    # this widget uses the default timeAppendix settings '00:00:00'
    # and prevents selecting previous dates
    widget = DatePickerWidget(request)
    widget.skipPastDates = True
    return z3c.form.widget.FieldWidget(field, widget)


def getEndDatePickerWidget(field, request):
    """IFieldWidget factory for ItemsWidget."""
    # this widget uses the default timeAppendix settings '23:59:59'
    # and prevents selecting previous dates
    widget = DatePickerWidget(request)
    widget.timeAppendix = '23:59:59'
    widget.skipPastDates = True
    return z3c.form.widget.FieldWidget(field, widget)
