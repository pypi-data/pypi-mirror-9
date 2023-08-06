##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: select2.py 3942 2014-03-24 08:59:21Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface

import z3c.form.widget
import z3c.form.interfaces

import j01.select2.widget

from j01.form import interfaces
from j01.form.widget.widget import WidgetMixin


TAG_INIT_SELECTION_SCRIPT = j01.select2.widget.TAG_INIT_SELECTION_SCRIPT
RESULT_QUERY_SCRIPT = j01.select2.widget.RESULT_QUERY_SCRIPT
SINGLE_TAG_INIT_SELECTION_SCRIPT = \
    j01.select2.widget.SINGLE_TAG_INIT_SELECTION_SCRIPT
LIVELIST_INIT_SELECTION_SCRIPT = \
    j01.select2.widget.LIVELIST_INIT_SELECTION_SCRIPT
LIVELIST_RESULT_QUERY_SCRIPT = j01.select2.widget.LIVELIST_RESULT_QUERY_SCRIPT


class Select2Widget(WidgetMixin, j01.select2.widget.Select2Widget):
    """Selects input widget"""

    zope.interface.implementsOnly(interfaces.ISelect2Widget)

    klass = u'select2-control'
    css = u'select2'


class TagListSelect2Widget(WidgetMixin,
    j01.select2.widget.TagListSelect2Widget):
    """Widget for IList of ITextLine
    
    This widget is based on a IList of ITextLine field, this means we can enter
    custom text data and the JSON-RPC callback is used for autosuggest
    useable input.

    """

    zope.interface.implementsOnly(interfaces.ITagListSelect2Widget)

    klass = u'select2-taglist-control'
    css = u'select2-taglist'


class SingleTagSelect2Widget(WidgetMixin,
    j01.select2.widget.SingleTagSelect2Widget):
    """Widget for ITextLine supporting jsonrpc autosuggest callback"""

    zope.interface.implementsOnly(interfaces.ISingleTagSelect2Widget)

    klass = u'select2-singletag-control'
    css = u'select2-singletag'


class LiveListSelect2Widget(WidgetMixin,
    j01.select2.widget.LiveListSelect2Widget):
    """Widget for IList of IChoice"""

    zope.interface.implementsOnly(interfaces.ILiveListSelect2Widget)

    klass = u'select2-livelist-control'
    css = u'select2-livelist'


# HTML select element
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getSelect2Widget(field, request):
    """IFieldWidget factory for Select2Widget."""
    return z3c.form.widget.FieldWidget(field, Select2Widget(request))


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getSingleSelect2Widget(field, request):
    """IFieldWidget factory for Select2Widget."""
    widget = z3c.form.widget.FieldWidget(field, Select2Widget(request))
    widget.multiple = None
    return widget


# tagging
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getTagListSelect2Widget(field, request):
    """IFieldWidget factory for TagListSelect2Widget."""
    return z3c.form.widget.FieldWidget(field, TagListSelect2Widget(request))


# live list
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getLiveListSelect2Widget(field, request):
    """IFieldWidget factory for LiveListSelect2Widget."""
    return z3c.form.widget.FieldWidget(field, LiveListSelect2Widget(request))

