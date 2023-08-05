###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Text widget
$Id: text.py 3979 2014-03-25 10:59:26Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.schema.interfaces

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.widget

from j01.form import interfaces
from j01.form.layer import IFormLayer
from j01.form.widget.widget import WidgetMixin


JAVASCRIPT = """
<script type="text/javascript">
  $("#%s").j01Placeholder();
</script>
"""


class TextWidget(WidgetMixin, z3c.form.browser.widget.HTMLTextInputWidget,
    z3c.form.widget.Widget):
    """Text input type widget"""

    zope.interface.implementsOnly(interfaces.ITextWidget)
    _type = 'text'

    klass = u'text-control form-control'
    css = u'text'
    value = u''

    addon = None
    placeholder = None
    pattern = None

    def extract(self, default=z3c.form.interfaces.NO_VALUE):
        """Return NO_VALUE if value is placeholder """
        value = self.request.get(self.name, default)
        if self.placeholder == value:
            # return empty string
            return u''
        else:
            # return default or NO_VALUE
            return value

    @property
    def javascript(self):
        if self.placeholder is not None:
            return JAVASCRIPT % self.id


class EMailWidget(TextWidget):
    """EMail input type widget"""

    zope.interface.implementsOnly(interfaces.IEMailWidget)
    _type = 'email'
    klass = u'email-control form-control'
    css = u'email'


class DateWidget(TextWidget):
    """Date input type widget"""

    zope.interface.implementsOnly(interfaces.IDateWidget)
    _type = 'date'
    klass = u'date-control form-control'
    css = u'date'


class DatetimeWidget(TextWidget):
    """Datetime input type widget"""

    zope.interface.implementsOnly(interfaces.IDatetimeWidget)
    _type = 'datetime'
    klass = u'datetime-control form-control'
    css = u'datetime'


class DatetimeLocalWidget(TextWidget):
    """Datetime local input type widget"""

    zope.interface.implementsOnly(interfaces.IDatetimeLocalWidget)
    _type = 'datetime-local'
    klass = u'datetime-local-control form-control'
    css = u'datetime-local'


class TimeWidget(TextWidget):
    """Time input type widget"""

    zope.interface.implementsOnly(interfaces.ITimeWidget)
    _type = 'time'
    klass = u'time-control form-control'
    css = u'time'


class WeekWidget(TextWidget):
    """Week input type widget"""

    zope.interface.implementsOnly(interfaces.IWeekWidget)
    _type = 'week'
    klass = u'week-control form-control'
    css = u'week'


class MonthWidget(TextWidget):
    """Month input type widget"""

    zope.interface.implementsOnly(interfaces.IMonthWidget)
    _type = 'month'
    klass = u'month-control form-control'
    css = u'month'


class ColorWidget(TextWidget):
    """Color input type widget"""

    zope.interface.implementsOnly(interfaces.IColorWidget)
    _type = 'color'
    klass = u'color-control form-control'
    css = u'color'


class SearchWidget(TextWidget):
    """Search input type widget"""

    zope.interface.implementsOnly(interfaces.ISearchWidget)
    _type = 'search'
    klass = u'search-control form-control'
    css = u'search'


class URLWidget(TextWidget):
    """URL input type widget"""

    zope.interface.implementsOnly(interfaces.IURLWidget)
    _type = 'url'
    klass = u'url-control form-control'
    css = u'url'


class NumberWidget(TextWidget):
    """Number input type widget"""

    zope.interface.implementsOnly(interfaces.INumberWidget)
    _type = 'number'
    klass = u'number-control form-control'
    css = u'number'


class TelWidget(TextWidget):
    """Tel input type widget"""

    zope.interface.implementsOnly(interfaces.ITelWidget)
    _type = 'tel'
    klass = u'tel-control form-control'
    css = u'tel'


# text
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getTextWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return z3c.form.widget.FieldWidget(field, TextWidget(request))


# email
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getEMailWidget(field, request):
    """IFieldWidget factory for EMailWidget."""
    return z3c.form.widget.FieldWidget(field, EMailWidget(request))


# date
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getDateWidget(field, request):
    """IFieldWidget factory for DateWidget."""
    return z3c.form.widget.FieldWidget(field, DateWidget(request))


# datetime
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getDatetimeWidget(field, request):
    """IFieldWidget factory for DateWidget."""
    return z3c.form.widget.FieldWidget(field, DatetimeWidget(request))


# datetime-local
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getDatetimeLocalWidget(field, request):
    """IFieldWidget factory for DatetimeLocalWidget."""
    return z3c.form.widget.FieldWidget(field, DatetimeLocalWidget(request))


# time
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getTimeWidget(field, request):
    """IFieldWidget factory for TimeWidget."""
    return z3c.form.widget.FieldWidget(field, TimeWidget(request))


# week
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getWeekWidget(field, request):
    """IFieldWidget factory for WeekWidget."""
    return z3c.form.widget.FieldWidget(field, WeekWidget(request))


# month
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getMonthWidget(field, request):
    """IFieldWidget factory for MonthWidget."""
    return z3c.form.widget.FieldWidget(field, MonthWidget(request))


# color
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getColorWidget(field, request):
    """IFieldWidget factory for ColorWidget."""
    return z3c.form.widget.FieldWidget(field, ColorWidget(request))


# search
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getSearchWidget(field, request):
    """IFieldWidget factory for SearchWidget."""
    return z3c.form.widget.FieldWidget(field, SearchWidget(request))


# url
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getURLWidget(field, request):
    """IFieldWidget factory for URLWidget."""
    return z3c.form.widget.FieldWidget(field, URLWidget(request))


# number
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getNumberWidget(field, request):
    """IFieldWidget factory for NumberWidget."""
    return z3c.form.widget.FieldWidget(field, NumberWidget(request))


# tel
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getTelWidget(field, request):
    """IFieldWidget factory for TelWidget."""
    return z3c.form.widget.FieldWidget(field, TelWidget(request))
