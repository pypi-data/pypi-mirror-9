##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id:$
"""

import zope.interface
import zope.component
import zope.i18nmessageid
from zope.site import hooks
from zope.traversing.browser.absoluteurl import absoluteURL


import z3c.jsonrpc.error
from z3c.jsonrpc.interfaces import IJSONRPCRequest
from z3c.form.interfaces import IValue
from z3c.form.interfaces import IErrorViewSnippet

_ = zope.i18nmessageid.MessageFactory('p01')


class Unauthorized(z3c.jsonrpc.error.JSONRPCErrorView):
    """Unauthorized error view which returns response.data.nextURL.
    
    The response can get handled by our j01.jsonrpc.js library and redirects to
    the given nextURL e.g. <site>/j01Login.html page. 

    This is probably not the best concept because we will loose the
    original page and what the user was trying to do. But it's probably not
    possible to traverse to the jsonrpc method because of unauthorized.
    This seems to be the only solution whcih is working for any project. But
    feel free to implement a custom concept for you own project if you like
    to provide a better user experience.

    Note: the j01Login.html page is a simple browser page probably the same as
    your existing login page and not a jsonrpc method.

    Note: use your own Unauthorized error view if you don't like to redirect to
    the <site>/j01Login.html page.
    
    Since this unauthorized error handling concept doesn't know about the
    javascript library used on the client side you have to make sure that
    the given error response (response.data.nextURL) can get handled by the
    client side javascript. The j01.jsonrpc.js javascript used by this package
    supports this error handling. But make sure that your own custom javascript
    can handle such a response or replace this error view with oru own custom
    error response.
    """

    code = -32000
    message = u'Unauthorized'

    @property
    def data(self):
        # setup a redirect url
        site = hooks.getSite()
        nextURL = '%s/j01Login.html' % absoluteURL(site, self.request)
        return {'nextURL': nextURL}

    def __call__(self):
        """Must return itself.
        
        This allows us to use the error view in setResult if ZopePublication
        is adapting an error view to error and request and calls them.
        """
        # do not call unauthorized, it's useless since it will only setup a
        # redirect. JSON-RPC doens't provide such a redirect
        self.request.response.self.setStatus(401)
        return self


# z3c.form IErrorViewSnippet
class JSONErrorViewSnippet(object):
    """Error view snippet."""
    zope.component.adapts(zope.schema.ValidationError, None, IJSONRPCRequest, 
        None, None, None)
    zope.interface.implements(IErrorViewSnippet)

    def __init__(self, error, request, widget, field, form, content):
        self.error = self.context = error
        self.request = request
        self.widget = widget
        self.field = field
        self.form = form
        self.content = content

    def update(self):
        value = zope.component.queryMultiAdapter(
            (self.context, self.request, self.widget,
             self.field, self.form, self),
            IValue, name='message')
        if value is not None:
            self.message = value.get()
        else:
            self.message = self.error.doc()

    def render(self):
        return self.message

    def __repr__(self):
        return '<%s for %s>' %(
            self.__class__.__name__, self.error.__class__.__name__)


class JSONValueErrorViewSnippet(JSONErrorViewSnippet):
    """An error view for ValueError raised by widget validation."""
    zope.component.adapts(ValueError, None, IJSONRPCRequest, None, None, None)
    
    @property
    def message(self):
        errMsg = _(u"The system could not process the given value.")
        return zope.i18n.translate(errMsg, context=self.request)

    def update(self):
        value = zope.component.queryMultiAdapter(
            (self.context, self.request, self.widget,
             self.field, self.form, self),
            IValue, name='message')
        if value is not None:
            self.message = value.get()

    def render(self):
        return self.message
