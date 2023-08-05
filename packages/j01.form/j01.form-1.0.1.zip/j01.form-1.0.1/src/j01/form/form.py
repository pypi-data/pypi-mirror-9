##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Form classes
$Id: form.py 4011 2014-04-04 02:25:13Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import sys

import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
import zope.i18nmessageid
from zope.traversing.browser import absoluteURL
from zope.schema.interfaces import IField
from zope.schema.interfaces import RequiredMissing

import z3c.form.form
import z3c.form.error
import z3c.form.button
import z3c.form.interfaces
from z3c.template.template import getLayoutTemplate
from z3c.template.template import getPageTemplate

import j01.form
from j01.form import btn
from j01.form import interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


applyChanges = z3c.form.form.applyChanges


# supports z3c.form and j01.jsonrpc button and handlers
def extends(*args, **kwargs):
    """Copy form button, handler and fields from given form
    
    Note: this method supports both (z3c.form and j01.jsonrpc) concepts and
    uses the correct button and handlers.
    """
    frame = sys._getframe(1)
    f_locals = frame.f_locals
    if not kwargs.get('ignoreFields', False):
        f_locals['fields'] = z3c.form.field.Fields()
        for arg in args:
            f_locals['fields'] += getattr(arg, 'fields',
                z3c.form.field.Fields())
    if not kwargs.get('ignoreButtons', False):
        f_locals['buttons'] = btn.Buttons()
        for arg in args:
            f_locals['buttons'] += getattr(arg, 'buttons', btn.Buttons())
    if not kwargs.get('ignoreHandlers', False):
        f_locals['handlers'] = btn.Handlers()
        for arg in args:
            f_locals['handlers'] += getattr(arg, 'handlers', btn.Buttons())



###############################################################################
#
# browser request form classes

class IFormButtons(zope.interface.Interface):
    """Form buttons"""

    add = btn.Button(
        title=_(u"Add"),
        css='btn btn-add',
        )

    apply = btn.Button(
        title=_(u"Apply"),
        css='btn btn-apply',
        )

    cancel = btn.Button(
        title=_(u"Cancel"),
        css='btn btn-cancel',
        )


@zope.interface.implementer(interfaces.IForm)
class Form(j01.form.FormMixin, z3c.form.form.Form):
    """Simple form"""


@zope.interface.implementer(interfaces.IDisplayForm)
class DisplayForm(j01.form.FormMixin, z3c.form.form.Form):
    """Form for displaying fields (supporting buttons too)"""

    mode = z3c.form.interfaces.DISPLAY_MODE
    ignoreRequest = True


@zope.interface.implementer(interfaces.IAddForm)
class AddForm(j01.form.AddFormMixin, z3c.form.form.AddForm):
    """Add form."""

    ignoreRequest = True
    showCancel = True

    @btn.buttonAndHandler(IFormButtons['add'])
    def handleAdd(self, action):
        self.doHandleAdd(action)

    @btn.buttonAndHandler(IFormButtons['cancel'],
        condition=lambda form: form.showCancel)
    def handleCancel(self, action):
        self.doHandleCancel(action)


@zope.interface.implementer(interfaces.IEditForm)
class EditForm(j01.form.EditFormMixin, z3c.form.form.EditForm):
    """Edit form"""

    showCancel = True

    @btn.buttonAndHandler(IFormButtons['apply'])
    def handleApply(self, action):
        self.doHandleApply(action)

    @btn.buttonAndHandler(IFormButtons['cancel'],
        condition=lambda form: form.showCancel)
    def handleCancel(self, action):
        self.doHandleCancel(action)


###############################################################################
#
# jsonrpc request form classes

class IJSONRPCButtons(zope.interface.Interface):

    add = btn.JSONRPCButton(
        title=_(u'Add'),
        css='btn btn-add',
        )

    apply = btn.JSONRPCButton(
        title=_(u'Apply'),
        css='btn btn-apply',
        )

    cancel = btn.JSONRPCButton(
        title=_(u'Cancel'),
        css='btn btn-cancel',
        )


@zope.interface.implementer(interfaces.IJSONRPCForm)
class JSONRPCForm(j01.form.JSONRPCMixin, j01.form.FormMixin,
    z3c.form.form.Form):
    """JSONRPC form mixin."""


@zope.interface.implementer(interfaces.IJSONRPCAddForm)
class JSONRPCAddForm(j01.form.JSONRPCMixin, j01.form.AddFormMixin,
    z3c.form.form.AddForm):
    """JSONRPC add form."""

    showCancel = True

    @btn.buttonAndHandler(IJSONRPCButtons['add'])
    def handleAdd(self, action):
        self.doHandleAdd(action)

    @btn.buttonAndHandler(IJSONRPCButtons['cancel'],
        condition=lambda form: form.showCancel)
    def handleCancel(self, action):
        self.doHandleCancel(action)


