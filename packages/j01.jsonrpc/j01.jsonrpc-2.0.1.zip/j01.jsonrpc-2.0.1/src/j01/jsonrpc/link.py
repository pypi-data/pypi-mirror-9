###############################################################################
#
# Copyright (c) 2015 Projekt01 GmbH
# All Rights Reserved.
#
###############################################################################
"""Links
$Id:$
"""
__docformat__ = "reStructuredText"

UNDEFINED = object()

def isTrue(value):
    if value in [True, 'True', 'true', '1', 1, 'push']:
        return True
    else:
        # anything else then: True, 'True', 'true', '1', 'push'
        return False

def isFalse(value):
    if value in [False, 'False', 'false', '0', 0]:
        return True
    else:
        # anything else then: False, 'False', 'false', '0', 0
        return False


###############################################################################
#
# link

LINK = """<a href="%(url)s"%(attrs)s>%(content)s</a>
"""

def getLoadContentLink(request, url=None, content=None, **kws):
    """Returns a clickable <a> tag supporting testing markers

    Note: the rendered dom element is supported by p01.testbrowser testing!
    You can test this with something like:

        link = browser.getLink(text=None, url=None, id=None, index=0)
        link.click()

    """
    # get default attributes
    isPushState = kws.pop('isPushState', UNDEFINED)
    onSuccess = kws.pop('onSuccess', 'j01RenderContent')
    onError = kws.pop('onError', 'j01RenderContent')
    # setup default attributes
    data = {
        'class': 'j01LoadContentLink',
        }
    # setup testing markers
    if request.get('paste.testing'):
        # testing
        data['data-j01-testing-typ'] = 'JSONRPCClick'
        data['data-j01-testing-url'] = url
        data['data-j01-testing-method'] = 'j01LoadContent'
        data['data-j01-testing-success'] = onSuccess
        data['data-j01-testing-error'] = onError
        # we can set the isPushState in j01.jsonrpc.js, this means we don't know
        # if the default is True or False for testing. The isPushStateTesting
        # marker allows to simulate the j01.jsonrpc.js setup without to define
        # the isPushState at all.
        if isPushState is UNDEFINED:
            isPushState = kws.pop('isPushStateTesting', True)
        # add history state (isPushState) marker
        if isTrue(isPushState):
            data['data-j01-history'] = 'push'
        else:
            data['data-j01-history'] = 'false'
    else:
        # not testing, only inlcude history (isPushState) marker if explicit
        # defined as True/False, otherwise the javascript option defined in
        # j01.jsonrpc.js get used
        if isTrue(isPushState):
            # only add marker if disabled
            data['data-j01-history'] = 'push'
        if isFalse(isPushState):
            data['data-j01-history'] = 'false'
    # update and override default data
    data.update(**kws)
    # render link
    aStr = ''
    for k, v in data.items():
        aStr += ' %s="%s"' % (k, v)
    return LINK % {'url': url, 'attrs': aStr, 'content': content}


###############################################################################
#
# clickable dom element

ELEMENT = """<%(tag)s %(attrs)s>%(content)s</%(tag)s>
"""

def getLoadContentClickable(request, tag=None, url=None, content=None, **kws):
    """Returns a clickable <tag> supporting testing markers

    Note: the rendered dom element is supported by p01.testbrowser testing!
    You can test this with something like:

        clickable = browser.getClickable(text=None, url=None, id=None, index=0)
        clickable.click()

    """
    # get default attributes
    dataURLName = kws.pop('dataURLName', 'url')
    isPushState = kws.pop('isPushState', UNDEFINED)
    onSuccess = kws.pop('onSuccess', 'j01RenderContent')
    onError = kws.pop('onError', 'j01RenderContent')
    # setup default attributes
    data = {
        dataURLName: url,
        'class': 'j01LoadContentClickable',
        }
    # setup testing markers
    if request.get('paste.testing'):
        # testing
        data['data-j01-testing-typ'] = 'JSONRPCClick'
        data['data-j01-testing-url'] = url
        data['data-j01-testing-method'] = 'j01LoadContent'
        data['data-j01-testing-success'] = onSuccess
        data['data-j01-testing-error'] = onError
        # we can set the isPushState in j01.jsonrpc.js, this means we don't know
        # if the default is True or False for testing. The isPushStateTesting
        # marker allows to simulate the j01.jsonrpc.js setup without to define
        # the isPushState at all.
        if isPushState is UNDEFINED:
            isPushState = kws.pop('isPushStateTesting', True)
        # add history state (isPushState) marker
        if isTrue(isPushState):
            data['data-j01-history'] = 'push'
        else:
            data['data-j01-history'] = 'false'
    else:
        # not testing, only inlcude history (isPushState) marker if explicit
        # defined as True/False, otherwise the javascript option defined in
        # j01.jsonrpc.js get used
        if isTrue(isPushState):
            # only add marker if disabled
            data['data-j01-history'] = 'push'
        if isFalse(isPushState):
            data['data-j01-history'] = 'false'
    # update and override default data
    data.update(**kws)
    # render link
    aStr = ''
    for k, v in data.items():
        aStr += ' %s="%s"' % (k, v)
    return ELEMENT % {'tag': tag, 'attrs': aStr, 'content': content}
