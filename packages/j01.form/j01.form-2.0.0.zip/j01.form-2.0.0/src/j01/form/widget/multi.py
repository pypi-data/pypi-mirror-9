##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Multi Widget Implementation

$Id: select.py 78513 2007-07-31 23:03:47Z srichter $
"""
__docformat__ = "reStructuredText"
from operator import attrgetter

import zope.component
import zope.interface
import zope.i18nmessageid

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.widget

_ = zope.i18nmessageid.MessageFactory('p01')

from j01.form import btn
from j01.form import interfaces


@zope.interface.implementer(z3c.form.interfaces.IButtonForm,
    z3c.form.interfaces.IHandlerForm)
class FormMixin(object):
    pass


@zope.interface.implementer(interfaces.IMultiWidget)
class MultiWidget(z3c.form.browser.widget.HTMLFormElement,
    z3c.form.widget.MultiWidget, FormMixin):
    """Multi widget implementation."""

    buttons = btn.Buttons()

    prefix = 'widget'
    klass = u'multi-control form-control'
    css = u'multi'
    items = ()

    showLabel = True  # show labels for item subwidgets or not

    # Internal attributes
    # Internal attributes
    _adapterValueAttributes = ('label', 'name', 'required', 'title', 'showLabel')

    def updateActions(self):
        self.updateAllowAddRemove()
        if self.name is not None:
            self.prefix = self.name
        self.actions = zope.component.getMultiAdapter(
            (self, self.request, self), z3c.form.interfaces.IActions)
        self.actions.update()

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(MultiWidget, self).update()
        self.updateActions()
        self.actions.execute()
        self.updateActions()  # Update again, as conditions may change

    @btn.buttonAndHandler(_('Add'), name='add',
        condition=attrgetter('allowAdding'))
    def handleAdd(self, action):
        self.appendAddingWidget()

    @btn.buttonAndHandler(_('Remove selected'), name='remove',
        condition=attrgetter('allowRemoving'))
    def handleRemove(self, action):
        self.removeWidgets([widget.name for widget in self.widgets
                            if ('%s.remove' % (widget.name)) in self.request])


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getMultiFieldWidget(field, request):
    """IFieldWidget factory for MultiWidget."""
    widget = MultiWidget(request)
    return z3c.form.widget.FieldWidget(field, widget)


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getMultiFieldWidgetDispatcher(field, value_type, request):
    """IFieldWidget factory for MultiWidget."""
    return getMultiFieldWidget(field, request)
