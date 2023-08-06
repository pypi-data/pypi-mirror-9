###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""File upload widget
$Id: file.py 3934 2014-03-17 07:38:52Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
import zope.schema.interfaces

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.file

from j01.form import interfaces
from j01.form.layer import IFormLayer
from j01.form.widget.widget import WidgetMixin


class FileWidget(WidgetMixin, z3c.form.browser.file.FileWidget):
    """Input type text widget implementation."""

    zope.interface.implementsOnly(interfaces.IFileWidget)

    klass = u'file-control form-control'
    css = u'file'

    # Filename and headers attribute get set by ``IDataConverter`` to the widget
    # provided by the FileUpload object of the form.
    headers = None
    filename = None


# get
@zope.component.adapter(zope.schema.interfaces.IBytes, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getFileWidget(field, request):
    """IFieldWidget factory for IPasswordWidget."""
    return z3c.form.widget.FieldWidget(field, FileWidget(request))