@zope.interface.implementer(interfaces.IJSONRPCEditForm)
class JSONRPCEditForm(j01.form.JSONRPCMixin, j01.form.EditFormMixin,
    z3c.form.form.EditForm):
    """JSONRPC edit form."""

    showCancel = True

    @btn.buttonAndHandler(IJSONRPCButtons['apply'])
    def handleApply(self, action):
        self.doHandleApply(action)

    @btn.buttonAndHandler(IJSONRPCButtons['cancel'],
        condition=lambda form: form.showCancel)
    def handleCancel(self, action):
        self.doHandleCancel(action)


###############################################################################
#
# dialog form classes

class IDialogButtons(zope.interface.Interface):
    """Dialog form buttons"""

    add = btn.DialogButton(
        title=_(u'Add'),
        css='btn btn-add',
        )

    applyChanges = btn.DialogButton(
        title=_(u'Apply'),
        css='btn btn-apply',
        )

    cancel = btn.DialogButton(
        title=_(u'Cancel'),
        css='btn btn-cancel',
        )

    close = btn.DialogCloseButton(
        title=_(u'Close'),
        css='btn btn-close',
        )

    delete = btn.DialogButton(
        title=_(u'Delete'),
        css='btn btn-delete',
        )

    confirm = btn.DialogButton(
        title=_(u'Confirm'),
        css='btn btn-confirm',
        )


class DialogMixin(object):
    """Dialog mixin class"""

    zope.interface.implements(interfaces.IDialogForm)

    layout = getLayoutTemplate(name='dialog')
    template = getPageTemplate()

    prefix = 'dialog'

    j01DialogTitle = None
    closeDialog = False
    nextURL = None
    contentTargetExpression = None

    def setNextURL(self, url, status, closeDialog=True):
        """Helper for set a nextURL including status message and closeDialog"""
        self.closeDialog = closeDialog
        super(DialogMixin, self).setNextURL(url, status)

    def renderClose(self):
        """Return content if you need to render content after close."""
        return None

    def render(self):
        # knows what to return for the dialog parent
        if self.closeDialog:
            return self.renderClose()
        return self.template()


class DialogForm(DialogMixin, JSONRPCForm):
    """Dialog JSONRPC form."""

    zope.interface.implements(interfaces.IDialogForm)


class DialogEditForm(DialogMixin, JSONRPCEditForm):
    """Dialog JSONRPC edit form."""

    zope.interface.implements(interfaces.IDialogEditForm)

    closeOnApplyWithoutError = True

    def doHandleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = self.successMessage
            # close on apply without error
            if self.closeOnApplyWithoutError:
                self.closeDialog = True
        else:
            self.status = self.noChangesMessage
            # close on apply without error
            if self.closeOnApplyWithoutError:
                self.closeDialog = True
        return changes

    def doHandleCancel(self, action):
        self.closeDialog = True

    @btn.buttonAndHandler(IDialogButtons['applyChanges'])
    def handleApply(self, action):
        self.doHandleApply(action)

    @btn.buttonAndHandler(IDialogButtons['cancel'])
    def handleCancel(self, action):
        self.doHandleCancel(action)


class DialogAddForm(DialogMixin, JSONRPCAddForm):
    """Dialog JSONRPC edit form."""

    zope.interface.implements(interfaces.IDialogAddForm)

    def doHandleAdd(self, action):
        # Note we, use the data from the request.form
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True
            self.closeDialog = True
        return obj

    def doHandleCancel(self, action):
        self.closeDialog = True

    @btn.buttonAndHandler(IDialogButtons['add'])
    def handleAdd(self, action):
        self.doHandleAdd(action)

    @btn.buttonAndHandler(IDialogButtons['cancel'])
    def handleCancel(self, action):
        self.doHandleCancel(action)


class DialogDeleteForm(DialogForm):
    """Dialog JSONRPC delete form."""

    zope.interface.implements(interfaces.IDialogDeleteForm)

    ignoreContext = True

    def doHandleDelete(self, action):
        raise NotImplementedError(
            'Subclass must implement doHandleDelete')

    def doHandleCancel(self, action):
        self.closeDialog = True

    @btn.buttonAndHandler(IDialogButtons['delete'])
    def handleDelete(self, action):
        self.doHandleDelete(action)

    @btn.buttonAndHandler(IDialogButtons['cancel'])
    def handleCancel(self, action):
        self.doHandleCancel(action)


class DialogConfirmForm(DialogForm):
    """Dialog JSONRPC confirm form."""

    zope.interface.implements(interfaces.IDialogConfirmForm)

    ignoreContext = True

    def doHandleConfirm(self, action):
        raise NotImplementedError('Subclass must implement doHandleConfirm')

    def doHandleCancel(self, action):
        self.closeDialog = True

    @btn.buttonAndHandler(IDialogButtons['confirm'])
    def handleConfirm(self, action):
        self.doHandleConfirm(action)

    @btn.buttonAndHandler(IDialogButtons['cancel'])
    def handleCancel(self, action):
        self.doHandleCancel(action)
