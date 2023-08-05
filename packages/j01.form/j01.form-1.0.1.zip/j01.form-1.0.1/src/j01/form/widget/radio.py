###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Radio widget
$Id: radio.py 3934 2014-03-17 07:38:52Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import sys

import zope.i18n
import zope.component
import zope.interface
import zope.schema.interfaces
from zope.pagetemplate.interfaces import IPageTemplate

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.util
import z3c.form.browser.widget

from j01.form import interfaces
from j01.form.layer import IFormLayer
from j01.form.widget.widget import WidgetMixin

PY3 = sys.version_info[0] >= 3

try:
    unicode
except NameError:
    # Py3: Define unicode.
    unicode = str

def toUnicode(obj):
    if isinstance(obj, bytes):
        return obj.decode('utf-8', 'ignore')
    if PY3:
        return str(obj)
    else:
        return unicode(obj)


class RadioWidget(WidgetMixin, z3c.form.browser.widget.HTMLInputWidget,
    z3c.form.widget.SequenceWidget):
    """RadioWidget using a div wrapper for option tags"""

    zope.interface.implementsOnly(interfaces.IRadioWidget)

    klass = u'radio-control' # no form-control
    css = u'radio'

    def isChecked(self, term):
        return term.token in self.value

    def renderForValue(self, value):
        term = self.terms.getTermByToken(value)
        checked = self.isChecked(term)
        id = '%s-%i' % (self.id, list(self.terms).index(term))
        item = {'id': id, 'name': self.name, 'value': term.token,
                'checked': checked}
        template = zope.component.getMultiAdapter(
            (self.context, self.request, self.form, self.field, self),
            IPageTemplate, name=self.mode + '_single')
        return template(self, item)

    @property
    def items(self):
        items = []
        for count, term in enumerate(self.terms):
            checked = self.isChecked(term)
            id = '%s-%i' % (self.id, count)
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                label = zope.i18n.translate(term.title, context=self.request,
                    default=term.title)
            else:
                label = toUnicode(term.value)
            items.append(
                {'id':id, 'name':self.name, 'value':term.token,
                 'label':label, 'checked':checked})
        return items


class RadioInlineWidget(RadioWidget):
    """RadioWidget using a span wrapper for option tags"""


JAVASCRIPT = """
<script type="text/javascript">
$(document).ready(function(){
    $('input[name^="%s"]').picker();
});
</script>
"""


class RadioPickerWidget(RadioWidget):
    """RadioPickerWidget using a div wrapper for option tags"""

    klass = u'radio-picker-control' # no form-control
    css = u'radio-picker'

    @property
    def javascript(self):
        return JAVASCRIPT % self.name.replace('.', '\\\.')


class RadioInlinePickerWidget(RadioWidget):
    """RadioInlinePickerWidget using a span wrapper for option tags"""

    klass = u'radio-picker-control'
    css = u'radio-inline-picker'

    @property
    def javascript(self):
        return JAVASCRIPT % self.name.replace('.', '\\\.')


# get
@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getRadioWidget(field, request):
    """IFieldWidget factory for RadioWidget."""
    return z3c.form.widget.FieldWidget(field, RadioWidget(request))


@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getRadioInlineWidget(field, request):
    """IFieldWidget factory for RadioWidget."""
    return z3c.form.widget.FieldWidget(field, RadioInlineWidget(request))


@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getRadioPickerWidget(field, request):
    """IFieldWidget factory for RadioWidget."""
    return z3c.form.widget.FieldWidget(field, RadioPickerWidget(request))


@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getRadioInlinePickerWidget(field, request):
    """IFieldWidget factory for RadioWidget."""
    return z3c.form.widget.FieldWidget(field, RadioInlinePickerWidget(request))