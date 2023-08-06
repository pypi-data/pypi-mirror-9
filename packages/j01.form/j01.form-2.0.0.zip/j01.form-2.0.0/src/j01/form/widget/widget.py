###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Widget layout and setup
$Id: widget.py 3934 2014-03-17 07:38:52Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.i18n
import zope.interface
import zope.component
from zope.schema.fieldproperty import FieldProperty

import z3c.form.field
import z3c.form.widget
import z3c.form.interfaces

from j01.form import interfaces


class WidgetMixin(object):
    """Enhanced widget layout mixin class supporting widget addons"""

    # description and addon set by updateWidget in j01 forms
    description = FieldProperty(interfaces.IWidget['description'])
    addOnBefore = FieldProperty(interfaces.IWidget['addOnBefore'])
    addOnAfter = FieldProperty(interfaces.IWidget['addOnAfter'])
    addOnWrapper = FieldProperty(interfaces.IWidget['addOnWrapper'])

# XXX: same as z3c.form (but we use getCSSClass(classPattern='%(class)s-widget')
#    def wrapCSSClass(self, klass, pattern='%(class)s'):
#        """Return a list of css class names wrapped with given pattern"""
#        if klass is not None and pattern is not None:
#            return [pattern % {'class': k} for k in klass.split()]
#        else:
#            return []
#
#    def unifyCSSClasses(self, classes):
#        """Remove duplicated class names but keep order"""
#        unique = []
#        [unique.append(kls) for kls in classes if kls not in unique]
#        return unique
#
#      in layout templete
#    def getCSSClass(self, klass=None, error=None, required=None,
#        classPattern='%(class)s', errorPattern='%(class)s-error',
#        requiredPattern='%(class)s-required'):
#        """Setup given css class (klass) with error and required postfix
#
#        If no klass name is given the widget.wrapper class name/names get used.
#        It is also possible if more then one (empty space separated) names
#        are given as klass argument.
#
#        This method can get used from your form or widget template or widget
#        layout template without to re-implement the widget itself just because
#        you a different CSS class concept.
#
#        The following sample:
#
#        <div tal:attributes="class python:widget.getCSSClass('foo bar')">
#          label widget and error
#        </div>
#
#        will render a div tag if the widget field defines required=True:
#
#        <div class="foo-error bar-error foo-required bar-required foo bar">
#          label widget and error
#        </div>
#
#        And the following sample:
#
#        <div tal:attributes="class python:widget.getCSSClass('row')">
#          label widget and error
#        </div>
#
#        will render a div tag if the widget field defines required=True
#        and an error occurs:
#
#        <div class="row-error row-required row">
#          label widget and error
#        </div>
#
#        Note; you need to define a globale widget property if you use
#        python:widget (in your form template). And you need to use the
#        view scope in your widget or layout templates.
#
#        Note, you can set the pattern to None for skip error or required
#        rendering. Or you can use a pattern like 'error' or 'required' if
#        you like to skip postfixing your default css klass name for error or
#        required rendering.
#
#        """
#        classes = []
#        # setup class names
#        if klass is not None:
#            kls = klass
#        else:
#            kls = self.css
#
#        # setup error class names
#        if error is not None:
#            error = error
#        else:
#            error = kls
#
#        # setup required class names
#        if required is not None:
#            required = required
#        else:
#            required = kls
#
#        # append error class names
#        if self.error is not None:
#            classes += self.wrapCSSClass(error, errorPattern)
#        # append required class names
#        if self.required:
#            classes += self.wrapCSSClass(required, requiredPattern)
#        # append given class names
#        classes += self.wrapCSSClass(kls, classPattern)
#        unique = self.unifyCSSClasses(classes)
#        return ' '.join(unique)

    def render(self):
        """Render the plain widget without additional layout"""
        widget = super(WidgetMixin, self).render()
        classes = ['input-group']
        if self.addOnBefore is not None:
            widget = '%s\n%s' % (self.addOnBefore, widget)
            classes.append('input-group-before')
        if self.addOnAfter is not None:
            widget = '%s\n%s' % (widget, self.addOnAfter)
            classes.append('input-group-after')
        if self.addOnWrapper:
            # don't use if None or an empty string
            widget = self.addOnWrapper % {'widget': widget,
                                          'class': ' '.join(classes)}
        return widget
