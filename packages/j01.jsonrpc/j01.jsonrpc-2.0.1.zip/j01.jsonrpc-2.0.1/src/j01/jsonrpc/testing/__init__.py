##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Common z3c.form test setups

$Id: __init__.py 4209 2015-03-17 14:05:50Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import os
import json
import doctest
import urlparse

import bs4

import zope.component
import zope.interface
import zope.schema
import zope.location.interfaces
import zope.traversing.testing
import zope.traversing.browser
import zope.traversing.browser.interfaces
import zope.publisher.interfaces.http
from zope.pagetemplate.interfaces import IPageTemplate
from zope.password.interfaces import IPasswordManager
from zope.password.password import PlainTextPasswordManager
from zope.publisher.browser import TestRequest

#import zope.app.testing.testbrowser
from zope.app.testing import functional

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.field
import z3c.form.browser
import z3c.jsonrpc.testing
import z3c.macro.tales
import z3c.template.template
from z3c.template.interfaces import IContentTemplate

import j01.jsonrpc
from j01.jsonrpc import interfaces
from j01.jsonrpc import btn


###############################################################################
#
# jsonrpc testing helper
#
# NOTE: this methods require a p01.testbrowser or zope.testbrowser > 5.0.0
# browser instance providing the wsgi application as browser.testapp
#
###############################################################################

# exceptions
class JSONRPCResponseProssessingError(Exception):
    """JSONRPC repsonse processing error"""

class JSONRPCResponseError(Exception):
    """JSONRPC response error"""


def getJSONRPCResponse(browser):
    try:
        # get json response data from browser instance
        data = browser.json()
        if data is None:
            # raise server response error
            raise JSONRPCResponseError('Missing json repsonse data')
        elif data is not None and data.get('error') is not None:
            # raise server response error
            raise JSONRPCResponseError(data.get('error'))
        else:
            return data
    except:
        raise JSONRPCResponseProssessingError(browser.body)


def getJSONRPCResult(browser):
    data = getJSONRPCResponse(browser)
    return data['result']


def getJSONRPCContent(browser):
    data = getJSONRPCResponse(browser)
    return data['result']['content']


def getJSONRPCNextURL(browser):
    data = getJSONRPCResponse(browser)
    return str(data['result']['nextURL'])


def doJSONRPCResponse(browser):
    """Process jsonrpc server response"""
    data = getJSONRPCResult(browser)
    if isinstance(data, basestring):
        return data
    if data.get('nextURL') is not None:
        # process nextURL
        nextURL = data['nextURL']
        browser.open(nextURL)
    elif data.get('nextContentURL') is not None:
        # load content from nextURL
        nextContentURL = data['nextContentURL']
        return j01LoadContent(browser, nextContentURL)
    elif data.get('content') is not None:
        content = data['content']
        if data.get('contentTargetExpression') is not None:
            # inject content into target
            contentTargetExpression = data['contentTargetExpression']
            browser.doInjectContent(contentTargetExpression, content)
            return browser.contents
        else:
            # return plain content if no target expression is given
            return content
    else:
        # return result if no nextURL or content is given. This must be
        # something we don't support in our j01.jsonrpc implementation
        return data


def getBrowserURL(browser):
    """Get the browswer url"""
    url = browser.url
    r = list(urlparse.urlparse(url))
    r[0] = ''
    r[1] = ''
    r[4] = ''
    return urlparse.urlunparse(r)


def getBrowserHost(browser):
    """Get the browswer url"""
    url = browser.url
    if url is not None:
        return urlparse.urlparse(url).netloc


