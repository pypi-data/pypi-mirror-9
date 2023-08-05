/**
 * @fileoverview JSON-RPC handler methods used in j01.jsonrpc form and buttons
 *
 * @author Roger Ineichen dev at projekt01 dot ch
 * @version 1.0.1
 *
 */
//-----------------------------------------------------------------------------

var j01HTMLBody = $('html, body');

// -----------------------------------------------------------------------------
// callback registry
// -----------------------------------------------------------------------------
var j01CallbackRegistry = []; // new Array();

function j01RegisterCallback(callbackName, callback, override) {
    // register callback by name and raise error if exists
    if (callbackName !== 'j01RenderContent') {
        // skip our default handler j01RenderContent
        var key;
        for (key in j01CallbackRegistry) {
            if (key === callbackName) {
                // callback already registered
                var msg = "callback method " +callbackName+ "already exists. "
                msg += "Use j01OverrideCallback instead of j01RegisterCallback";
                alert(msg); // p01.checker.silence
            }
        }
        // add callback if not exists
        j01CallbackRegistry[callbackName] = callback;
    }
}

function j01OverrideCallback(callbackName, callback) {
    // register callback and don't riase error if exists
    j01CallbackRegistry[callbackName] = callback;
}

function j01GetCallback(callbackName) {
    // get callback by name
    if (callbackName) {
        var key;
        for (key in j01CallbackRegistry) {
            if (key === callbackName) {
                // return this callback method
                return j01CallbackRegistry[callbackName];
            }
        }
    }
    // fallback to default (generic) callback
    return j01RenderContent;
}


// -----------------------------------------------------------------------------
// load content processor
// -----------------------------------------------------------------------------

// process load content used by click event handler function
function j01LoadContentProcessor(url, callback, onError, onTimeout, isPushState, requestId) {
    // trigger loading event on body tag
    $(document).trigger('j01.jsonrpc.loading')
    proxy = getJSONRPCProxy(url);
    proxy.addMethod('j01LoadContent', callback, onError, onTimeout, isPushState, requestId);
    var params = j01URLToArray(url);
    if (params) {
        proxy.j01LoadContent(params);
    } else {
        proxy.j01LoadContent();
    }
}

// -----------------------------------------------------------------------------
// callback (response) helper
// -----------------------------------------------------------------------------

// scroll to handler (if scrollToExpression is given)
function j01RenderScrollToProcessing(response, targetContainer) {
    // process scrollTo
    if (response.scrollToExpression) {
        container = $(response.scrollToExpression);
        if (container) {
            // get previous height
            var wHeight = $(window).height();
            var sOffset = container.offset();
            if (container && sOffset) {
                var scrollTop = sOffset.top;
                if (response.scrollToOffset) {
                    scrollTop += response.scrollToOffset;
                }
                if (scrollTop >= wHeight) {
                    if (response.scrollToSpeed) {
                        scrollToSpeed = response.scrollToSpeed
                    } else {
                        scrollToSpeed = 500;
                    }
                    // scroll, but only if outside viewport and only the missing
                    // height
                    scrollTop -= wHeight;
                    j01HTMLBody.animate({'scrollTop': scrollTop}, scrollToSpeed);
                }
            }
        }
    }
}

// -----------------------------------------------------------------------------
// callback (response) handler
// -----------------------------------------------------------------------------
// generic error handling
function j01RenderContentError(response, errorTargetExpression, isPushState) {
    // handle error respnse
    /* see: z3c.publisher.interfaces.IJSONRPCErrorView
     * The z3c.publisher returns the following error data
     * {'jsonrpc': self._request.jsonVersion,
     *  'error': {'code': result.code,
     *  'message': '<server error message>',
     *  'data': {
     *      'i18nMessage': '<i18n server error message>'
     *  },
     *  'id': self._request.jsonId
     * }
     *
     * Note, the error get returned without the page involved. This means we do
     * not get a content target expression etc. which means we do not really
     * know what's to do with the error message.
     *
     * Hint: register your own error handler within your render callback an
     * do whatever you need to do for present the error in your layout.
     */
    var msg;
    if (response.data.nextURL) {
        // note, since j01.jsonrpc 0.6.0 j01.proxy supports nextURL as low
        // level error handling, but only if status is not 200
        window.location.href = response.data.nextURL;
    } else {
        if (response.data.i18nMessage){
            msg = response.data.i18nMessage;
        }else {
            msg = response.message;
        }
        // find location defined in JSONRPCErrorView or use default
        var targetContainer;
        if (response.errorTargetExpression) {
            targetContainer = $(response.errorTargetExpression);
        } else {
            targetContainer = $(errorTargetExpression);
        }
        if (targetContainer && targetContainer.get(0)) {
            // render new content
            targetContainer.empty();
            targetContainer.html(msg);
        } else {
            // if errorTargetExpression not available
            $(document).trigger({
                type: 'j01.jsonrpc.error',
                msg: msg,
            });
        }
    }
}

