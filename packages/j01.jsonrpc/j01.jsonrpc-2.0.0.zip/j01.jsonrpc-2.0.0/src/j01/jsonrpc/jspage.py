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

import zope.interface
from zope.traversing.browser import absoluteURL

from z3c.pagelet import browser
from z3c.jsonrpc.browser import JSONRPCTraversablePage
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate

from j01.jsonrpc import interfaces

REDIRECT_STATUS_CODES = (301, 302, 303)


class JSONRPCPage(JSONRPCTraversablePage, browser.BrowserPagelet):
    """JSON-RPC traversable pagelet.

    Note: this JSON-RPC pagelet is also usable as normal BrowserPagelet
    replacement. The pagelet only supports an additional traversal option.
    see: JSONRPCTraversablePage
    This traversal option should not be a problem since we need the permission
    to traverse the page first before we traverse to the JSON-RPC handler.
    """

    zope.interface.implements(interfaces.IJSONRPCPage)

    layout = getLayoutTemplate()
    template = getPageTemplate()

    _contextURL = None
    _pageURL = None

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
    def stateURL(self):
        """Browser history url

        Only use an url if the full page can get loaded within a browser request
        make sure that the page provides a layout within the browser request.
        Remember, a jsonrpc request will only call update/render and a browser
        request will call __call__/update/render. Only the __call__ method will
        include the layout template.
        """
        if not self.skipStateURL:
            return self.pageURL

    def render(self):
        if self.nextURL is not None:
            return None
        return self.template()

    def __call__(self):
        self.update()
        if self.nextURL is not None:
            self.request.response.redirect(self.nextURL)
            return u''
        return self.layout()
