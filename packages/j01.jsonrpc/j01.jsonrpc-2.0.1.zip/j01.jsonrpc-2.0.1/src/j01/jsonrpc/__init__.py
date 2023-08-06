##############################################################################
#
# Copyright (c) 2015 Projekt01 GmbH and Contributors.
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
$Id:$
"""
__docformat__ = "reStructuredText"


class HistoryStateMixin(object):
    """HTML5 history stae data mixin"""

    # option for skip browser history state
    skipState = False

    # history state title (not supported by all browser history implementations)
    stateTitle = ''

    # method for process state, by default we simply load the page content.
    # Note, by default the cbStateParams get used for calling this method
    # and if no cbStateParams get used they get extracted from the cbStateURL.
    # This means if there are any params, your method must accept the params
    # argument
    cbStateMethod = 'j01LoadContent'
    # optional params for cbStateMethod method, if None, the params get
    # extracted from the cbStateURL if any. Such cbStateParams must be json
    # seriazable
    cbStateParams = None
    # onSuccess callback used by state processing
    cbStateSuccess = 'j01RenderContentSuccess'
    # onError callback used by state processing
    cbStateError = 'j01RenderContentError'
    # onTimeout callback used by state processing
    cbStateTimeout = None

    @property
    def cbStateURL(self):
        """JSONRPC proxy url used for state processing

        NOTE: this url will force to load the content from the server via
        jsonrpc. By default the pageURL get used. If this cbStateURL is missing,
        the stateURL get used for load the page from the server using a non
        jsonrpc request. See stateURL description below for more information.
        """
        if not self.skipState:
            return self.pageURL

    @property
    def stateURL(self):
        """State URL (by default pageURL is used)

        This url is shown in browser navigation and also used for reload a page

        Note: this url will force to load the page with:

            window.location.href = url

        But only if the cbStateURL is not used. Because we first process a
        cbStateURL before we process the stateURL

        Note: Only use the stateURL url if the full page can get loaded within
        a browser request and make sure that the page provides a layout within
        the browser request. You can also use a totaly different url of  page
        which can get loaded including  layout if the page itself does not
        support a layout.

        Note: the stateURL is also shown in the browser navigation and will get
        use for navigation if the user clicks the browser relaod button e.g.
        ctrl/F5.

        Note; this url is also used if the user booksmarks a page.

        Remember, a jsonrpc request will only call update/render and a browser
        request will call __call__/update/render. Only the __call__ method will
        include the layout template.
        """
        if not self.skipState:
            return self.pageURL
