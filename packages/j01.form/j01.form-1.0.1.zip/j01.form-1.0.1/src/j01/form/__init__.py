###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Widgt mixin classes shared in form and jsform

$Id:$
"""
__docformat__ = "reStructuredText"

import urllib

import zope.interface
import zope.schema.interfaces
import zope.i18nmessageid
import zope.event
import zope.lifecycleevent
from zope.publisher.interfaces import NotFound
from zope.traversing.browser import absoluteURL

import z3c.form.error
import z3c.form.interfaces
from z3c.jsonrpc.interfaces import IMethodPublisher
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate

from j01.form import interfaces
from j01.form import btn

_ = zope.i18nmessageid.MessageFactory('p01')

REDIRECT_STATUS_CODES = (301, 302, 303)


###############################################################################
#
# enhanced form mixin class

class FormMixin(object):
    """Form widgets mixin class"""

    template = getPageTemplate()
    layout = getLayoutTemplate()

    # simplified button and action handler concept (supports jsonrpc too!)
    buttons = btn.Buttons()
    handlers = btn.Handlers()

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')

    # cached urls
    _contextURL = None
    # action/page ur
    _pageURL = None
    # next url
    nextURL = None
    # support download (direct) results
    directResult = None

    # default values used by IValue(name='default') adapter
    defaultValues = None

    # allows to skip action and widget processing. This is sometimes required
    # for JSON-RPC forms
    skipActions = False
    skipWidgets = False

    # set this conditions in your action handler method if needed
    refreshWidgets = False
    # action condition may have changed after action execution
    refreshActions = False

    # override button prefix if you need to load different forms using the same
    # button in one single page.
    btnPrefix = 'buttons'

    # override widget prefix if you need to load different forms using the same
    # field names in one single page.
    widgetPrefix = 'widgets'

    # widget factories
    widgetFactories = {}

    # widget labels
    widgetLabels = {}

    # widget titles
    widgetTitles = {}

    # widget descriptions
    widgetDescriptions = {}

    # required widgets
    widgetRequireds = {}

    # ignore required on extracts
    widgetIgnoreRequiredOnExtracts = {}

    # ignoreContext widgets
    widgetIgnoreContexts = {}

    # ignoreContext widgets
    widgetIgnoreRequests = {}

    # widget modes
    widgetModes = {}

    # widget layout
    widgetInputLayoutName = z3c.form.interfaces.INPUT_MODE
    widgetDisplayLayoutName = z3c.form.interfaces.DISPLAY_MODE
    widgetHiddenLayoutName = z3c.form.interfaces.HIDDEN_MODE
    widgetInputLayoutNames = {}
    widgetDisplayLayoutNames = {}
    widgetHiddenLayoutNames = {}

    # widget placeholders
    widgetPlaceholders = {}

    # addons
    widgetAddOnWrapperDefault = unicode(
        '<div class="%(class)s">%(widget)s</div>')
    widgetAddOnWrappers = {}
    widgetBeforeAddOns = {}
    widgetAfterAddOns = {}

    # widget patterns
    widgetPatterns = {}

    # tab indexes
    tabIndexes = {}

    # set this conditions in your action handler method if needed
    # widgets normaly not change their value
    refreshWidgets = False
    # action condition may have changed after action execution
    refreshActions = False

    @property
    def name(self):
        """Never use an empty name if prefix is an empty string"""
        return self.prefix.strip('.') or 'form'

    @property
    def action(self):
        """Take care on action url."""
        return self.pageURL

    @property
    def contextURL(self):
        """Setup and cache context URL"""
        if self._contextURL is None:
            self._contextURL = absoluteURL(self.context, self.request)
        return self._contextURL

    @property
    def pageURL(self):
        """Setup and cache context URL"""
        if self._pageURL is None:
            self._pageURL = '%s/%s' % (absoluteURL(self.context, self.request),
                self.__name__)
        return self._pageURL

    def setUpWidgetFields(self):
        """Setup additional/conditional widget fields"""
        pass

    def applyIgnoreContext(self):
        """Apply ignore context marker"""
        for name, state in self.widgetIgnoreContexts.items():
            try:
                self.fields[name].ignoreContext = state
            except KeyError:
                pass

    def applyWidgetFactories(self):
        """Apply widget factories"""
        for name, factory in self.widgetFactories.items():
            try:
                self.fields[name].widgetFactory = factory
            except KeyError:
                pass

    def applyDefaultValues(self):
        """Apply default widget values

        Put those default values into self.defaultValues.

        NOTE: With z3c.form it's a NOGO, to just assign widget.value after
        update because some widgets need updating after that and the update
        gets a new value. The right way is to use an IValue(name='default')
        adapter and let widget.update() get the default value.
        """
        pass

    def applyIgnoreRequest(self):
        """Apply ignore context marker"""
        for name, state in self.widgetIgnoreRequests.items():
            try:
                self.widgets[name].ignoreRequests = state
            except KeyError:
                pass

    def applyWidgetLabels(self):
        """Apply widget labels"""
        for name, label in self.widgetLabels.items():
            try:
                self.widgets[name].label = label
            except KeyError:
                pass

    def applyWidgetTitles(self):
        """Apply widget titles"""
        for name, title in self.widgetTitles.items():
            try:
                self.widgets[name].title = title
            except KeyError:
                pass

    def applyWidgetDescriptions(self):
        """Apply widget descriptions"""
        for name, description in self.widgetDescriptions.items():
            try:
                widget = self.widgets[name]
                if description is True:
                    # use field description if value is True
                    description = widget.field.description
                widget.description = description
            except KeyError:
                pass

    def applyWidgetsRequireds(self):
        """Apply widget required"""
        # override required
        for name, required in self.widgetRequireds.items():
            try:
                self.widgets[name].required = required
            except KeyError:
                pass

    def applyIgnoreRequiredOnExtract(self):
        """Apply ignore context marker"""
        for name, state in self.widgetIgnoreRequiredOnExtracts.items():
            try:
                self.widgets[name].ignoreRequiredOnExtract = state
            except KeyError:
                pass

    def applyWidgetsModes(self):
        """Apply widget mode"""
        for name, mode in self.widgetModes.items():
            try:
                self.widgets[name].mode = mode
            except KeyError:
                pass

    def applyWidgetsPlaceholders(self):
        """Apply widget patterns"""
        for name, placeholder in self.widgetPlaceholders.items():
            try:
                self.widgets[name].placeholder = placeholder
            except KeyError:
                pass

    def applyWidgetPatterns(self):
        """Apply widget patterns"""
        for name, pattern in self.widgetPatterns.items():
            try:
                self.widgets[name].pattern = pattern
            except KeyError:
                pass

    def applyWidgetAddOns(self):
        """Apply widget addon before widget"""
        for name, content in self.widgetAddOnWrappers.items():
            try:
                self.widgets[name].addOnWrapper = content
            except KeyError:
                pass
        for name, content in self.widgetBeforeAddOns.items():
            try:
                self.widgets[name].addOnBefore = content
                if self.widgets[name].addOnWrapper is None:
                    self.widgets[name].addOnWrapper = \
                        self.widgetAddOnWrapperDefault
            except KeyError:
                pass
        for name, content in self.widgetAfterAddOns.items():
            try:
                self.widgets[name].addOnAfter = content
                if self.widgets[name].addOnWrapper is None:
                    self.widgets[name].addOnWrapper = \
                        self.widgetAddOnWrapperDefault
            except KeyError:
                pass

    def applyTabIndexes(self):
        """Apply tab indexes"""
        for name, idx in self.tabIndexes.items():
            try:
                self.widgets[name].tabindex = idx
            except KeyError:
                pass

    def applyWidgetLayouts(self):
        """Apply widget layout templates"""
        for widget in self.widgets.items():
            if widget.mode == z3c.form.interfaces.INPUT_MODE:
                name = self.widgetInputLayoutNames.get(widget.__name__)
                if name is None:
                    name = self.widgetInputLayoutName
            elif widget.mode == z3c.form.interfaces.DISPLAY_MODE:
                name = self.widgetDisplayLayoutName.get(widget.__name__)
                if name is None:
                    name = self.widgetDisplayLayoutName
            elif widget.mode == z3c.form.interfaces.HIDDEN_MODE:
                name = self.widgetHiddenLayoutNames.get(widget.__name__)
                if name is None:
                    name = self.widgetHiddenLayoutName
            else:
                raise ValueError("Unknown widget mode given", widget.mode)
            layout = zope.component.queryMultiAdapter(
                (self.context, self.request, self, widget.field, widget),
                z3c.form.interfaces.IWidgetLayoutTemplate, name=name)
            if layout is not None:
                widget.layout = layout

    def setUpActions(self):
        """Allows to override setUpActions and re-use super updateActions"""
        if self.btnPrefix is not None:
            # overrride button prefix before update actions
            self.buttons.prefix = self.btnPrefix
        super(FormMixin, self).updateActions()

    def setUpWidgets(self, prefix=None):
        """Allows to override setUpWidgets and re-use updateWidgets"""
        prefix = prefix and prefix or self.widgetPrefix
        self.setUpWidgetFields()
        self.applyIgnoreContext()
        self.applyWidgetFactories()
        self.applyDefaultValues()
        self.updateWidgets(prefix)
        self.applyIgnoreRequest()
        self.applyWidgetLabels()
        self.applyWidgetTitles()
        self.applyWidgetDescriptions()
        self.applyWidgetsRequireds()
        self.applyIgnoreRequiredOnExtract()
        self.applyWidgetsModes()
        self.applyWidgetsPlaceholders()
        self.applyWidgetPatterns()
        self.applyWidgetAddOns()
        self.applyTabIndexes()

    def setUpWidgetValidation(self, name):
        """Support for single widget ssetup used by j01.validate"""
        # by default we simply setup al widgets. Customize this method in your
        # own form and only setup the relevant widget
        self.setUpWidgets()

    def setUpErrorViewSnippet(self, field, error, errors, setErrors=True):
        """Widget error setup helper method"""
        if isinstance(error, basestring):
            error = zope.interface.Invalid(error)
        err = zope.component.getMultiAdapter((
            error, self.request,
            self.widgets[field],
            self.widgets[field].field,
            self, self.getContent()), z3c.form.interfaces.IErrorViewSnippet)
        err.update()
        self.widgets[field].error = err
        errors += (err,)
        if setErrors:
            self.widgets.errors = errors
        return errors

    def extractData(self, setErrors=True):
        # extract data
        data, errors = super(FormMixin, self).extractData(setErrors)
        # validate additional required fields
        for name, required in self.widgetRequireds.items():
            try:
                w = self.widgets[name]
            except KeyError:
                pass
            else:
                if required and not data.get(name):
                    error = zope.schema.interfaces.RequiredMissing(name)
                    errors = self.setUpErrorViewSnippet(name, error, errors,
                        setErrors=setErrors)
        return data, errors

    def executeActions(self):
        """Dispatch actions.execute call"""
        self.actions.execute()

    def update(self):
        """Update form

        The update process supports setUpActions and setUpWidgets instead of
        updateActions and updateWidgets. This allows us to override the
        action and widget setup methods and re-use the original super
        classes.

        The default z3c.form calles the following methods in update:

        self.updateWidgets()
        self.updateActions()
        self.actions.execute()
        if self.refreshActions:
            self.updateActions()

        We implemented the following coditions:

        - skipWidgets
        - skipActions
        - refreshActions (also supported by z3c.form)
        - refreshWidgets

        This allows us to prepare the JSONRPC call setup and gives more
        controll for complex form setup. Also see J01FormProcessor in
        j01/jsform/jsonrpc.py

        """
        if not self.skipWidgets:
            # default False
            self.setUpWidgets()

        if not self.skipActions:
            # default False
            self.setUpActions()
            self.executeActions()

        if self.refreshActions:
            # default False
            self.setUpActions()

        if self.refreshWidgets:
            # default False
            self.setUpWidgets()

    def render(self):
        if self.nextURL is not None:
            return None
        return self.template()

    def __call__(self):
        self.update()
        if self.directResult is not None:
            # support returning csv and pdf results
            return self.directResult
        elif self.nextURL is not None:
            # use nextURL for redirect
            self.request.response.redirect(self.nextURL)
            return u''
        elif self.request.response.getStatus() in REDIRECT_STATUS_CODES:
            # don't render on redirect
            return u''
        else:
            # default rendering
            return self.layout()


class AddFormMixin(FormMixin):
    """Add form mixin class"""

    def createAndAdd(self, data):
        obj = self.create(data)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        # HEADSUP: The add method could return None if something fails. This
        # will implicit prevent to apply self._finishedAdd in doHandleAdd method
        return self.add(obj)

    def doHandleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # HEADSUP: mark only as finished if we get the new object
            self._finishedAdd = True
        return obj

    def doHandleCancel(self, action):
        self.ignoreRequest = True
        self.refreshActions = True
        self.refreshWidgets = True

    def renderAfterAdd(self):
        return self.template()

    def render(self):
        if self._finishedAdd:
            return self.renderAfterAdd()
        return super(AddFormMixin, self).render()


class EditFormMixin(FormMixin):
    """Edit form mixin class"""

    def doHandleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage
        return changes

    def doHandleCancel(self, action):
        self.ignoreRequest = True
        self.refreshActions = True
        self.refreshWidgets = True


class JSONRPCMixin(object):
    """JSONRPC form mixin class providing traversal concept

    Note: the IJSONRPCForm interfaces makes sure that a pagelet
    (content provider) adapter is available by default. This is usefull if you
    instanciate such classes without to lookup them as adapters registred
    with the pagelet directive.
    """

    inputEnterActionName = None # see inputEnterJavaScript

    # JSON-RPC javascript callback arguments
    # content target expression where the result get rendered in. By default
    # the built-in argument ``#content`` get used
    contentTargetExpression = None

    # optional scrollTo expression where the callback method will scroll to
    # after rendering. The default implementation uses offset().top. Feel free
    # to implement a custom j01CallbackRegistry method which uses another
    # concept instead of add more callback arguments
    scrollToExpression = None
    scrollToOffset = None
    scrollToSpeed = None

    # the next URL where the jsonrpc callback method will redirect to using
    # window.location.href = response.nextURL
    nextURL = None
    # the nextHash will update the url witout to redirect
    nextHash = None

    # url used for load content via j01LoadContent method
    nextContentURL = None

    # browser history support
    # skip brwoser history state marker. Note: we allways apply a browser
    # history state if this is not True, even if we don't provide a stateTitle,
    # stateURL or stateCallbackName
    skipState = False
    # disable browser history url if page only provides partial content
    # Note: we use the pageURL as default stateURL, see stateURL method below
    skipStateURL = False
    # history state title (not supported by all browser history implementations)
    stateTitle = None
    # browser history callback name for load content based on history state
    stateCallbackName = 'j01RenderContent'

    def publishTraverse(self, request, name):
        """Allows jsonrpc method traversing"""
        view = zope.component.queryMultiAdapter((self, request), name=name)
        if view is None or not IMethodPublisher.providedBy(view):
            raise NotFound(self, name, request)
        return view

    @property
    def inputEnterJavaScript(self):
        """Enter button click handler.

        You can define an action handler name which get called on enter button
        call in your form like:

        inputEnterActionName = 'myHandlerName'

        Note: you need to include the inputEnter javascript in your template
        within:

        <script type="text/javascript"
                tal:content="view/inputEnterJavaScript">
        </script>
        """
        return self.buttons.getInputEnterJavaScript(self, self.request)


    def setNextURL(self, url, status):
        """Helper for set a nextURL including a status message

        Note: the status message must be an i18n message which will get
        translated later as status message.

        If you don't use a status message just use self.nextURL = myURL and
        don't use this method.

        """
        self.nextURL = '%s?%s' % (url, urllib.urlencode({'status':status}))

    @property
    def stateURL(self):
        """Browser history url

        Only use an url if the full page can get loaded within a browser request
        make sure that the page provides a layout within the browser request.
        Remember, a jsonrpc request will only call update/render and a browser
        request will call __call__/update/render. Only the __call__ method will
        include the layout template.
        """
        if not self.skipState and not self.skipStateURL:
            # only used if state and state url are not marked as skipped
            return self.pageURL


###############################################################################
#
# defaultValues adapter

class DefaultValueProvider(object):
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


@zope.interface.implementer(z3c.form.interfaces.IValue)
@zope.component.adapter(zope.interface.Interface, zope.interface.Interface,
    interfaces.IForm, zope.schema.interfaces.IField,
    z3c.form.interfaces.IWidget)
def defaultValueProvider(context, request, form, field, widget):
    """return a default value for a field"""
    if form.defaultValues is None:
        return None

    name1 = widget.name
    try:
        v = form.defaultValues[name1]
    except KeyError:
        name2 = name1.split('.')[-1]
        try:
            v = form.defaultValues[name2]
        except KeyError:
            return None

    return DefaultValueProvider(v)
