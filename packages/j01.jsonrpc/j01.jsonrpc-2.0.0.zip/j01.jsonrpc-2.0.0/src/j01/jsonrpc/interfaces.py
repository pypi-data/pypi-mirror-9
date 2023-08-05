##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
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
"""
$Id: __init__.py 6 2006-04-16 01:28:45Z roger.ineichen $
"""

import zope.schema
import zope.interface

import z3c.form.interfaces


###############################################################################
#
# action and handler concept

class IButtons(z3c.form.interfaces.IButtons):
    """Buttons."""

    def getInputEnterJavaScript(form, request):
        """Returns the input enter java script code if the inputEnterActionName
        name defines a button and the button condition is True.
        """


class IButtonHandlers(z3c.form.interfaces.IButtonHandlers):
    """A collection of handlers for buttons."""


class IButtonHandler(z3c.form.interfaces.IButtonHandler):
    """A handler managed by the button handlers."""

    def __call__(form, action):
        """Processes the action handler"""


class IActionHandler(z3c.form.interfaces.IActionHandler):

    def __call__():
        """Lookup and execute the action handler."""


###############################################################################
#
# action and widget

class IButtonWidget(z3c.form.interfaces.IButtonWidget):
    """Button widget."""


class IButtonAction(z3c.form.interfaces.IButtonAction):
    """Button Action."""

    javascript = zope.schema.Text(
        title=u'Javascript',
        description=(u'This attribute specifies the javascript part rendered '
                     u'directly after the button if given.'),
        default=None,
        required=False)

    data = zope.schema.Dict(
        title=u'Additional button data attributes',
        description=u'Additional button data attributes',
        default=None,
        required=False)


###############################################################################
#
# submit buttons

class IButton(z3c.form.interfaces.IButton):
    """Button using a string template and data attributes based on attrNames
    
    The default attribute names should be fine for mist button implementations.
    Set the template to None in your own button if you like to use a page
    template for rendering the button. The simple string template allows us to
    render additional data attributes which you can define with a data dict
    or a dataGetter method. 
    """

    css = zope.schema.Field(
        title=u'CSS class',
        description=u'CSS class',
        required=False)

    template = zope.schema.TextLine(
        title=u'Button string template',
        description=u'Button string template',
        default=None,
        required=False)

    attrNames = zope.schema.Field(
        title=u'Attribute names used for button element',
        description=u'Attribute names used for button element',
        default=['type', 'id', 'name', 'value', 'class', 'title', 'alt',
                 'tabindex'],
        required=True)

    data = zope.schema.Dict(
        title=u'Additional button data attributes',
        description=u'Additional button data attributes',
        default=None,
        required=False)

    dataGetter = zope.interface.Attribute("""Button data getter method""")

    def getInputEnterJavaScript(form, request):
        """Returns the input enter JavaScript code."""

    def getJavaScript(action, request):
        """Returns the javascript code."""

    def getData(action, request, data):
        """Returns the the optional data-loading value.
        
        This value can get used as loading message after button click and is
        only supported in javascript and jsonrpc (ajax)  buttons.
        """


###############################################################################
#
# javascript buttons


class IJSButton(IButton):
    """JS javascript aware button."""

    urlGetter = zope.interface.Attribute("""URL getter method""")


class IJSONRPCButton(IJSButton):
    """JSONRPC button"""

    css = zope.interface.Attribute("""css""")

    callback = zope.schema.ASCIILine(
        title=u'Callback function name as string',
        description=u'Callback function name as string',
        default='',
        required=False)

    loading = zope.schema.TextLine(
        title=u'Button loading text',
        description=u'Button loading text',
        default=None,
        required=False)

    def getURL(form):
        """Returns the url based on urlGetter or the form url"""


###############################################################################
#
# jsonrpc page

class IJSONRPCPage(zope.interface.Interface):
    """JSON-RPC page marker."""


###############################################################################
#
# jsonrpc form

class IJSONRPCForm(zope.interface.Interface):
    """JSON-RPC base form mixin class."""

    inputEnterActionName = zope.schema.TextLine(
        title=(u'Button name where the input enter JS code get used'),
        description=(u'Button name where the input enter JS code get used'),
        required=False)

    inputEnterJavaScript = zope.schema.Text(
        title=u'Input enter javascript code',
        description=(u'This attribute specifies the javascript part rendered '
                     u'for bind input to keypress enter handler'),
        required=True)

    refreshWidgets = zope.schema.Bool(
        title=u'Refresh widgets',
        description=(u'A flag, when set, causes form widgets to be updated '
                     u'again after action execution.'),
        default=False,
        required=True)


class IJSONRPCAddForm(IJSONRPCForm, z3c.form.interfaces.IAddForm):
    """JSON-RPC based add form."""


class IJSONRPCEditForm(IJSONRPCForm, z3c.form.interfaces.IEditForm):
    """JSON-RPC based edit form."""


class IJSONRPCSearchForm(IJSONRPCForm, z3c.form.interfaces.IForm):
    """JSON-RPC based search form."""
