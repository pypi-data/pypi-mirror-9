###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH
# All Rights Reserved.
#
###############################################################################
"""Buttons
$Id: btn.py 4145 2015-02-02 05:22:17Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import os
import sys

import zope.schema
import zope.interface
import zope.component
import zope.i18nmessageid
import zope.location
import zope.interface.adapter
from zope.pagetemplate.interfaces import IPageTemplate
from zope.schema.fieldproperty import FieldProperty

import z3c.form.interfaces
import z3c.form.button
import z3c.form.action
import z3c.form.widget
import z3c.form.util
import z3c.form.browser.widget

from j01.jsonrpc import interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


try:
    unicode
except NameError:
    # Py3: Define unicode.
    unicode = str


###############################################################################
#
# decorators

def handler(btnOrName):
    """A decorator for defining a success handler."""
    if isinstance(btnOrName, basestring):
        __name__ = btnOrName
    else:
        __name__ = btnOrName.__name__
    def createHandler(func):
        handler = Handler(func)
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        handlers = f_locals.setdefault('handlers', Handlers())
        handlers.addHandler(__name__, handler)
        return handler
    return createHandler


def buttonAndHandler(btnOrTitle, *args, **kwargs):
    """Button and handler setup decorator"""
    if isinstance(btnOrTitle, basestring):
        # add the title to button constructor keyword arguments
        kwargs['title'] = btnOrTitle
        # create button and add it to the button manager
        button = Button(**kwargs)
    else:
        button = btnOrTitle
    if args:
        __name__ = args[0]
    else:
        __name__ = kwargs.get('name', button.__name__)
    for k, v in kwargs.items():
        if k == 'name':
            continue
        # apply additional attributes
        setattr(button, k, v)
    # Extract directly provided interfaces:
    provides = kwargs.pop('provides', ())
    if provides:
        zope.interface.alsoProvides(button, provides)
    frame = sys._getframe(1)
    f_locals = frame.f_locals
    buttons = f_locals.setdefault('buttons', Buttons())
    f_locals['buttons'] += Buttons(button)
    # return create handler method
    return handler(button and button or __name__)


###############################################################################
#
# action and handler concept

import zope.interface.interfaces

# IButtons
@zope.interface.implementer(interfaces.IButtons)
class Buttons(z3c.form.button.Buttons):
    """Button manager."""

    def __init__(self, *args):
        buttons = []
        for arg in args:
            if zope.interface.interfaces.IInterface.providedBy(arg):
                for name, button in zope.schema.getFieldsInOrder(arg):
                    if interfaces.IButton.providedBy(button):
                        buttons.append((name, button))
            elif self.managerInterface.providedBy(arg):
                buttons += arg.items()
            elif interfaces.IButton.providedBy(arg):
                if not arg.__name__:
                    arg.__name__ = z3c.form.util.createId(arg.title)
                buttons.append((arg.__name__, arg))
            else:
                raise TypeError("Unrecognized argument type", arg)
        keys = []
        seq = []
        byname = {}
        for name, button in buttons:
            keys.append(name)
            seq.append(button)
            byname[name] = button

        self._data_keys = keys
        self._data_values = seq
        self._data = byname

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter java script code if the inputEnterActionName
        name defines a button and the button condition is True.
        """
        # find and return the form submit javascript
        btnName = getattr(form, 'inputEnterActionName', None)
        if btnName is not None:
            button = self.get(btnName)
            # note button AND condition could be None
            if button is not None:
                if button.condition is None or (
                    button.condition is not None and button.condition(form)):
                    return button.getInputEnterJavaScript(form, request)

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self._data.keys())