def doJSONRPCRequest(browser, url=None, method=None, params=None, button=None,
    headers=None, data=None, retJSON=False, retBody=False, retResponse=False,
    retResult=False, retContent=False, retNextURL=False, applyResponse=True):
    """WSGI application based jsonrpc call handling

    The browser instance must be a p01.testbrowser Browser instance.

    The jsonrpc server returns the following repsonse:

    version 1.0:
        return {
            'result': result,
            'error': None,
            'id': 'id'
            }

    version 1.1:
        return {
            'version': '1.1',
            'result': result,
            'id': 'id'
            }

    version 2.0:
        return {
            'jsonrpc': '2.0',
            'result': result,
            'id': 'id'
            }

    Or the jsonrpc server returns the following error response:

    version 1.0:
        return {
            'result': None,
            'error': message,
            'id': 'id'
            }

    version 1.1:
        return {
            'version': '1.1',
            'error': message,
            'id': 'id'
            }
    version 2.0:
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': code,
                'message': message,
                'data': data
                },
           'id': 'id'
           }
    """
    if url is None:
        url = getBrowserURL(browser)

    if params is None:
        params = {}
    if button is not None:
        params["j01FormHandlerName"] = button

    # # apply form values
    # if button == 'comInvited':
    #     import pdb;pdb.set_trace()

    if data is None:
        data = {
            "jsonrpc": "2.0",
            "id": "j01.jsonrpc.testing",
            "method": None,
            "params": {},
            }

    # apply/override method
    if method is not None:
        data['method'] = method

    # apply/override params
    for k, v in params.items():
        data['params'][k] = v

    # process request
    body = json.dumps(data)
    __traceback_info__ = (url, headers)
    browser._req_content_type = 'application/json-rpc'
    browser.request('POST', url, data=body.encode('utf8'), headers=headers)

    # prepare result before process response. If you need the result from a
    # processed response, just get them from the browser instance after
    # processing as we do here
    if retBody:
        # return current response.body
        res = browser.body
    elif retJSON:
        # return current response.json
        res = browser.json()
    elif retResponse:
        # return jsonrpc response as json data
        res = getJSONRPCResponse(browser)
    elif retResult:
        # return result data
        res = getJSONRPCResult(browser)
    elif retContent:
        # return content data
        res = getJSONRPCContent(browser)
    elif retNextURL:
        # return nextURL
        res = getJSONRPCNextURL(browser)
    else:
        res = None

    # process response
    # this could force another request if nextURL is given and means,
    # that the current response is not from related to the initial
    # jsonrpc request
    if applyResponse is True:
        # marked for processing
        doJSONRPCResponse(browser)
    elif applyResponse is not None:
        # applyResponse must be a callable if not True or None, just use them
        # for processing
        applyResponse(browser)

    # return the result from the initial jsonrpc response if asked for
    return res


# j01.dialog jsonrpc helper methods
def j01Dialog(browser, url=None, **kwargs):
    method = "j01Dialog"
    return doJSONRPCRequest(browser, url=url, method=method, **kwargs)


def j01DialogContent(browser, url=None, **kwargs):
    method = "j01DialogContent"
    return doJSONRPCRequest(browser, url=url, method=method, **kwargs)


def j01DialogFormProcessor(browser, url=None, **kwargs):
    method = "j01DialogFormProcessor"
    return doJSONRPCRequest(browser, url=url, method=method, **kwargs)


# j01.jsonrpc jsonrpc helper methods
def j01LoadContent(browser, url=None, **kwargs):
    method = "j01LoadContent"
    return doJSONRPCRequest(browser, url=url, method=method, **kwargs)


def j01FormProcessor(browser, url=None, **kwargs):
    """Form processing method

    By default this method will process the given jsonrpc server response as
    the related j01.jsonrpc javacsript library does. If you use different
    jsonrpc response handler methods you probably ned to implement your own
    repsonse processing methods. If so, just skip prost processing by using
    retRaw=True and use the returned browser content or the browser instance
    which contains the respsonse in browser.contents.

    The j01FormProcessor method returns the following response:

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
    """
    method = "j01FormProcessor"
    return doJSONRPCRequest(browser, url=url, method=method, **kwargs)


###############################################################################
#
# test setup helper
#
###############################################################################

class FormTestRequest(TestRequest):
    zope.interface.implements(z3c.form.interfaces.IFormLayer)


def getPath(filename, package=None):
    if package is None:
        package = __file__
    return os.path.join(os.path.dirname(package), filename)


