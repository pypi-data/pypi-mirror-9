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

$Id: __init__.py 4132 2015-01-20 11:21:23Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import os
import json
import doctest
import urlparse

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

def setUpAbsoluteURL(): #pragma: nocover
    # zope.component.provideAdapter(Traverser, (None,), ITraverser)
    # zope.component.provideAdapter(DefaultTraversable, (None,), ITraversable)
    # zope.component.provideAdapter(LocationPhysicallyLocatable,
    #                               (None,), ILocationInfo)
    # zope.component.provideAdapter(RootPhysicallyLocatable,
    #                               (IRoot,), ILocationInfo)
    # # set up the 'etc' namespace
    # zope.component.provideAdapter(etc, (None,), ITraversable, name="etc")
    # zope.component.provideAdapter(etc, (None, None), ITraversable, name="etc")

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
# jsonrpc testing helper
# NOTE: this methods require a zope.testbrowser > 5.0.0 or p01.testbrowser
# browser instance providing the wsgi application as browser.testapp
#
###############################################################################

def getReplyContent(response):
    data = json.loads(response.content)
    try:
        if isinstance(data['result'], basestring):
            return data['result']
        if data['result'].get('nextURL'):
            return 'REDIRECT TO ' + str(data['result']['nextURL'])
        return data['result']['content']
    except TypeError:
        return data['result']


def doJSONRPC(browser, url=None, params=None, button=None, headers=None, method=None):
    """Process jsonrpc call

    NOTE: this method requires the new zope.testbrowser >= 5.0.0 (not released
    yet) or the p01.testbrowser (copy of zope.testbrowser >= 5.0.0 dev) as
    browser instance. This new testbrowser implementation use a webtest based
    browser providing the wsgi application as browser.testapp for process the
    given request.
    """
    contents = browser.contents
#    conn = zope.app.testing.testbrowser.PublisherConnection('localhost:9090')
    if url is None:
        url = browser.url
        r = list(urlparse.urlparse(url))
        r[0] = ''
        r[1] = ''
        r[4] = ''
        url = urlparse.urlunparse(r)
    if params is None:
        params = {}
    if button is not None:
        params["j01FormHandlerName"] = button
    data = {"jsonrpc": "2.0",
            "id": "jsonRequest",
            "method": method,
            "params": params,
            }
    if headers is None:
        headers = {'Accept-Language': 'en-us,en',
                   'Connection': 'close',
                   'Content-Type': 'application/json; charset=UTF-8',
                   'User-Agent': 'Python-urllib/2.7',
                   'X-Zope-Handle-Errors': 'False',
                   'Host': 'localhost:9090',
                   'Referer': browser.url}
        cookies = browser.cookies.header
        if cookies:
            headers['cookie'] = cookies
    body = json.dumps(data)
    body = body.encode('utf8')

# XXX: process request and merge response into previous content using similar
#      methods like we use in javascript

#    conn.request('POST', url, body.encode('utf8'), headers)
#    resp = conn.getresponse()
#    browser.testapp.post(url, body, **args)
#    resp =

    if method == 'j01FormProcessor':
        # inject content into existing content using lxml parser
#        contents =
        browser._response = 'XXX j01.jsponrpc.testing.doJSONRPC implement this XXX'

#    if retContent:
#        return getReplyContent(resp)
#    return resp


def j01Dialog(browser, url=None, headers=None):
    return doJSONRPC(browser, url, headers, method="j01Dialog")


def j01DialogFormProcessor(browser, url=None, params=None, button=None, headers=None):
    return doJSONRPC(browser, url, params, button, headers, method="j01DialogFormProcessor")


def j01FormProcessor(browser, url=None, params=None, button=None, headers=None):
    return doJSONRPC(browser, url, params, button, headers, method="j01FormProcessor")


def getNextURL(browser):
    reply = json.loads(browser.content)
    return str(reply['result']['nextURL'])


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