@zope.interface.implementer(interfaces.IButtonHandlers)
class Handlers(object):
    """Action Handlers for a Button-based form."""

    def __init__(self):
        # setup name, handler container
        self._data = {}

    def addHandler(self, name, handler):
        self._data[name] = handler

    def getHandler(self, name, default=None):
        return self._data.get(name, default)

    def copy(self):
        handlers = Handlers()
        for name, handler in self._data.items():
            handlers.addHandler(name, handler)
        return handlers

    def __add__(self, other):
        """See interfaces.IButtonHandlers"""
        if not isinstance(other, Handlers):
            raise NotImplementedError
        handlers = self.copy()
        for name, handler in other._data.items():
            handlers.addHandler(name, handler)
        return handlers

    def __call__(self):
        handler = self.form.handlers.getHandler(self.action.field)
        # If no handler is found, then that's okay too.
        if handler is None:
            return
        return handler(self.form, self.action)

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self._data.keys())


@zope.interface.implementer(interfaces.IButtonHandler)
class Handler(object):
    """Handler handler."""

    def __init__(self, func):
        self.func = func

    def __call__(self, form, action):
        return self.func(form, action)

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.func.__name__)


@zope.interface.implementer(interfaces.IActionHandler)
class ActionHandler(object):
    """Button handler executer.

    This adapter makes it possible to execute button handler.
    """

    zope.component.adapts(
        z3c.form.interfaces.IForm,
        zope.interface.Interface,
        zope.interface.Interface,
        z3c.form.interfaces.IButtonAction)

    def __init__(self, form, request, content, action):
        self.form = form
        self.request = request
        self.content = content
        self.action = action

    def __call__(self):
        handler = self.form.handlers.getHandler(self.action.__name__)
        if handler is None:
            return
        return handler(self.form, self.action)


###############################################################################
#
# button action widget

@zope.interface.implementer(interfaces.IButtonAction)
@zope.component.adapter(z3c.form.interfaces.IFormLayer, interfaces.IButton)
class ButtonAction(z3c.form.action.Action,
    z3c.form.browser.widget.HTMLInputWidget, z3c.form.widget.Widget,
    zope.location.Location):
    """A button action supporting javascript"""

    klass = u'button-widget'

    def __init__(self, request, field):
        z3c.form.action.Action.__init__(self, request, field.title)
        z3c.form.widget.Widget.__init__(self, request)
        self.field = field

    def isExecuted(self):
        j01FormHandlerName = self.request.get('j01FormHandlerName')
        if j01FormHandlerName and self.name.endswith(j01FormHandlerName):
            return True
        else:
            # also support non JSONRPC request concept for urls like
            # <page-url>?form.buttons.foobar=1
            return self.name in self.request

    @property
    def _type(self):
        return self.field._type

    @property
    def accesskey(self):
        return self.field.accessKey

    @property
    def value(self):
        return self.title

    @property
    def id(self):
        return self.name.replace('.', '-')

    # access css from button
    @property
    def css(self):
        return self.field.css

    @property
    def javascript(self):
        return self.field.getJavaScript(self, self.request)

    @property
    def data(self):
        """Returns relevant widget data used for button template"""
        data = {
            'type': self._type,
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'class': self.css and self.css or self.klass,
            }
        for attrName in self.field.attrNames:
            v = getattr(self, attrName, None)
            if v:
                data[attrName] = v
        # apply button data
        btnData = self.field.getData(self, self.request)
        if btnData:
            dstr = ''
            for k, v in btnData.items():
                dstr += 'data-%s="%s" ' % (k, v)
            data['data'] = dstr
        else:
            data['data'] = ''
        return data

#    def update(self):
#        # We simply use a given css class or fallback to the default klass
#        if not self.klass:
#            self.klass = ''
#        classes = self.klass.split()
#        if self.field.css:
#            # make sure items are not repeated and prepend css classes
#            classes = self.field.css.split() + classes
#        # make sure every class is unique
#        seen = {}
#        unique = []
#        for item in classes:
#            if item in seen:
#                continue
#            seen[item]=1
#            unique.append(item)
#        self.klass = u' '.join(unique)

    def update(self):
        # skip super widget update call
        pass

    def render(self):
        """Render the plain widget without additional layout"""
        if self.field.template is not None:
            # use the button string template providing data attributes
            javascript = self.javascript
            if javascript:
                javascript = '\n<script>%s</script>' % javascript
            else:
                javascript = ''
            return '%s%s' % (self.field.template % self.data, javascript)
        else:
            # use the page template (only used if template=None get used in
            # button setup
            template = self.template
            if template is None:
                template = zope.component.getMultiAdapter(
                    (self.context, self.request, self.form, self.field, self),
                    IPageTemplate, name=self.mode)
            return template(self)