// generic success handling
function j01RenderContentSuccess(response, contentTargetExpression, isPushState) {
    if (response.nextURL) {
        // handle redirect based on given nextURL agument
        window.location.href = response.nextURL;
    } else {
        // success handling
        var targetContainer;
        if (response.contentTargetExpression) {
            targetContainer = $(response.contentTargetExpression);
        } else {
            targetContainer = $(contentTargetExpression);
        }
        // render new content
        targetContainer.empty();
        targetContainer.html(response.content);
        // process scrollTo
        j01RenderScrollToProcessing(response, targetContainer);
        // process browser history state
        if (typeof isPushState !== 'undefined' && isPushState) {
            // only process pushState if marked as isPushState. This prevents
            // adding bad states where ca can't reach by the given url
            j01PushState(response);
        }

    }
}

// generic response handler
function j01RenderContent(response, isPushState) {
    if (response.code) {
        // error handling
        j01RenderContentError(response, '#j01Error', isPushState);
    } else {
        // success handling with default content target expression
        j01RenderContentSuccess(response, '#content', isPushState);
    }
    // trigger end event on document
    $(document).trigger('j01.jsonrpc.loaded');
}


// -----------------------------------------------------------------------------
// content loader
// -----------------------------------------------------------------------------
// content loader offering defaults
var J01ContentLoader = function (options) {
    this.options = $.extend({
        callbackName: 'j01RenderContent',
        dataURLName: null,
        id: null,
        onError: null,
        onTimeout: null,
        isPushState: true,
        preCallFunction: null
    }, options);
    if (typeof this.options.callbackName !== "string") {
        var t = typeof this.options.callbackName;
        var msg = "j01LoadContent: callbackName must be a string not " + t;
        alert(msg); // p01.checker.silence
    }
};

J01ContentLoader.prototype.process = function (self) {
    // load content from server via jsonrpc
    // process pre call function with context
    if (this.options.preCallFunction) {
        this.options.preCallFunction(self);
    }
    // get url and callback
    if (this.options.dataURLName !== null){
        var url = $(self).data(this.options.dataURLName);
    }else{
        var url = $(self).attr('href');
    }
    // probably blocked by a href data marker
    var isPushState = $(self).data('isPushState');
    if (typeof isPushState !== 'undefined' &&
        (isPushState == 'false' || isPushState == '0')){
        isPushState = false;
    } else if (typeof isPushState !== 'undefined' &&
        (isPushState == 'true' || isPushState == '1')){
        isPushState = true;
    } else {
        isPushState = this.options.isPushState;
    }
    var callback = j01GetCallback(this.options.callbackName);
    var onTimeout = null;
    // load content
    j01LoadContentProcessor(url, callback, this.options.onError,
        this.options.onTimeout, isPushState, this.options.id);
};


// -----------------------------------------------------------------------------
// jQuery api hooks
// -----------------------------------------------------------------------------
/**
 * j01LoadContent without delegation (not recommended)
 * this plugin does not re bind handlers for new loaded content
 */
(function ($) {
    $.fn.j01LoadContent = function (options) {
        // setup loader with given options
        var loader = new J01ContentLoader(options);
        return this.each(function () {
            // apply event handler to links
            $(this).click(function (event) {
                // process with our content loader
                loader.process(this);
                event.preventDefault();
                return false;
            });
        });
    };
})(jQuery);

/**
 * j01LoadContentOn uses delegation pattern (recommended)
 * This plugin uses the delegation pattern and works on new loaded content
 * You can use your own events. Normaly you can use the j01LoadContentOnClick
 * handler which uses this method with a predefined click event.
 */
(function ($) {
    $.fn.j01LoadContentOn = function (events, selector, options) {
        // apply delegated event handler
        var loader = new J01ContentLoader(options);
        return this.on(events, selector, function (event) {
            loader.process(this);
            event.preventDefault();
            return false;
        });
    };
})(jQuery);

/**
 * j01LoadContentOnClick uses delegation pattern (recommended)
 * this plugin uses the delegation pattern and works on new loaded content
 */
(function ($) {
    $.fn.j01LoadContentOnClick = function (selector, options) {
        if (typeof selector === "object") {
            // only options given, use default selector and adjust options
            options = selector;
            selector = 'a.j01LoadContentLink';
        } else if (typeof selector === "undefined") {
            // non argument given, use default selector
            selector = 'a.j01LoadContentLink';
        }
        // apply delegated event handler to click event
        return this.j01LoadContentOn('click', selector, options);
    };
})(jQuery);