def setupJSONRPCFormDefaults():
    """setup jsonrpc form defaults"""

    # setup absulutURL adapter
    zope.traversing.testing.setUp()
    zope.component.provideUtility(PlainTextPasswordManager(), IPasswordManager,
        'Plain Text')

    # setup form template
    zope.component.provideAdapter(
        z3c.template.template.TemplateFactory(
            getPath('layout.pt'), 'text/html'),
        (zope.interface.Interface, z3c.form.interfaces.IFormLayer),
        IContentTemplate)

    # setup button widgets
    zope.component.provideAdapter(
        z3c.form.widget.WidgetTemplateFactory(
            getPath('btn_display.pt', j01.jsonrpc.__file__), 'text/html'),
        (None, None, None, None, interfaces.IButtonWidget),
        IPageTemplate, name=z3c.form.interfaces.DISPLAY_MODE)

    zope.component.provideAdapter(
        z3c.form.widget.WidgetTemplateFactory(
            getPath('btn_input.pt', j01.jsonrpc.__file__), 'text/html'),
        (None, None, None, None, interfaces.IButtonWidget),
        IPageTemplate, name=z3c.form.interfaces.INPUT_MODE)

    # setup button action
    zope.component.provideAdapter(btn.ButtonAction,
        provides=z3c.form.interfaces.IButtonAction)

    # setup form adapters for jsonrpc request
    zope.component.provideAdapter(
        z3c.form.button.ButtonAction,
        (z3c.jsonrpc.interfaces.IJSONRPCRequest, z3c.form.interfaces.IButton),
        z3c.form.interfaces.IButtonAction)

    zope.component.provideAdapter(z3c.form.field.FieldWidgets,
        (z3c.form.interfaces.IFieldsForm,
         z3c.jsonrpc.interfaces.IJSONRPCRequest, zope.interface.Interface))

    zope.component.provideAdapter(
        z3c.form.browser.text.TextFieldWidget,
        adapts=(zope.schema.interfaces.ITextLine,
                z3c.jsonrpc.interfaces.IJSONRPCRequest))

    zope.component.provideAdapter(
        z3c.template.template.TemplateFactory(
            getPath('layout.pt'), 'text/html'),
        (zope.interface.Interface, z3c.jsonrpc.interfaces.IJSONRPCRequest),
        IContentTemplate)


def browserView(for_, name, factory, providing=zope.interface.Interface):
    zope.component.provideAdapter(factory,
        (for_, zope.publisher.interfaces.http.IHTTPRequest),
        providing, name=name)

def setUpAbsoluteURL():
    browserView(None, "absolute_url", zope.traversing.browser.AbsoluteURL)
    browserView(zope.location.interfaces.IRoot, "absolute_url",
        zope.traversing.browser.SiteAbsoluteURL)

    browserView(None, '', zope.traversing.browser.AbsoluteURL,
        providing=zope.traversing.browser.interfaces.IAbsoluteURL)
    browserView(zope.location.interfaces.IRoot, '',
        zope.traversing.browser.SiteAbsoluteURL,
        providing=zope.traversing.browser.interfaces.IAbsoluteURL)


###############################################################################
#
# Unittest setup
#
###############################################################################

from zope.pagetemplate.engine import Engine
from zope.pagetemplate.engine import _Engine
from zope.pagetemplate.engine import TrustedEngine
from zope.pagetemplate.engine import _TrustedEngine

def registerType(name, handler):
    Engine.registerType(name, handler)
    TrustedEngine.registerType(name, handler)


def clear():
    Engine.__init__()
    _Engine(Engine)
    TrustedEngine.__init__()
    _TrustedEngine(TrustedEngine)


try:
    from zope.testing.cleanup import addCleanUp
except ImportError:
    pass
else:
    addCleanUp(clear)


def setUp(test):
    registerType('macro', z3c.macro.tales.MacroExpression)


def tearDown(test):
    # ensure that we cleanup everything
    zope.testing.cleanup.cleanUp()


###############################################################################
#
# Test layer
#
###############################################################################

functional.defineLayer("JSONRPCTestingLayer", "ftesting.zcml",
                       allow_teardown=True)


###############################################################################
#
# Doctest setup
# NOTE: this test setup still uses the HTTPCaller given from z3c.jsonrpc
#       We should migrate z3c.jsonrpc to a webtest based setup.
#       See: XMLRPCTestTransport in zope.app.wsgi.testlayer for a sample.
#
###############################################################################

def _prepare_doctest_keywords(kw):
    globs = kw.setdefault('globs', {})
    globs['http'] = z3c.jsonrpc.testing.HTTPCaller()
    globs['getRootFolder'] = functional.getRootFolder
    globs['sync'] = functional.sync

    kwsetUp = kw.get('setUp')
    def setUp(test):
        functional.FunctionalTestSetup().setUp()
        if kwsetUp is not None:
            kwsetUp(test)
    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        if kwtearDown is not None:
            kwtearDown(test)
        functional.FunctionalTestSetup().tearDown()
    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old
                             | doctest.ELLIPSIS
                             | doctest.REPORT_NDIFF
                             | doctest.NORMALIZE_WHITESPACE)


def FunctionalDocFileSuite(*paths, **kw):
    # use our custom HTTPCaller and layer
    kw['package'] = doctest._normalize_module(kw.get('package'))
    _prepare_doctest_keywords(kw)
    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = JSONRPCTestingLayer
    return suite