###############################################################################
#
# submit buttons

BUTTON = """<input type="%(type)s" id="%(id)s" name="%(name)s" class="%(class)s" value="%(value)s" %(data)s/>
"""

@zope.interface.implementer(interfaces.IButton)
class Button(zope.schema.Field):
    """A button with a custom css class attribute"""

    accessKey = FieldProperty(interfaces.IButton['accessKey'])
    actionFactory = FieldProperty(interfaces.IButton['actionFactory'])
    css = FieldProperty(interfaces.IButton['css'])

    _type = 'submit'

    # used attribute names
    attrNames = [
        'tabindex'
        'title',
        'alt',
        ]

    data = None
    dataGetter = None
    template = BUTTON

    def __init__(self, *args, **kwargs):
        # Provide some shortcut ways to specify the name
        if args:
            kwargs['__name__'] = args[0]
            args = args[1:]
        if 'name' in kwargs:
            kwargs['__name__'] = kwargs['name']
            del kwargs['name']
        # apply additonal data key/values
        if 'template' in kwargs:
            self.template = kwargs['template']
            del kwargs['template']
        # apply additonal data key/values
        if 'data' in kwargs:
            self.data = kwargs['data']
            del kwargs['data']
        # apply optional dataGetter
        if 'dataGetter' in kwargs:
            self.dataGetter = kwargs['dataGetter']
            del kwargs['dataGetter']
        # apply optional css, which get added in front of other classes
        if 'css' in kwargs:
            self.css = kwargs['css']
            del kwargs['css']
        # Extract button-specific arguments
        self.accessKey = kwargs.pop('accessKey', None)
        self.condition = kwargs.pop('condition', None)
        # Initialize the button
        super(Button, self).__init__(*args, **kwargs)

    def getInputEnterJavaScript(self, form, request):
        """A simple button doesn't provide any javascript"""
        return u""

    def getJavaScript(self, action, request):
        """A simple button doesn't provide any javascript"""
        return u""

    def getData(self, action, request):
        """Returns additional data attibutes"""
        data = {}
        if self.data is not None:
            data.update(self.data)
        if self.dataGetter is not None:
            data.update(self.dataGetter(action, request))
        return data

    def __repr__(self):
        return '<%s %r %r>' %(self.__class__.__name__, self.__name__,
            self.title)


###############################################################################
#
# javascript buttons

@zope.interface.implementer(interfaces.IJSButton)
class JSButton(Button):
    """JS button.

    This is the basic implementation and only shows an alert message. Use this
    class for implement your own custom buttons.
    """

    _type = 'button'
    urlGetter = None

    def __init__(self, *args, **kwargs):
        # apply optional urlGetter
        if 'urlGetter' in kwargs:
            self.urlGetter = kwargs['urlGetter']
            del kwargs['urlGetter']
        super(JSButton, self).__init__(*args, **kwargs)

    def getURL(self, form, request):
        """Returns the url based on urlGetter or the form url"""
        if self.urlGetter is not None:
            return self.urlGetter(form)
        else:
            return form.pageURL

    def getInputEnterJavaScript(self, form, request):
        raise NotImplementedError(
            "Subclass must implement getInputEnterJavaScript method")

    def getJavaScript(self, action, request):
        raise NotImplementedError(
            "Subclass must implement getJavaScript method")


# JQuery trigger event
TRIGGER_JAVASCRIPT = """
                $btn.trigger({
                    type: '%(type)s',
                    form: '%(form)s',
                    action: '%(action)s',
                    handler: '%(handler)s'
                });"""

