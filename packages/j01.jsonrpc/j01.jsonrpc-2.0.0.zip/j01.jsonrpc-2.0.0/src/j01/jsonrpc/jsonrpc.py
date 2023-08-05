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
__docformat__ = 'restructuredtext'

from z3c.jsonrpc.publisher import MethodPublisher


class J01LoadContent(MethodPublisher):
    """Can load content via JSONRPC.

    Note: This method publisher must be able to traverse the context which is
    a view or a form. Our default JSON-RPC tarverser could be used.
    See: JSONRPCTraversablePage

    Note: This method is registered with zope.Public permission and will run
    into Unauthorized if the principal does not have the permission to traverse
    the view.

    This method supports the browser history api and includes fallbacks if the
    browser doesnt support the history api.

    Note: it's important that you only provide a stateURL for pages which are
    available as standalone page. Never provide an url if you only load
    partial page content and the page is can't get loaded with a non JSONRPC
    request.

    """

    def j01LoadContent(self):
        self.context.update()
        pageURL = self.context.pageURL
        nextURL = self.context.nextURL
        nextContentURL = self.context.nextContentURL
        if nextURL is not None:
            # load next page with location.href redirect
            content = None
            stateURL = None
            stateTitle = None
            stateCallbackName = None
        elif nextContentURL is not None:
            # load next content with jsonrpc
            content = None
            stateURL = None
            stateTitle = None
            stateCallbackName = None
            nextURL = ''
        else:
            content = self.context.render()
            stateURL = self.context.stateURL
            stateTitle = self.context.stateTitle
            stateCallbackName = self.context.stateCallbackName
            nextURL = ''
        # setup target expression at the end, could probably get adjusted
        # in the render method call
        targetExpression = self.context.contentTargetExpression
        skipState = self.context.skipState
        nextHash = self.context.nextHash
        return {'url': pageURL,
                'content': content,
                'contentTargetExpression': targetExpression,
                # animation
                'scrollToExpression': self.context.scrollToExpression,
                'scrollToOffset': self.context.scrollToOffset,
                'scrollToSpeed': self.context.scrollToSpeed,
                # history setup
                'skipState': skipState,
                'stateURL': stateURL,
                'stateTitle': stateTitle,
                'stateCallbackName': stateCallbackName,
                # load next page with location.href redirect
                'nextURL': nextURL,
                # load next content with jsonrpc
                'nextContentURL': nextContentURL,
                # next hash for custom navitation concepts
                'nextHash': self.context.nextHash,
                }


class J01FormProcessor(MethodPublisher):
    """Can process a form button handler via JSONRPC.

    Note: This method publisher must be able to traverse the context which is
    a view or a form. Our default JSON-RPC tarverser could be used.
    See: JSONRPCTraversablePage

    Note: This method is registered with zope.Public permission and will run
    into Unauthorized if the principal does not have the permission to traverse
    the view.
    """

    def j01FormProcessor(self):
        # self.context.update()
        # nextURL = self.context.nextURL
        # if nextURL is None:
        #     # redirect, no history state
        #     content = self.context.render()
        #     stateTitle = self.context.stateTitle
        #     stateURL = self.context.stateURL
        #     nextURL = ''
        # else:
        #     content = None
        #     stateTitle = None
        #     stateURL = None
        # # setup target expression at the end, could probably get adjusted
        # # in update or render method call
        # targetExpression = self.context.contentTargetExpression
        # scrollToExpression = self.context.scrollToExpression
        # scrollToOffset = self.context.scrollToOffset
        # scrollToSpeed = self.context.scrollToSpeed
        # nextHash = self.context.nextHash
        # return {'content': content,
        #         'contentTargetExpression': targetExpression,
        #         'scrollToExpression': scrollToExpression,
        #         'scrollToOffset': scrollToOffset,
        #         'scrollToSpeed': scrollToSpeed,
        #         'nextHash': '%s' % nextHash,
        #         'nextURL': '%s' % nextURL,
        #         'stateURL': stateURL,
        #         'stateTitle': stateTitle,
        #         }
        self.context.update()
        pageURL = self.context.pageURL
        nextURL = self.context.nextURL
        nextContentURL = self.context.nextContentURL
        if nextURL is not None:
            # load next page with location.href redirect
            content = None
            stateURL = None
            stateTitle = None
            stateCallbackName = None
        elif nextContentURL is not None:
            # load next content with jsonrpc
            content = None
            stateURL = None
            stateTitle = None
            stateCallbackName = None
            nextURL = ''
        else:
            content = self.context.render()
            stateURL = self.context.stateURL
            stateTitle = self.context.stateTitle
            stateCallbackName = self.context.stateCallbackName
            nextURL = ''
        # setup target expression at the end, could probably get adjusted
        # in the render method call
        targetExpression = self.context.contentTargetExpression
        skipState = self.context.skipState
        nextHash = self.context.nextHash
        return {'url': pageURL,
                'content': content,
                'contentTargetExpression': targetExpression,
                # animation
                'scrollToExpression': self.context.scrollToExpression,
                'scrollToOffset': self.context.scrollToOffset,
                'scrollToSpeed': self.context.scrollToSpeed,
                # history setup
                'skipState': skipState,
                'stateURL': stateURL,
                'stateTitle': stateTitle,
                'stateCallbackName': stateCallbackName,
                # load next page with location.href redirect
                'nextURL': nextURL,
                # load next content with jsonrpc
                'nextContentURL': nextContentURL,
                # next hash for custom navitation concepts
                'nextHash': self.context.nextHash,
                }
