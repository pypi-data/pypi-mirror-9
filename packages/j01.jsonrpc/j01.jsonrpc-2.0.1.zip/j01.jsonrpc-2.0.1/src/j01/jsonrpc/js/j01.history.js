// -----------------------------------------------------------------------------
// j01.jsonrpc.js browser history support
// -----------------------------------------------------------------------------
/* We provide the browser history concept out of the box without any special
 * configuration. This means we will pushState after the content get loaded and
 * the content get applied to the right place in the page. We do not apply
 * anything if an error get handled. You can simple change this pushState
 * handling concept in your own custom content handling methods.
 *
 * Note: if you like to support a push state history for jsonrpc error views
 * you can simply register your own jsonrpc error view and provide state data
 * in the error view result.
 *
 * Also check the p01.testbrowser package which is able to simulate this
 * history concept out of the box.
 *
 * See: HistoryStateMixin located in j01/jsonrpc/__init__.py for more
 * information about how to control the history state handling.
 */

/* Chrome fires the onpopstate event when the document has been loaded. This
 * is not intended, so we block popstate events until the the first event
 * loop cicle after document has been loaded. This is done by the
 * preventDefault and stopImmediatePropagation calls (unlike stopPropagation
 * stopImmediatePropagation stops all event handler calls instantly).
 * However, since the document's readyState is already on "complete" when
 * Chrome fires onpopstate erroneously, we allow opopstate events, which have
 * been fired before document loading has been finished to allow onpopstate
 * calls before the document has been loaded.
 * Update 2014-04-23: Fixed a bug where popstate events have been blocked if
 * the script is executed after the page has been loaded.
 * http://stackoverflow.com/questions/6421769/popstate-on-pages-load-in-chrome
 */
(function() {
    // There's nothing to do for older browsers ;)
    if (!window.addEventListener)
        return;
    var blockPopstateEvent = document.readyState != "complete";
    window.addEventListener("load", function() {
        // In WebKit browsers, a popstate event would be triggered after
        // document's onload event, but Firefox and IE do not have this
        // behavior.
        // The timeout ensures that popstate-events will be unblocked right
        // after the load event occured, but not in the same event-loop cycle.
        setTimeout(function(){ blockPopstateEvent = false; }, 0);
    }, false);
    window.addEventListener("popstate", function(evt) {
        if (blockPopstateEvent && document.readyState == "complete") {
            evt.preventDefault();
            evt.stopImmediatePropagation();
        }
    }, false);
})();

function j01PushState(response) {
    // push state data given from success or error response to browser history
    // Note: this method must get called explicit in your javascript code. We
    // call this in different methods located in j01.jsonrpc.js. You can
    // configure if this method get called in any j01.jsonrpc.jsm j01.dialog.js
    // method based on the isPushState argument. You can also force or skip
    // this state handling based on the page and form HistoryStateMixin class
    // located in j01/jsonrpc/__init__.py
    // Note: this method does not process non jsonrpc request/response. This
    // will get handled by the browser itself without the browser.history api.
    if (typeof(history.pushState) !== 'undefined') {
        // only if pushState is provided
        var state = null;
        if (typeof(response.state) !== 'undefined' && response.state) {
            // success response with state information
            state = response.state;
        }
        else if (typeof(response.data) !== 'undefined' &&
            typeof(response.data.state) !== 'undefined' &&
            response.data.state) {
            // error response with state information
            state = response.data.state;
        }
        if (state) {
            // only if state is given, otherwise ignore
            // apply timestamp to state data
            state.timestamp = new Date().getTime();
            // push state with given url and title
            history.pushState(state, state.title, state.url);
        }
    }
}

function j01PopState(e) {
    // load content based on history state
    var state = history.state || (e && e.state);
    if (state && state.cbURL) {
        // j01.jsonrpc state processing
        var cbURL = state.cbURL;
        // trigger loading event on body tag
        $(document).trigger('j01.history.loading');
        var method = state.method,
            params = state.params,
            onSuccess = j01GetCallback(state.onSuccess),
            onError = j01GetCallback(state.onError),
            onTimeout = j01GetCallback(state.onTimeout, null),
            // add skip push state marker and make sure we don't add the
            // loaded content reponse as a new history entry. Otherwise we
            // whould need two clicks for get back in the history for the
            // previous page
            isPushState = false,
            id = 'j01PopState';
        // ensure default method
        if (typeof(method) !== 'string') {
            method = 'j01LoadContent';
        }
        // get optional params
        if (params == null) {
            // get the params from the url, you can force not to get them from
            // the url by use an empty array (dict) as state.params in your
            // response. But most the time the url params are what we need
            // and get used because the detfault state.params is null (None)
            params = j01URLToArray(cbURL);
        }
        // process state
        proxy = getJSONRPCProxy(cbURL);
        proxy.addMethod(method, onSuccess, onError, onTimeout, isPushState, id);
        if (params) {
            proxy[method](params);
        } else {
            proxy[method]();
        }
    }
    else if (state && state.url) {
        // initial state, see below
        window.location.href = state.url;
    }
}

// add popstate handler
(function(window, undefined) {
    // condition
    if (typeof history.pushState != 'undefined') {
        window.addEventListener("popstate", j01PopState, false);
    }
})(window);


// store the initial state so we can revisit it later
$(document).ready(function(){
    // condition
    if (typeof history.replaceState != 'undefined') {
        var state = {
            url: window.location.href,
            title: document.title,
            timestamp: (new Date().getTime())
        }
        history.replaceState(state, document.title, window.location.href);
    }
});