class TriggerMixin(object):
    """JQuery event trigger mixin

    Include j01.form.button.js for support button loading messages and button
    disable state.

    Enable JQuery event trigger with default j01.form.button.click event
    or implement your own event type using the trigger attribute. You can also
    add more event attributes by implement your own trigger call using the
    jsTrigger attribute.
    """

    loading = None
    trigger = None
    jsTrigger = None
    defaultTriggerEventType = 'j01.form.button.click'

    def __init__(self, *args, **kwargs):
        # apply button loading setup
        if 'loading' in kwargs:
            # setup i18n loading message
            self.loading = kwargs['loading']
            del kwargs['loading']
        # apply button trigger setup (also required for loading conecpt)
        if 'trigger' in kwargs:
            self.trigger = kwargs['trigger']
            del kwargs['trigger']
            if self.trigger is True:
                # trigger arg was True, use default trigger event type
                self.trigger = self.defaultTriggerEventType
            self.jsTrigger = TRIGGER_JAVASCRIPT
        if 'jsTrigger' in kwargs:
            # allow to override the javascript
            self.jsTrigger = kwargs['jsTrigger']
            del kwargs['jsTrigger']
        super(TriggerMixin, self).__init__(*args, **kwargs)

    def getData(self, action, request):
        data = super(TriggerMixin, self).getData(action, request)
        if self.loading:
            data['j01-loading-text'] = zope.i18n.translate(self.loading,
                context=request)
        return data

    def getTrigger(self, action):
        if self.jsTrigger:
            return self.jsTrigger % {
                'type': self.trigger,
                'form': action.form.id.replace('.', '\\\.'),
                'action': action.id,
                'handler': self.__name__,
                }
        else:
            return ''


