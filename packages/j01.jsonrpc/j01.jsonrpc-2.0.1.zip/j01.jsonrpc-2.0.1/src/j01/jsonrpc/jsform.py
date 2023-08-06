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
__docformat__ = "reStructuredText"

import sys
import urllib

import zope.interface
import zope.component
import zope.i18nmessageid
from zope.traversing.browser import absoluteURL
from zope.publisher.interfaces import NotFound

import z3c.form.field
import z3c.form.form
from z3c.jsonrpc.interfaces import IMethodPublisher
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate

import j01.jsonrpc
from j01.jsonrpc import interfaces
from j01.jsonrpc import btn

_ = zope.i18nmessageid.MessageFactory('p01')


REDIRECT_STATUS_CODES = (301, 302, 303)


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


class JSONRPCFormMixin(j01.jsonrpc.HistoryStateMixin):
    """JSONRPC form mixin providing IJSONRPCForm

    Note: the IJSONRPCForm interfaces makes sure that a pagelet
    (content provider) adapter is available by default. This is usefull if you
    instanciate such classes without to lookup them as adapters registred
    with the pagelet directive.
    """

    zope.interface.implements(interfaces.IJSONRPCForm)

    template = getPageTemplate()
    layout = getLayoutTemplate()

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')

    # cached urls
    _contextURL = None
    _pageURL = None

    # override widget prefix if you need to load different forms using the same
    # field names in one single page.
    prefixWidgets = 'widgets'

    # override button prefix if you need to load different forms using the same
    # button in one single page.
    prefixButtons = 'buttons'

    # allows to skip action and widget processing. This is sometimes required
    # for JSON-RPC forms
    skipActions = False
    skipWidgets = False

    # allows to fetch a status message from an url set by redirect. Set this to
    # None or a different name if you don't like to support such status
    # messages e.g. foo.html?status=foobar. Note: such status message must
    # be urlencoded
    statusAttrName = 'status'

    # set this conditions in your action handler method if needed
    # widgets normaly not change their value
    refreshWidgets = False
    # action condition may have changed after action execution
    refreshActions = False

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
    # Note: we don't provide any javascript for hasbang since we fully support
    # the browser history api. Implement you own navigation concept if you
    # need it
    nextHash = None

    # url used for load content via j01LoadContent method
    nextContentURL = None

    buttons = btn.Buttons()
    handlers = btn.Handlers()

    def publishTraverse(self, request, name):
        view = zope.component.queryMultiAdapter((self, request), name=name)
        if view is None or not IMethodPublisher.providedBy(view):
            raise NotFound(self, name, request)
        return view

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

    def updateActions(self):
        if self.prefixButtons is not None:
            # overrride button prefix before update actions
            self.buttons.prefix = self.prefixButtons
        super(JSONRPCFormMixin, self).updateActions()

    def updateWidgets(self, prefix=None):
        if prefix is None and self.prefixWidgets is not None:
            prefix = self.prefixWidgets
        super(JSONRPCFormMixin, self).updateWidgets(prefix)

    def executeActions(self):
        """Dispatch actions.execute call"""
        self.actions.execute()

    def update(self):
        """Update form

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
            self.updateWidgets()

        if not self.skipActions:
            # default False
            self.updateActions()
            self.executeActions()

        if self.refreshActions:
            # default False
            self.updateActions()

        if self.refreshWidgets:
            # default False
            self.updateWidgets()

        if self.statusAttrName is not None:
            # get and set status given from url
            status = self.request.get(self.statusAttrName)
            if status:
                self.status = status

    def setNextURL(self, url, status):
        """Helper for set a nextURL including a status message

        Note: the status message must be an i18n message which will get
        translated later as status message.

        If you don't use a status message just use self.nextURL = myURL and
        don't use this method.

        """
        self.nextURL = '%s?%s' % (url, urllib.urlencode({'status':status}))

    def render(self):
        if self.nextURL is not None:
            return None
        return self.template()

    def __call__(self):
        # don't render on redirect
        if self.request.response.getStatus() in REDIRECT_STATUS_CODES:
            return u''
        self.update()
        if self.request.response.getStatus() in REDIRECT_STATUS_CODES:
            return u''
        # we only use the nextURL pattern and not the redirect status check
        # in our JSON-RPC method call. But this __call__ method get only used
        # if no JSON-RPC call is involved. So let's setup the redirect.
        if self.nextURL is not None:
            self.request.response.redirect(self.nextURL)
            return u''
        return self.layout()


class JSONRPCForm(JSONRPCFormMixin, z3c.form.form.Form):
    """JSONRPC form mixin."""

    buttons = btn.Buttons()


class JSONRPCEditForm(JSONRPCFormMixin, z3c.form.form.EditForm):
    """JSONRPC edit form."""

    zope.interface.implements(interfaces.IJSONRPCEditForm)

    showCancel = True
    buttons = btn.Buttons()

    def doHandleApplyChanges(self, action):
        # Note we, use the data from the request.form
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
        self.updateActions()
        self.updateWidgets()

    @btn.buttonAndHandler(btn.IJSONRPCButtons['applyChanges'])
    def handleApplyChanges(self, action):
        self.doHandleApplyChanges(action)

    @btn.buttonAndHandler(btn.IJSONRPCButtons['cancel'],
        condition=lambda form: form.showCancel)
    def handleCancel(self, action):
        self.doHandleCancel(action)


class JSONRPCAddForm(JSONRPCFormMixin, z3c.form.form.AddForm):
    """JSONRPC add form."""

    zope.interface.implements(interfaces.IJSONRPCAddForm)

    showCancel = True
    buttons = btn.Buttons()

    def doHandleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    def doHandleCancel(self, data):
        self.ignoreRequest = True
        self.updateActions()
        self.updateWidgets()

    @btn.buttonAndHandler(btn.IJSONRPCButtons['add'])
    def handleAdd(self, action):
        self.doHandleAdd(action)

    @btn.buttonAndHandler(btn.IJSONRPCButtons['cancel'],
        condition=lambda form: form.showCancel)
    def handleCancel(self, action):
        self.doHandleCancel(action)

    def renderAfterAdd(self):
        return super(JSONRPCAddForm, self).render()

    def render(self):
        if self._finishedAdd:
            return self.renderAfterAdd()
        return super(JSONRPCAddForm, self).render()


class JSONRPCSearchForm(JSONRPCFormMixin, z3c.form.form.Form):
    """JSONRPC search form."""

    zope.interface.implements(interfaces.IJSONRPCSearchForm)

    buttons = btn.Buttons()
    inputEnterActionName = 'search'

    def doHandleSearch(self, action):
        raise NotImplementedError('Subclass must implement doHandleSearch')

    @btn.buttonAndHandler(btn.IJSONRPCButtons['search'])
    def handleSearch(self, action):
        self.doHandleSearch(action)
