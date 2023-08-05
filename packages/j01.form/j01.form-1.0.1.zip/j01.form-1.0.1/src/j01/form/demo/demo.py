##############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: demo.py 4011 2014-04-04 02:25:13Z roger.ineichen $
"""

import zope.interface
import zope.schema

from z3c.form import field

import p01.schema

from j01.form import btn
from j01.form import form

# checkbox
from j01.form.widget import getCheckBoxWidget
from j01.form.widget import getCheckBoxInlineWidget

from j01.form.widget import getSingleCheckBoxWidget
from j01.form.widget import getSingleCheckBoxInlineWidget

from j01.form.widget import getCheckBoxPickerWidget
from j01.form.widget import getCheckBoxInlinePickerWidget

from j01.form.widget import getSingleCheckBoxPickerWidget
from j01.form.widget import getSingleCheckBoxInlinePickerWidget

# radio
from j01.form.widget import getRadioWidget
from j01.form.widget import getRadioInlineWidget
from j01.form.widget import getRadioPickerWidget
from j01.form.widget import getRadioInlinePickerWidget

# select
from j01.form.widget import getSelectPickerWidget
from j01.form.widget import getMultiSelectPickerWidget
try:
    from j01.form.widget import getSelect2Widget
    from j01.form.widget import getSingleSelect2Widget
except ImportError:
    getSelect2Widget = None
    getSingleSelect2Widget = None
try:
    from j01.form.widget import getDatePickerWidget
except ImportError:
    getDatePickerWidget = None


class IDemoSchema(zope.interface.Interface):
    """Demo schema"""

    textline = zope.schema.TextLine(
        title=u'TextLine',
        description=u'TextLine Description',
        required=True)

    text = zope.schema.Text(
        title=u'Text',
        description=u'Text Description',
        required=True)

    password = zope.schema.TextLine(
        title=u'Password',
        description=u'Password Description',
        required=True)

    date = zope.schema.Date(
        title=u'Date',
        description=u'Date Description',
        required=True)

    datetime = zope.schema.Datetime(
        title=u'Datetime',
        description=u'Datetime Description',
        required=True)

    email = p01.schema.EMail(
        title=u'EMail',
        description=u'EMail Description',
        required=True)
    # checkbox
    checkbox = zope.schema.List(
        title=u'CheckBoxWidget',
        description=u'CheckBoxWidget',
        value_type=zope.schema.Choice(
            title=u'Checkbox',
            values=[1,2,3],
        ),
        required=False)

    checkBoxInline = zope.schema.List(
        title=u'CheckBoxInlineWidget',
        description=u'CheckBoxInlineWidget',
        value_type=zope.schema.Choice(
            title=u'Checkbox',
            values=[1,2,3],
        ),
        required=False)

    singleCheckBox = zope.schema.Choice(
        title=u'SingleCheckBoxWidget',
        description=u'SingleCheckBoxWidget',
        values=[1,2,3],
        required=False)

    singleCheckBoxInline = zope.schema.Choice(
        title=u'SingleCheckBoxInlineWidget',
        description=u'SingleCheckBoxInlineWidget',
        values=[1,2,3],
        required=False)

    # checkbox picker
    checkBoxPicker = zope.schema.List(
        title=u'CheckBoxPickerWidget',
        description=u'CheckBoxPickerWidget',
        value_type=zope.schema.Choice(
            title=u'Checkbox',
        values=[1,2,3],
        ),
        required=False)

    checkBoxInlinePicker = zope.schema.List(
        title=u'CheckBoxInlinePickerWidget',
        description=u'CheckBoxInlinePickerWidget',
        value_type=zope.schema.Choice(
            title=u'Checkbox',
        values=[1,2,3],
        ),
        required=False)

    singleCheckBoxInlinePicker = zope.schema.Choice(
        title=u'SingleCheckBoxInlinePickerWidget',
        description=u'SingleCheckBoxInlinePickerWidget',
        values=[1,2,3],
        required=False)

    singleCheckBoxPicker = zope.schema.Choice(
        title=u'SingleCheckBoxPickerWidget',
        description=u'SingleCheckBoxPickerWidget',
        values=[1,2,3],
        required=False)

    singleCheckBoxInlinePicker = zope.schema.Choice(
        title=u'SingleCheckBoxInlinePickerWidget',
        description=u'SingleCheckBoxInlinePickerWidget',
        values=[1,2,3],
        required=False)


    # radio widgets
    radio = zope.schema.Choice(
        title=u'RadioWidget',
        description=u'RadioWidget',
        values=[1,2,3],
        required=False)

    radioInline = zope.schema.Choice(
        title=u'RadioInlineWidget',
        description=u'RadioInlineWidget',
        values=[1,2,3],
        required=False)

    radioPicker = zope.schema.Choice(
        title=u'RadioPickerWidget',
        description=u'RadioPickerWidget',
        values=[1,2,3],
        required=False)

    radioInlinePicker = zope.schema.Choice(
        title=u'RadioInlinePickerWidget',
        description=u'RadioInlinePickerWidget',
        values=[1,2,3],
        required=False)


    # features
    textHelp = zope.schema.TextLine(
        title=u'Text with help below',
        description=u'Help below input field',
        required=True)

    allInOne = zope.schema.TextLine(
        title=u'All in one widget',
        description=u'Description text for all in one widget',
        required=False)

    addOn = zope.schema.TextLine(
        title=u'Addon widget',
        description=u'Description text for addon widget',
        required=False)

    addOnAfter = zope.schema.TextLine(
        title=u'Addon after widget',
        description=u'Description text for addon after widget',
        required=False)

    # select
    selectPicker = zope.schema.Choice(
        title=u'Select picker widget',
        description=u'Select picker widget',
        values=[1,2,3],
        required=False)

    multiSelectPicker = zope.schema.List(
        title=u'Multi select picker widget',
        description=u'Multi select picker widget',
        value_type=zope.schema.Choice(
            title=u'Multi select picker',
        values=[1,2,3],
        ),
        required=False)

    # select2
    singleSelect2 = zope.schema.Choice(
        title=u'Single select2 widget',
        description=u'Single select2 widget',
        values=[1,2,3],
        required=False)

    select2 = zope.schema.List(
        title=u'Select2 widget',
        description=u'Select2 widget',
        value_type=zope.schema.Choice(
            title=u'Multi select picker',
            values=[1,2,3],
        ),
        required=False)

    # datepicker
    datepicker = zope.schema.Date(
        title=u'Datepicker',
        description=u'Datepicker Description',
        required=True)


class IDemoButtons(zope.interface.Interface):
    """Demo buttons"""

    simple = btn.Button(
        title=u'No css',
        )

    simplePrimary = btn.Button(
        title=u'Primary',
        )

    simpleSecondary = btn.Button(
        title=u'Secondary',
        )

    simpleLink= btn.Button(
        title=u'Link',
        )

    default = btn.Button(
        title=u'Default',
        css='btn btn-default',
        )

    primary = btn.Button(
        title=u'Primary',
        css='btn btn-primary',
        )

    info = btn.Button(
        title=u'Info',
        css='btn btn-info',
        )

    warning = btn.Button(
        title=u'Warning',
        css='btn btn-warning',
        )

    danger = btn.Button(
        title=u'Danger',
        css='btn btn-danger',
        )

    link = btn.Button(
        title=u'Link',
        css='btn btn-link',
        )


class DemoForm(form.Form):
    """Demo form"""

    ignoreContext = True

    fields = field.Fields(IDemoSchema).select(
        'textline',
        'text',
        'password',
        'date',
        'datetime',
        'email',

        # checkbox
        'checkbox',
        'checkBoxInline',
        'singleCheckBox',
        'singleCheckBoxInline',

        # checkbox picker
        'checkBoxPicker',
        'checkBoxInlinePicker',
        'singleCheckBoxPicker',
        'singleCheckBoxInlinePicker',

        # radio
        'radio',
        'radioInline',

        # radio picker
        'radioPicker',
        'radioInlinePicker',

        # select picker
        'selectPicker',
        'multiSelectPicker',

        # select2
        'singleSelect2',
        'select2',
        'datepicker',

        # variants
        'textHelp',
        'allInOne',
        'addOnAfter',
        'addOn',
        )

    widgetFactories = {

        # checkbox
        'checkbox': getCheckBoxWidget,
        'checkBoxInline': getCheckBoxInlineWidget,
        'singleCheckBox': getSingleCheckBoxWidget,
        'singleCheckBoxInline': getSingleCheckBoxInlineWidget,

        # checkbox picker
        'checkBoxPicker': getCheckBoxPickerWidget,
        'checkBoxInlinePicker': getCheckBoxInlinePickerWidget,
        'singleCheckBoxPicker': getSingleCheckBoxPickerWidget,
        'singleCheckBoxInlinePicker': getSingleCheckBoxInlinePickerWidget,

        # radio
        'radio': getRadioWidget,
        'radioInline': getRadioInlineWidget,

        # radio picker
        'radioPicker': getRadioPickerWidget,
        'radioInlinePicker': getRadioInlinePickerWidget,

        # select picker
        'selectPicker': getSelectPickerWidget,
        'multiSelectPicker': getMultiSelectPickerWidget,
        # select 2
        'singleSelect2': getSingleSelect2Widget,
        'select2': getSelect2Widget,
        'datepicker': getDatePickerWidget,
        }

    widgetLabels = {
        'allInOne': u"Override all in one widget label"
        }

    widgetTitles = {
        'allInOne': u"Use 3 uppercase letters followed by 4 digits."
        }

    widgetRequireds = {
        'allInOne': True,
        'addOn': True,
        'addOnAfter': True,
        }

    widgetPlaceholders = {
        'allInOne': u"All in one placeholder"
        }

    widgetPatterns = {
        'allInOne': '[A-Z]{3}[0-9]{4}'
        }

    widgetDescriptions = {
        'textHelp': True,
        'allInOne': True,
        'addOn': u"Add on description",
        'addOnAfter': u"Add on after description",
        }

    widgetAfterAddOns = {
        'addOnAfter': u'<span class="input-group-addon">@</span>',
        'addOn': u'<span class="input-group-addon">a</span>',
        }
    widgetBeforeAddOns = {
        'addOn': u'<span class="input-group-addon">b</span>',
        }

    def getWigdetSource(self, name):
        return self.widgets[name].render()

    def justValidate(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

    # no css styles
    @btn.buttonAndHandler(IDemoButtons['simple'])
    def handleSimple(self, action):
        self.justValidate(action)

    @btn.buttonAndHandler(IDemoButtons['simplePrimary'])
    def handleSimplePrimary(self, action):
        self.justValidate(action)

    @btn.buttonAndHandler(IDemoButtons['simpleSecondary'])
    def handleSimpleSecondary(self, action):
        self.justValidate(action)

    @btn.buttonAndHandler(IDemoButtons['simpleLink'])
    def handleSimpleLink(self, action):
        self.justValidate(action)

    # bootstrap buttons
    @btn.buttonAndHandler(IDemoButtons['default'])
    def handleDefault(self, action):
        self.justValidate(action)

    @btn.buttonAndHandler(IDemoButtons['primary'])
    def handlePrimary(self, action):
        self.justValidate(action)

    @btn.buttonAndHandler(IDemoButtons['info'])
    def handleInfo(self, action):
        self.justValidate(action)

    @btn.buttonAndHandler(IDemoButtons['warning'])
    def handleWarning(self, action):
        self.justValidate(action)

    @btn.buttonAndHandler(IDemoButtons['danger'])
    def handleDanger(self, action):
        self.justValidate(action)

    @btn.buttonAndHandler(IDemoButtons['link'])
    def handleLink(self, action):
        self.justValidate(action)