# form processing button
@zope.interface.implementer(interfaces.IJSONRPCButton)
class JSONRPCButton(TriggerMixin, JSButton):
    """JSON-RPC for msubmit button

    This button will submit a form using the JSON-RPC method j01FormProcessor
    and renders the content into the existing page dom using the javascript
    method j01RenderContent.

    Only use this button if the form is a part of the loading JSON-RPC content.
    If the form tag is not a part of the loading JSON-RPC content them button
    javascript will apply it's handler to the form again and again which will
    end in multiple form submits on click. Use the JSONRPCClickButton if the
    form tag is not a part of the loading JSON-RPC content.

    Redirect is also supported if the form will set a nextURL. Or you can
    define a location where the content should get rendered by define a
    contentTargetExpression in your page/form.

    The getInputEnterJavaScript method get called if you set the buttons
    action handler name as inputEnterActionName value e.g:

    inputEnterActionName = 'applyChanges'

    Don't forget to include the inputEnterJavaScript part in your form
    template if you use an inputEnterActionName e.g.:

    <script type="text/javascript"
            tal:content="view/inputEnterJavaScript"> </script>

    This button requires the following javascript files:

    - jquery.js >= 1.7.0
    - j01.proxy.js
    - j01.jsonrpc.js

    NOTE: The form using this button must contain the form tag. If the form
    tag doesn't get rendered within each new request, the button click handler
    will get applied more then once to the form and will submit the form more
    then once.

    Note: file uploads can't get handeled by JSON-RPC or ajax. You have to
    use an iframe. See j01.dialog for built in iframe support.

    Note: the rendered button is supported by p01.testbrowser testing!
    You can test this with something like:

        button = browser.getControl(label=None, name=None, index=None)
        button.click()

    """

    typ = 'JSONRPCButton'
    method = 'j01FormProcessor'
    onSuccess = 'j01RenderContentSuccess'
    onError = 'j01RenderContentError'
    onTimeout = None
    isPushState = None
    idGetter = None

    def __init__(self, *args, **kwargs):
        # conditions
        if 'onSuccess' in kwargs and 'callback' in kwargs:
            raise ValueError(
                "Can't use onSuccess and callback argument for button setup")
        if 'onError' in kwargs and 'callback' in kwargs:
            raise ValueError(
                "Can't use onError and callback argument for button setup")
        # apply callback methods
        if 'onSuccess' in kwargs:
            self.onSuccess = kwargs['onSuccess']
            del kwargs['onSuccess']
        if 'onError' in kwargs:
            self.onError = kwargs['onError']
            del kwargs['onError']
        if 'onTimeout' in kwargs:
            self.onTimeout = kwargs['onTimeout']
            del kwargs['onTimeout']
        if 'callback' in kwargs:
            self.onSuccess = kwargs['callback']
            self.onError = kwargs['callback']
            del kwargs['callback']
        # apply isPushState
        if 'isPushState' in kwargs:
            self.isPushState = kwargs['isPushState']
            del kwargs['isPushState']
        # apply jsonrpc request id getter method
        if 'idGetter' in kwargs:
            self.idGetter = kwargs['idGetter']
            del kwargs['idGetter']

        # apply loading message
        if 'loading' in kwargs:
            self.loading = kwargs['loading']
            del kwargs['loading']
        super(JSONRPCButton, self).__init__(*args, **kwargs)

    def getData(self, action, request):
        """Returns additional data attibutes and the testing control type

        NOTE: this button data attributes are used for testing. The Browser
        located in p01.testbrowser.browser is able to handle the button clicks
        using python testing hook methods.
        """
        data = super(JSONRPCButton, self).getData(action, request)
        if request.get('paste.testing'):
            data['j01-testing-typ'] = self.typ
            data['j01-testing-url'] = self.getURL(action.form, request)
            data['j01-testing-form'] = action.form.name
            data['j01-testing-method'] = self.method
            data['j01-testing-error'] = self.onError
            data['j01-testing-success'] = self.onSuccess
            if self.onTimeout:
                data['j01-testing-timeout'] = self.onTimeout
        return data

    def getMethodArguments(self, request):
        """Returns the method arguments (don't skip one, except the last)"""
        # method, onSuccess, onError
        res = "'%s', %s, %s" % (self.method, self.onSuccess, self.onError)
        # onTimeout
        if self.onTimeout:
            res  += ", %s" % self.onTimeout
        else:
            res += ", null"
        # isPushState
        if self.isPushState is True:
            res  += ", true"
        elif self.isPushState is False:
            res  += ", false"
        else:
            res += ", null"
        # id
        if self.idGetter is not None:
            id = self.idGetter(request)
            if id is not None:
                res  += ", '%s'" % id
        return res

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter JavaScript code"""
        # replace dots in id with '\\.' See jquery.com for details
        return """
            $('#%(form)s').on('keypress', 'input', function(){
                if(!e){e = window.event;}
                key = e.which ? e.which : e.keyCode;
                if (key == 13) {
                    var data = $('#%(form)s').j01FormToArray('%(handler)s');
                    proxy = getJSONRPCProxy('%(url)s');
                    proxy.addMethod(%(arguments)s);
                    proxy.%(method)s(data);
                    return false;
                }
            });
            """ % {'form': form.id.replace('.', '\\\.'),
                   'url': self.getURL(form, request),
                   'handler': self.__name__,
                   'method': self.method,
                   'arguments': self.getMethodArguments(request),
                   }

    def getJavaScript(self, action, request):
        # replace dots in id with '\\.' See jquery.com for details
        return """
            $('#%(form)s').on('click', '#%(action)s', function(){
                var $btn = $('#%(action)s');
                if (!$btn.prop('disabled')) {%(trigger)s
                    var data = $('#%(form)s').j01FormToArray('%(handler)s');
                    proxy = getJSONRPCProxy('%(url)s');
                    proxy.addMethod(%(arguments)s);
                    proxy.%(method)s(data);
                }
                return false;
            });
            """ % {'form': action.form.id.replace('.', '\\\.'),
                   'url': self.getURL(action.form, request),
                   'action': action.id,
                   'handler': self.__name__,
                   'trigger': self.getTrigger(action),
                   'method': self.method,
                   'arguments': self.getMethodArguments(request),
                   }


@zope.interface.implementer(interfaces.IJSONRPCButton)
class JSONRPCClickButton(JSONRPCButton):
    """JSON-RPC for msubmit button

    This button will submit a form using the JSON-RPC method j01FormProcessor
    and renders the content into the existing page dom using the javascript
    method j01RenderContent.

    The difference between this and the JSONRPCButton is that this button uses
    a JQuery delegation pattern. This means we don't apply the javascript event
    handler again on loading content conatining such a button. This is
    important if the form tag itself is contained in the dom and not a part of
    the loaded JSON-RPC content.

    If the edit form does not contain the form tag (partial jsonrpc loaded
    content in a large form), we need to use another pattern then the default
    .on('click', ..) handler. Otherwise we whould (re)apply everytime the edit
    button get loaded without to remove them from the form tag. This is because
    the form contains the delegated event handler if we sould use the
    .on('click',...) handler.

    This button uses a simple click handler which will get removed including
    it's click handler if the button get removed.

    IMPORTANT: If you use more then one JSONRPC form in one page you need to
    use different widget and button prefixes. Otherwise the button click
    handler get blocked if the same button is used in loaded open forms.
    The widget prefix is important if you use the same form field names in 2
    different forms loaded in the same page.

    The widget prefix will get changed by define a prefixWidgets property
    and the buttons prefix will get changed by define a prefixButtons property.
    See the improved updateWidgets and updateActions methods in JSONRPCForm

    Note: the rendered button is supported by p01.testbrowser testing!
    You can test this with something like:

        button = browser.getControl(label=None, name=None, index=None)
        button.click()

    """

    typ = 'JSONRPCClickButton'
    method = 'j01FormProcessor'
    onSuccess = 'j01RenderContentSuccess'
    onError = 'j01RenderContentError'

    def getInputEnterJavaScript(self, form, request):
        # not supported yet
        return ""

    def getJavaScript(self, action, request):
        # replace dots in id with '\\.' See jquery.com for details
        return """
            $('#%(action)s').click(function(){
                var $btn = $(this);
                if (!$btn.prop('disabled')) {%(trigger)s
                    var data = $('#%(form)s').j01FormToArray('%(handler)s');
                    proxy = getJSONRPCProxy('%(url)s');
                    proxy.addMethod(%(arguments)s);
                    proxy.%(method)s(data);
                }
                return false;
            });
            """ % {'form': action.form.id.replace('.', '\\\.'),
                   'action': action.id,
                   'handler': self.__name__,
                   'method': self.method,
                   'trigger': self.getTrigger(action),
                   'url': self.getURL(action.form, request),
                   'arguments': self.getMethodArguments(request),
                   }


# simple content loader button
@zope.interface.implementer(interfaces.IJSONRPCButton)
class JSONRPCContentButton(JSONRPCButton):
    """JSONRPC content loader button

    This button will load and render content via JSON-RPC from a JSONRPC page
    or form. The form does not get processed the form actions if we get the
    content from a form.

    The JSON-RPC method j01LoadContent get used for loading content.

    The callback method j01RenderContent is responsible for render the given
    content to the target defined by contentTargetExpression

    The optional urlGetter method can get used for define the url where the
    form content get loaded. By default the urlGetter uses the built in
    page url based on the pageURL property.

    This button requires the following javascript files:

    - jquery.js >= 1.7.0
    - j01.proxy.js
    - j01.jsonrpc.js

    NOTE: The form using this button must contain the form tag. If the form
    tag doesn't get rendered within each new request, the button click handler
    will get applied more then once to the form and doesn't work.

    Note: the rendered button is supported by p01.testbrowser testing!
    You can test this with something like:

        button = browser.getControl(label=None, name=None, index=None)
        button.click()

    """

    typ = 'JSONRPCContentButton'
    method = 'j01LoadContent'
    onSuccess = 'j01RenderContentSuccess'
    onError = 'j01RenderContentError'

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter JavaScript code."""
        # replace dotted id with '\\.' See jquery.com for details
        return """
            $('#%(form)s').on('keypress', 'input', function(){
                if(!e){e = window.event;}
                key = e.which ? e.which : e.keyCode;
                if (key == 13) {
                    proxy = getJSONRPCProxy('%(url)s');
                    proxy.addMethod(%(arguments)s);
                    proxy.%(method)s();
                    return false;
                }
            });
            """ % {'form': form.id.replace('.', '\\\.'),
                   'url': self.getURL(form, request),
                   'method': self.method,
                   'arguments': self.getMethodArguments(request),
                   }

    def getJavaScript(self, action, request):
        """Returns the button javascript code"""
        # replace dotted id with '\\.' See jquery.com for details
        return """
            $('#%(form)s').on('click', '#%(action)s', function(){
                var $btn = $('#%(action)s');
                if (!$btn.prop('disabled')) {%(trigger)s
                    proxy = getJSONRPCProxy('%(url)s');
                    proxy.addMethod(%(arguments)s);
                    proxy.%(method)s();
                }
                return false;
            });
            """ % {'form': action.form.id.replace('.', '\\\.'),
                   'action': action.id,
                   'trigger': self.getTrigger(action),
                   'method': self.method,
                   'url': self.getURL(action.form, request),
                   'arguments': self.getMethodArguments(request),
                   }


