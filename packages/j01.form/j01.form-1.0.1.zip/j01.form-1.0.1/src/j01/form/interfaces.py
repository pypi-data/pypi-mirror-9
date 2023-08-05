###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Interfaces

$Id: interfaces.py 4116 2014-10-28 20:27:00Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.schema
import zope.interface
import zope.i18nmessageid

import z3c.form.interfaces

import j01.dialog.interfaces
import j01.jsonrpc.interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


###############################################################################
#
# form

class IForm(zope.interface.Interface):
    """Simple form"""

    refreshWidgets = zope.schema.Bool(
        title=u'Refresh widgets',
        description=(u'A flag, when set, causes form widgets to be updated '
                     u'again after action execution.'),
        default=False,
        required=True)

    refreshActions = zope.schema.Bool(
        title=u'Refresh actions',
        description=(u'A flag, when set, causes form actions to be updated '
                     u'again after action execution.'),
        default=False,
        required=True)

    def setUpWidgetValidation(name):
        """Support for single widget ssetup used by j01.validate"""


class IDisplayForm(IForm, z3c.form.interfaces.IDisplayForm):
    """Display Form"""


class IAddForm(IForm, z3c.form.interfaces.IAddForm):
    """Add form."""


class IEditForm(IForm, z3c.form.interfaces.IEditForm):
    """Edit form."""


###############################################################################
#
# jsonrpc form

class IJSONRPCForm(IForm, j01.jsonrpc.interfaces.IJSONRPCForm):
    """JSON-RPC base form mixin class."""


class IJSONRPCAddForm(IJSONRPCForm, j01.jsonrpc.interfaces.IJSONRPCAddForm):
    """JSON-RPC based add form."""


class IJSONRPCEditForm(IJSONRPCForm, j01.jsonrpc.interfaces.IJSONRPCEditForm):
    """JSON-RPC based edit form."""


###############################################################################
#
# dialog form

class IDialogForm(IForm, j01.dialog.interfaces.IDialogPage):
    """Dialog form."""


class IDialogAddForm(IDialogForm, j01.dialog.interfaces.IDialogAddForm):
    """Dialog add form."""


class IDialogEditForm(IDialogForm, j01.dialog.interfaces.IDialogEditForm):
    """Dialog edit form."""


class IDialogDeleteForm(IDialogForm, j01.dialog.interfaces.IDialogDeleteForm):
    """Dialog delete form."""


class IDialogConfirmForm(IDialogForm, j01.dialog.interfaces.IDialogConfirmForm):
    """Dialog confirm form."""


###############################################################################
#
# widgets

class IWidget(z3c.form.interfaces.IWidget):
    """Enhanced widget supporting addons and description text"""

    description = zope.schema.TextLine(
        title=u'Description',
        description=u'Description',
        default=None,
        required=False)

    addOnBefore = zope.schema.TextLine(
        title=u'Addon before widget',
        description=u'Addon before widget',
        default=None,
        required=False)

    addOnAfter = zope.schema.TextLine(
        title=u'Addon after widget',
        description=u'Addon after widget',
        default=None,
        required=False)

    addOnWrapper = zope.schema.TextLine(
        title=u'Addon widget wrapper',
        description=u'Addon widget wrapper',
        default=None,
        required=False)


# html5 text
class ITextWidget(IWidget):
    """Text widget with placeholder and hint support"""

    pattern = zope.schema.ASCIILine(
        title=u'Validation pattern',
        description=u'Validation pattern',
        default=None,
        required=False)

    placeholder = zope.schema.TextLine(
        title=u'Placeholder',
        description=u'Placeholder',
        default=None,
        required=False)


class IEMailWidget(ITextWidget):
    """EMail input type widget"""


class IDateWidget(ITextWidget):
    """Date input type widget"""


class IDatetimeWidget(ITextWidget):
    """Datetime input type widget"""


class IDatetimeLocalWidget(ITextWidget):
    """Datetime local input type widget"""


class ITimeWidget(ITextWidget):
    """Time input type widget"""


class IWeekWidget(ITextWidget):
    """Week input type widget"""


class IMonthWidget(ITextWidget):
    """Month input type widget"""


class IColorWidget(ITextWidget):
    """Color input type widget"""


class ISearchWidget(ITextWidget):
    """Search input type widget"""