// -----------------------------------------------------------------------------
// url and form helpers
// -----------------------------------------------------------------------------
function j01RemoveURLParam(url, param) {
    var urlparts = url.split('?'),
        prefix,
        pars,
        i;
    if (urlparts.length >= 2) {
        prefix = encodeURIComponent(param) + '=';
        pars = urlparts[1].split(/[&;]/g);
        for (i = 0; i < pars.length; i = i + 1) {
            if (pars[i].indexOf(prefix, 0) === 0) {
                pars.splice(i, 1);
            }
        }
        if (pars.length > 0) {
            return urlparts[0] + '?' + pars.join('&');
        } else {
            return urlparts[0];
        }
    } else {
        return url;
    }
}

function j01URLToArray(url, params) {
    if (typeof params === "undefined") {
        params = {};
    }
    var qString = null,
        strQueryString,
        i;
    if (url.indexOf("?") > -1) {
        strQueryString = url.substr(url.indexOf("?") + 1);
        qString = strQueryString.split("&");
    }
    if (qString === null) {
        if (typeof params !== "undefined") {
            return params;
        }else{
            return null;
        }
    }
    for (i = 0; i < qString.length; i = i + 1) {
        params[qString[i].split("=")[0]] = qString[i].split("=")[1];
    }
    return params;
}

(function ($) {
    /**
     * Serializes form data into a 'submittable' string. This method will
     * return string in the format: url?name1=value1&amp;name2=value2 or url
     */
    $.fn.j01FormToURL = function (url) {
        //hand off to jQuery.param for proper encoding
        var query = this.serialize();
        if (query) {
            return url +'?'+ query;
        } else {
            return url;
        }
    };

    /**
     * Taken from jquery.form and modified. We use an object instead of an
     * array as data container. This makes it possible to use the data with
     * JSON-RPC.
     *
     * j01FormToArray() gathers form element data into a data object which is a
     * collection of objects. Each object in the data object provides the field
     * name and the value. An example of an array for a simple login form might
     * be: {'login': 'jresig', 'password': 'secret'}
     */
    $.fn.j01FormToArray = function (handlerName) {
        var data = {},
            form,
            els,
            i,
            max,
            el,
            n,
            v,
            j,
            jmax,
            inputs,
            input;
        function add(n, v) {
            if (v !== null && typeof v !== 'undefined') {
                if (data[n]) {
                    var val = data[n];
                    if (val && val.constructor === Array) {
                        val.push(v);
                    } else {
                        val = [data[n]];
                        val.push(v);
                    }
                    data[n] = val;

                } else {
                    data[n] = v;
                }
            }
        }
        if (this.length === 0) {
            return data;
        }

        form = this[0];
        els = form.elements;
        if (!els) {
            return data;
        }
        for (i = 0, max = els.length; i < max; i = i + 1) {
            el = els[i];
            n = el.name;
            if (!n) {
                continue;
            }

            v = $.j01FieldValue(el);
            if (v && v.constructor === Array) {
                for (j = 0, jmax = v.length; j < jmax; j = j + 1) {
                    add(n, v[j]);
                }
            } else {
                if (v !== null && typeof v !== 'undefined') {
                    add(n, v);
                }
            }
        }

        if (form.clk) {
            // input type=='image' are not found in elements array! handle them here
            inputs = form.getElementsByTagName("input");
            for (i = 0, max = inputs.length; i < max; i = i + 1) {
                input = inputs[i];
                n = input.name;
                if (n && !input.disabled && input.type === "image" && form.clk === input) {
                    add(n + '.x', form.clk_x);
                    add(n + '.y', form.clk_y);
                }
            }
        }
        if (handlerName) {
            add('j01FormHandlerName',  handlerName);
        }
        return data;
    };

    $.j01FieldValue = function (el) {
        var n = el.name,
            t = el.type,
            tag = el.tagName.toLowerCase(),
            index,
            a,
            ops,
            one,
            max,
            i,
            op,
            v;

        if (!n || el.disabled || t === 'reset' || t === 'button' ||
                ((t === 'checkbox' || t === 'radio') && !el.checked) ||
                ((t === 'submit' || t === 'image') && el.form && el.form.clk !== el) ||
                (tag === 'select' && el.selectedIndex === -1)) {
            return null;
        }

        if (tag === 'select') {
            index = el.selectedIndex;
            if (index < 0) {
                return null;
            }
            a = [];
            ops = el.options;
            one = (t === 'select-one');
            max = (one ? index + 1 : ops.length);
            for (i = (one ? index : 0); i < max; i = i + 1) {
                op = ops[i];
                if (op.selected) {
                    // extra pain for IE...
                    v = $.browser.msie && !(op.attributes.value.specified) ? op.text : op.value;
                    if (one) {
                        return v;
                    }
                    a.push(v);
                }
            }
            return a;
        }
        return el.value;
    };
})(jQuery);