# form processing button
@zope.interface.implementer(interfaces.IJSButton)
class CloseButton(TriggerMixin, JSButton):
    """Generic close button which will remove content from a html page.

    Note: the rendered button is supported by p01.testbrowser testing!
    You can test this with something like:

        button = browser.getControl(label=None, name=None, index=None)
        button.click()

    The expression defines a JQuery selector. The content contained will
    get removed from the dom on button click.

    This button requires the following javascript files:

    - jquery.js >= 1.7.0
    """

    typ = 'CloseButton'
    expression = 'form'
    animation = 'slideUp'
    duration = 400

    def __init__(self, *args, **kwargs):
        # apply expression
        if 'expression' in kwargs:
            self.expression = kwargs['expression']
            del kwargs['expression']
        # animation
        if 'animation' in kwargs:
            self.animation = kwargs['animation']
            del kwargs['animation']
        if self.animation not in ['slideUp', 'slideDown',]:
            raise ValueError("animation must be one of slideUp, slideDown")
        # apply duration
        if 'duration' in kwargs:
            self.duration = kwargs['duration']
            del kwargs['duration']
        super(CloseButton, self).__init__(*args, **kwargs)

    def getData(self, action, request):
        """Returns additional data attibutes and the testing control type

        NOTE: this button data attributes are used for testing. The Browser
        located in p01.testbrowser.browser is able to handle the button clicks
        using python testing hook methods.
        """
        data = super(CloseButton, self).getData(action, request)
        if request.get('paste.testing'):
            data['j01-testing-typ'] = self.typ
            data['j01-testing-expression'] = self.expression
        return data

    def getInputEnterJavaScript(self, form, request):
        # not supported yet
        return ""

    def getJavaScript(self, action, request):
        # replace dots in id with '\\.' See jquery.com for details
        return """
            $('#%(action)s').click(function(){
                var $btn = $(this);
                if (!$btn.prop('disabled')) {%(trigger)s
                    var part = $('%(expression)s');
                    part.%(animation)s(%(duration)s, function() {
                        part.empty();
                        part.show();
                    });
                }
                return false;
            });
            """ % {'form': action.form.id.replace('.', '\\\.'),
                   'action': action.id,
                   'trigger': self.getTrigger(action),
                   'expression': self.expression,
                   'animation': self.animation,
                   'duration': self.duration,
                   }


def canDelete(form):
    if hasattr(form, 'supportsDelete'):
        return form.supportsDelete
    return True


class IJSONRPCButtons(zope.interface.Interface):

    add = JSONRPCButton(
        title=_(u'Add')
        )

    applyChanges = JSONRPCButton(
        title=_(u'Apply')
        )

    delete = JSONRPCButton(
        title=_(u'Delete'),
        condition=canDelete
        )

    search = JSONRPCButton(
        title=_(u'Search')
        )

    cancel = JSONRPCButton(
        title=_(u'Cancel')
        )

    close = CloseButton(
        title=_(u'Close')
        )