class IURLWidget(ITextWidget):
    """Search input type widget"""


class INumberWidget(ITextWidget):
    """Number input type widget"""


class ITelWidget(ITextWidget):
    """Tel input type widget"""


# checkbox
class ICheckBoxWidget(IWidget, z3c.form.interfaces.ICheckBoxWidget):
    """CheckBoxWidget using a div wrapper for option tags"""


class ICheckBoxInlineWidget(ICheckBoxWidget):
    """CheckBoxWidget using a span wrapper for option tags"""


class ISingleCheckBoxWidget(ICheckBoxWidget,
    z3c.form.interfaces.ISingleCheckBoxWidget):
    """Single checkbox using a div wrapper for option tags"""


class ISingleCheckBoxInlineWidget(ISingleCheckBoxWidget):
    """SingleCheckBoxWidget using a span wrapper for option tags"""


class ICheckBoxPickerWidget(ICheckBoxWidget):
    """Checkbox picker using a div wrapper for option tags"""


class ICheckBoxInlinePickerWidget(ICheckBoxWidget):
    """Checkbox picker using a span wrapper for option tags"""


class ISingleCheckBoxPickerWidget(ISingleCheckBoxWidget):
    """Single checkbox using a div wrapper for option tags"""


class ISingleCheckBoxInlinePickerWidget(ISingleCheckBoxPickerWidget):
    """SingleCheckBoxWidget using a span wrapper for option tags"""


# file
class IFileWidget(IWidget, z3c.form.interfaces.IFileWidget):
    """File widget."""


# password
class IPasswordWidget(ITextWidget, z3c.form.interfaces.IPasswordWidget):
    """Password widget with placeholder and hint support"""


class IPasswordConfirmationWidget(z3c.form.interfaces.ITextWidget):
    """Password including confirmation field widget."""


# radio
class IRadioWidget(IWidget, z3c.form.interfaces.IRadioWidget):
    """Radio widget."""

class IRadioInlineWidget(IRadioWidget):
    """Radio inline widget."""

class IRadioPickerWidget(IRadioWidget):
    """Radio picker widget."""

class IRadioInlinePickerWidget(IRadioWidget):
    """Radio inline picker widget."""


# select
class ISelectWidget(IWidget, z3c.form.interfaces.ISelectWidget):
    """Select widget with ITerms option."""


class IMultiSelectWidget(ISelectWidget):
    """Multi select widget"""


class ISelectPickerWidget(ISelectWidget):
    """MultiSelectPickerWidget"""


class IMultiSelectPickerWidget(ISelectPickerWidget, IMultiSelectWidget):
    """MultiSelectPickerWidget"""


class IGroupSelectWidget(ISelectWidget):
    """Select widget with optgroup support"""


# text lines
class ITextLinesWidget(IWidget, z3c.form.interfaces.ITextLinesWidget):
    """Text lines widget."""


# textarea
class ITextAreaWidget(IWidget, z3c.form.interfaces.ITextAreaWidget):
    """Text widget."""


# dictionary
class IDictKeyValueWidget(IWidget, z3c.form.interfaces.ITextAreaWidget):
    """Dict with key:value values as textarea widget."""


###############################################################################
#
# only availabe if j01.datepicker is available

try:
    import j01.datepicker.interfaces
    class IDatePickerWidget(IWidget,
        j01.datepicker.interfaces.IDatePickerWidget):
        """DatePicker date widget."""
except ImportError:
    pass


###############################################################################
#
# only availabe if j01.select2 is available

try:
    import j01.select2.interfaces
    # select
    class ISelect2Widget(IWidget, j01.select2.interfaces.ISelect2Widget):
        """Select2 widget for ISequence of IChoice."""


    # tagging
    class ITagListSelect2Widget(IWidget,
        j01.select2.interfaces.ITagListSelect2Widget):
        """Select2 widget for IList of ITextLine"""


    # single tag
    class ISingleTagSelect2Widget(IWidget,
        j01.select2.interfaces.ISingleTagSelect2Widget):
        """Select2 widget for ITextLine"""


    # livelist
    class ILiveListSelect2Widget(IWidget,
        j01.select2.interfaces.ILiveListSelect2Widget):
        """Select2 widget for IList of IChoice offering live autosuggest"""
except ImportError:
    pass
