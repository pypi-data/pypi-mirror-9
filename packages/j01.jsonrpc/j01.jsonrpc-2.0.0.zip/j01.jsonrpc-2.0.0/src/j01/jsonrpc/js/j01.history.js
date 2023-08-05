// -----------------------------------------------------------------------------
// j01.jsonrpc.js browser history support
// -----------------------------------------------------------------------------
/* We provide the browser history concept out of the box without any special
 * configuration. This means we will pushState after the content get loaded and
 * the content get applied to the right place in the page. We do not apply
 * anything if an error get handled. You can simple change this pushState
 * hanlding concept in your own custom content handling methods.
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
    // push data given from response to history state
    if (typeof history.pushState != 'undefined' &&
        typeof response.skipState != 'undefined' && !response.skipState &&
        response.url) {
        // only if pushState is provided and marked with skipState=false and
        // page url is given, otherwise ignore. Note a missing skipState will
        // also prevent apply the state to the history!
        var url = response.url;
        var stateURL = response.stateURL;
        var title = response.stateTitle;
        var state = {
            url: url,
            title: title,
            callbackName: response.stateCallbackName,
            timestamp: (new Date().getTime())
        }
        history.pushState(state, title, stateURL);
    }
}

function j01PopState(e) {
    // load content based on history state
    var state = history.state || (e && e.state);
    if(state && state.url) {
        var url = state.url;
        if (url && state.callbackName) {
            // trigger loading event on body tag
            $(document).trigger('j01.jsonrpc.loading');
            var onSuccess = j01GetCallback(state.callbackName);
            var onError = null;
            var onTimeout = null;
            var isPushState = false;
            var id = 'j01LoadContent';
            proxy = getJSONRPCProxy(url);
            proxy.addMethod('j01LoadContent', onSuccess, onError, onTimeout,
                isPushState, id);
            var params = j01URLToArray(url);
            if (params) {
                proxy.j01LoadContent(params);
            } else {
                proxy.j01LoadContent();
            }
        } else if (url){
            // initial content
            window.location.href = url;
        }
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
            callbackName: null,
            timestamp: (new Date().getTime())
        }
        history.replaceState(state, document.title, window.location.href);
    }
});
