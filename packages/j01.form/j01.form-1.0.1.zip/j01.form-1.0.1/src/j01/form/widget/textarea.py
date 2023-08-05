###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Textarea widget
$Id: textarea.py 3934 2014-03-17 07:38:52Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
import zope.schema.interfaces

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.widget

from j01.form import interfaces
from j01.form.layer import IFormLayer
from j01.form.widget.widget import WidgetMixin


class TextAreaWidget(WidgetMixin, z3c.form.browser.widget.HTMLTextAreaWidget,
    z3c.form.widget.Widget):
    """Textarea widget"""

    zope.interface.implementsOnly(interfaces.ITextAreaWidget)

    klass = u'textarea-control form-control'
    css = u'textarea'
    value = u''


# get
@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getTextAreaWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return z3c.form.widget.FieldWidget(field, TextAreaWidget(request))
