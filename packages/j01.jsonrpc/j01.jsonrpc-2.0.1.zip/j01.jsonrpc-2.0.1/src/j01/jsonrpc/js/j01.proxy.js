//----------------------------------------------------------------------------
/**
 * @fileoverview Cross browser XMLHttpRequest implementation
 * Make sure the response set the Header to 'no-cache'.
 *
 * @author Roger Ineichen dev at projekt01 dot ch
 * @version 2.0.0
 *
 * changes compared with z3c.xmlhttp and z3c.jsonrpcproxy:
 *
 * - support application/json-rpc as default content-type for getJSONRPCProxy
 * - support application/json as default content-type for getJSONProxy
 *   (this allows us to use the jsonrpc server only for this content-type
 *    and using the default http server for application/json)
 * - support optional onError method for non 200 status err response
 * - support optional onTimeout method
 * - support getMethod for apply readyState handler per json-rpc method
 * - support jsonrpc server unauthorized error view support using a
 *   data.nextURL property as redirect value for unauthorized calls
 * - use json2 stringify instead of own converter methods by default
 * - trigger j01.proxy.error JQuery event on error
 * - removed username, password credentials
 * - removed callbackArgs
 */
//----------------------------------------------------------------------------

//----------------------------------------------------------------------------
// public API
//----------------------------------------------------------------------------

var j01XHRId = 0
var j01XMLHttpReferences = {}

// Support: IE<10, open requests must be manually aborted on unload
if (window.ActiveXObject) {
    jQuery(window).on("unload", function() {
        for (var key in j01XMLHttpReferences) {
            var xhr = j01XMLHttpReferences[key];
            delete j01XMLHttpReferences[key];
            xhr.onUnload();
        }
    });
}

/**
 * Construct a new XMLHttp.
 * @class This is the basic XMLHttp class.
 * @constructor
 * @param {string} url URL pointing to the server
 * @return A new XMLHttp
 */
function XMLHttp(url) {
    this.id = ++j01XHRId;
    j01XMLHttpReferences[this.id] = this;
    this.url = url;
    this.method = 'GET';
    this.async = false;
    this.timeout = null;
    this.argString = "";
    this.parameters = new Array();
    this.headers = new Array();
    this.contentType = 'application/x-www-form-urlencoded';

    /* internal status flags */
    this.isAborted = false;
    this.isLoading = false;
    this.isLoaded = false;
    this.isInteractive = false;
    this.isComplete = false;

    /* event handlers (attached functions get called if readyState reached) */
    this.onLoading = null;       // if readyState 1
    this.onLoaded = null;        // if readyState 2
    this.onInteractive = null;   // if readyState 3
    this.onCallback = null;      // if readyState 4
    this.onTimeout = null;       // if timeout reached

    /*  response variables */
    this.responseText = null;
    this.responseXML = null;

    /* setup the xmlhttp request now */
    this.xmlhttp = getXmlHttpRequest()
}

/**
 * Set the header information for the XMLHttp instance.
 * @param {array} args of key, value
 */
XMLHttp.prototype.setHeaders = function(args) {
    for (var i in args) {
        this.headers[i] = args[i];
    }
}

/**
 * Set the arguments for the request or the XMLHttp instance.
 * @param {array} args of key, value
 */
XMLHttp.prototype.setArguments = function(args) {
    for (var i in args) {
        // set parameter to the xmlhttp instance or to the parameter array
        if (typeof(this[i])=="undefined") {
            this.parameters[i] = args[i];
        }
        else {
            this[i] = args[i];
        }
    }
}

// /**
//  * Process a 'POST' request.
//  * @param {function} callback callback funtion
//  */
// XMLHttp.prototype.post = function(onCallback) {
//     this.method = 'POST';
//     this.async = false;
//     if (typeof(onCallback) === "function") {
//         this.onCallback = onCallback;
//         this.async = true
//         this.process();
//     }
//     else {
//         return this.process();
//     }
// }

// /**
//  * Process a 'GET' request.
//  * @param {function} callback callback funtion
//  */
// XMLHttp.prototype.get = function(onCallback) {
//     this.method = 'GET';
//     this.async = false;
//     if (typeof(onCallback) === "function") {
//         this.onCallback = onCallback;
//         this.async = true
//         this.process();
//     }
//     else {
//         return this.process();
//     }
// }

/**
 * Process a 'POST' request.
 * @param {function} callback callback funtion
 */
XMLHttp.prototype.post = function() {
    this.method = 'POST';
    if (typeof(this.onCallback) === "function") {
        this.async = true
    }else{
        this.async = false;
    }
    return this.process();
}


/**
 * Process a 'GET' request.
 * @param {function} callback callback funtion
 */
XMLHttp.prototype.get = function() {
    this.method = 'GET';
    if (typeof(this.onCallback) === "function") {
        this.async = true
    }else{
        this.async = false;
    }
    return this.process();
}


//----------------------------------------------------------------------------
// helper methods (can be used directly if you need enhanced access, but the
// method post and get are the prefered methods for processing a request.)
//----------------------------------------------------------------------------

/** @private */
XMLHttp.prototype.process = function() {
    if (!this.xmlhttp) {
        return false;
    }
    var self = this;
    this.xmlhttp.onreadystatechange = function() {
        if (self.xmlhttp == null) { return; }
        if (self.xmlhttp.readyState == 1) { self._doLoading(self); }
        if (self.xmlhttp.readyState == 2) { self._doLoaded(self); }
        if (self.xmlhttp.readyState == 3) { self._doInteractive(self); }
        if (self.xmlhttp.readyState == 4) { self._doComplete(self); }
    };

    try {
        var args = null;
        for ( var i = 0; i < this.parameters.length; i++ ) {
            if (this.argString.length>0) {
                this.argString += "&";
            }
            this.argString += encodeURIComponent(i) + "=" + encodeURIComponent(this.parameters[i]);
        }
        if (this.method == "GET") {
            if (this.argString.length>0) {
                this.url += ((this.url.indexOf("?")>-1)?"&":"?") + this.argString;
            }
            this.xmlhttp.open(this.method, this.url, this.async);
        }
        if (this.method == "POST") {
            this.xmlhttp.open(this.method, this.url, this.async);
            args = this.argString;
        }
        if (typeof(this.xmlhttp.setRequestHeader) !== "undefined" &&
            this.xmlhttp.readyState === 1) {
            this.xmlhttp.setRequestHeader("Content-Type", this.contentType);
            for (var i in this.headers) {
                if ( headers[ i ] !== undefined ) {
                    this.xmlhttp.setRequestHeader(i, this.headers[i] + "");
                }
            }
        }
        if (this.timeout > 0) {
            function cbTimeout(){
                self._doTimeout(self);
            }
            setTimeout(cbTimeout, this.timeout);
        }
        this.xmlhttp.send(args);
    }
    catch(e) {
        return false;
    }
    // on async call we return false and on sync calls we return the xmlhttp
    // request
    if (this.async) {
        return false;
    }
    else {
        return this.xmlhttp;
    }
}



//----------------------------------------------------------------------------
// helper methods (can be used as a standalone cross browser xmlhttp request)
//----------------------------------------------------------------------------

/**
 * Global helper function for a cross browser XMLHttpRequest object.
 * @class This is a global helper function for a cross browser XMLHttpRequest object.
 * @constructor
 * @return A XMLHttpRequest instance for gecko browsers and a ActiveXObjecct
 * for ie browsers. Unsuported browsers get null returned.
 */
getXmlHttpRequest = function() {
    if (window.XMLHttpRequest) {
        var req = new XMLHttpRequest();
        // some older versions of Moz did not support the readyState property
        // and the onreadystate event so we patch it!
        if (req.readyState == null) {
            req.readyState = 1;
            req.addEventListener("load", function () {
                req.readyState = 4;
                if (typeof req.onreadystatechange == "function") {
                    req.onreadystatechange();
                }
            }, false);
        }
        return req;
    }
    // see comments about the MSXML2.XMLHTTP order,
    // http://blogs.msdn.com/b/xmlteam/archive/2006/10/23/
    // using-the-right-version-of-msxml-in-internet-explorer.aspx
    else if (window.ActiveXObject) {
        var MSXML_XMLHTTP_IDS = new Array(
            "MSXML2.XMLHTTP.6.0",
            "MSXML2.XMLHTTP.3.0",
            "MSXML2.XMLHTTP",
            "MSXML2.XMLHTTP.5.0",
            "MSXML2.XMLHTTP.4.0",
            "Microsoft.XMLHTTP");
        var success = false;
        for (var i = 0; i < MSXML_XMLHTTP_IDS.length && !success; i++) {
            try {
                return new ActiveXObject(MSXML_XMLHTTP_IDS[i]);
                success = true;
            } catch (e) {}
        }
    }
    else {
        return null;
    }
}


//----------------------------------------------------------------------------
// built in helper methods
//----------------------------------------------------------------------------

/** @private */
XMLHttp.prototype._doLoading = function(self) {
    if (self.isLoading) { return; }
    if (typeof(self.onLoading) === 'function') {
        self.onLoading(self.xmlhttp);
        }
    self.isLoading = true;
}

/** @private */
XMLHttp.prototype._doLoaded = function(self) {
    if (self.isLoaded) { return; }
    if (typeof(self.onLoaded) === 'function') {
        self.onLoaded(self.xmlhttp);
    }
    self.isLoaded = true;
}

/** @private */
XMLHttp.prototype._doInteractive = function(self) {
    if (self.isInteractive) { return; }
    if (typeof(self.onInteractive) === 'function') {
        self.onInteractive(self.xmlhttp);
    }
    self.isInteractive = true;
}

/** @private */
// Note, if a CORS request fails there is no handling for that
XMLHttp.prototype._doComplete = function(self) {
    if (self.isComplete || self.isAborted) {
        return;
    }
    // remove xmlhttp unload reference
    delete j01XMLHttpReferences[self.id]
    self.isComplete = true;
    self.status = self.xmlhttp.status;
    // IE sometimes returns 1223 when it should be 204
    if (self.status === 1223) {
        self.status = 204;
    }
    // Firefox throws an exception when accessing
    // statusText for faulty cross-domain requests
    try {
        self.statusText = self.xmlhttp.statusText;
    } catch( e ) {
        // We normalize with Webkit giving an empty statusText
        self.statusText = "";
    }
    // Support: IE<10, Accessing binary-data responseText throws an exception
    if (typeof self.xmlhttp.responseText === "string") {
        self.responseText = self.xmlhttp.responseText;
    }else {
        self.responseText = "";
    }
    self.responseXML = self.xmlhttp.responseXML;
    if (typeof(self.onCallback) === "function") {
        self.onCallback(self.xmlhttp);
    }
    // on async calls, clean up so IE doesn't leak memory
    if (self.async) {
        try {
             delete self.xmlhttp['onreadystatechange'];
        }
        catch (e) {}
        self.xmlhttp = null;
    }
}

/** @private */
XMLHttp.prototype._doTimeout = function(self) {
    if (self.xmlhttp !== null && !self.isComplete) {
        self.xmlhttp.abort();
        self.isAborted = true;
        if (typeof(self.onTimeout) === "function") {
            // process custom timeout
            self.onTimeout(self);
        }else{
            $(document).trigger({
                type: 'j01.proxy.timeout',
                xmlhttp: self
            });
        }
        // Opera won't fire onreadystatechange after abort, but other browsers
        // do. So we can't rely on the onreadystate function getting called.
        // clean up here!
        try {
            delete self.xmlhttp['onreadystatechange'];
        }catch(e){}
        self.xmlhttp = null;
    }
}

/** @private */
XMLHttp.prototype.onUnload = function(self) {
    if (self.xmlhttp != null && !self.isComplete) {
        self.xmlhttp.abort();
        self.isAborted = true;
    // Opera won't fire onreadystatechange after abort, but other browsers do.
    // So we can't rely on the onreadystate function getting called.
    // Clean up here!
    try {
        delete self.xmlhttp['onreadystatechange'];
    }catch(e){}
    self.xmlhttp = null;
    }
}

//----------------------------------------------------------------------------
/**
 * @fileoverview JSON-RPC client implementation
 * @author Roger Ineichen dev at projekt01 dot ch
 * @version 2.0.0 supports JSON-RPC 1.0, 1.1 and 2.0
 *
 * usage:
 *
 * var proxy = getJSONRPCProxy(url);
 * proxy.addMethod('getSomething', renderResult);
 * proxy.getSomething();
 *
 * var addToTable = function(response) {
 *     // just return {'content': 'something'} in your z3c.jsonrpc method,
 *     // everything else is implicit added by the z3c.jsonrpc implementation
 *     // and the response will provide your content attr/value as
 *     // respone.content
 *     $('#myTarget').append(response.content);
 * }
 * var onError = function(error){// do something}
 * var onTimeout = function(xhr){// do something}
 * var isPushState = true;
 * var id = 'my-request';
 * var proxy = getJSONRPCProxy(url);
 * proxy.addMethod('addPerson', addToTable, onError, onTimeout, isPushState, id);
 * data = {'firstName': 'Roger, 'lastName': 'Ineichen'}
 * proxy.addPerson(data);
 *
 * or you can manipulate a method with:
 *
 * var proxy = getJSONRPCProxy(url);
 * proxy.addMethod('addPerson', addToTable);
 * method = proxy.getMethod('addPerson');
 * method.version = '1.1';
 * method.onTimeout = function(xhr){// do something};
 * method.isPushState = true;
 * data = {'firstName': 'Roger, 'lastName': 'Ineichen'}
 * proxy.addPerson(data);
 *
 */
//----------------------------------------------------------------------------

function JSONRPC(url, options) {
    options = $.extend({
        version: '2.0',
        contentType: 'application/json-rpc',
        timeout: null
    }, options);
    this._methods = new Array();
    this._url = url;
    this._version = options.version;
    this._timeout = options.timeout;
}

function getJSONRPCProxy(url, version, timeout) {
    return new JSONRPC(url, {
        version: version,
        timeout: timeout
    });
}

function getJSONProxy(url, version, timeout) {
    return new JSONRPC(url, {
        version: version,
        contentType: 'application/json',
        timeout: timeout
    });
}

JSONRPC.prototype.addMethod = function(name, onSuccess, onError, onTimeout,
    isPushState, id) {
    var self = this;
    if (typeof self[name] !== "undefined") {
        // we will call the JSONRPCMethod as JSONRPC.<name>. This doens't
        // allow to use internal JSONRPC method names as JSONRPCMethod names
        throw "Forbidden name '" +name+ "'used in j01.proxy.js addMethod"
    }
    if (typeof self._methods[name] !== "undefined") {
        // method already used
        throw "Method name '" +name+ "'already used in j01.proxy.js addMethod"
    }else{
        var method = new JSONRPCMethod(self, self._url, name, onSuccess,
            onError, onTimeout, isPushState, id);
        method.timeout = self._timeout
        method.version = this._version
        method.contentType = this.contentType;
        self[name] = method.__call__;
        // return method, this can be used for apply additional hooks if needed
        return method;
    }
}

JSONRPC.prototype.getMethod = function(name) {
    // returns JSONRPCMethod which is callable as method.__call__
    var self = this;
    for (var i in self._methods) {
        if (name === self._methods[i].name) {
            return self._methods[i];
        }
    }
}

var JSONRPCMethod = function (proxy, url, name, onSuccess, onError, onTimeout,
    isPushState, id) {
    if (typeof(onError) === 'undefined') {
        onError = null;
    }
    if (typeof(onTimeout) === 'undefined') {
        onTimeout = null;
    }
    if (typeof(isPushState) === 'undefined') {
        isPushState = null;
    }
    if (typeof(id) === 'undefined') {
        id = "j01";
    }
    // given from setup
    this.timeout = proxy.timeout;
    this.url = url;
    this.name = name;
    this.onSuccess = onSuccess;
    this.onError = onError;
    this.onTimeout = onTimeout;
    this.isPushState = isPushState;
    this.id = id;
    // defaults, change this after method get created if needed
    this.onException = null
    this.onLoading = null;
    this.onLoaded = null;
    this.onInteractive = null;
    // we use the response.result and response.error as callback argument
    // this can make it almost impossible to find out if the response was
    // success or an error if you use the same method for onSuccess and onError
    // Just set the useFullResponse to true if you need to get the full
    // response and not just result or error data in your response callback
    this.useFullResponse = false;
    // allows to redirect on error
    this.skipNextURLOnError = false;
    // default values will get overriden by addMethod based on JSONRPC setup
    this.version = '2.0';
    this.contentType = "application/json-rpc";

    // keep reference to method and support getMethod for apply on*
    // (state change) handler
    var self = this;
    proxy._methods[name] = self;
    var fn = function(){
        // setup and return callable function
        var oldVersion = false;
        if (self.version == '1.0' || self.version == '1.1') {
            oldVersion = true;
        }
        if (!oldVersion && arguments.length == 1 &&
            typeof arguments[0] === "object"){
            // we've got version 2.0 and an associative array as argument
            var args = arguments[0];
        } else {
            // we've got positional arguments
            var args = new Array();
            for(var i=0;i<arguments.length;i++){
                args.push(arguments[i]);
            }
        }
        if (typeof(self.onSuccess) === "function") {
            // process async success callback
            var data = self.getRequestData(self.id, self.name, args);
            var onCallback = function(xhr){
                var resp = self.getResponseData(xhr);
                try {
                    if(resp && xhr.status == 200){
                        // handle success or error response
                        self.doHandleResponse(resp);
                    }else{
                    // handle non status 200 exception
                        self.doHandleException(resp);
                    }
                } catch(e){
                    // error doesn't provide response data
                }
                args = null;
                xhr = null;
            }
            self.postData(self.url, data, onCallback);
        } else {
            // process sync response
            var data = self.getRequestData(self.id, self.name, args);
            var xhr = self.postData(self.url, data);
            var resp = self.getResponseData(xhr);
            try {
                if(resp && xhr.status == 200){
                    // return success or error response
                    // Note: we do not apply the isPushState to the result or
                    // error because this is not async and you can handle this
                    // in your own javascript code.
                    return self.doHandleDirectResponse(resp);
                }else{
                    // handle non status 200 exception
                    self.doHandleException(resp);
                }
            } catch(e){
                // error doesn't provide response data
            }
            args = null;
            xhr = null;
        }
    }
    // return method with __call__ hook
    return {
        __call__: fn
    }
}

JSONRPCMethod.prototype.getResponseData = function(xhr){
    // returns server response or None on exception
    var source = "";
    try {
        // Firefox throws an exception when accessing
        // statusText for faulty cross-domain requests
        source = xhr.responseText;
    }catch(e){}
    try {
        // unmarshalling given response including javascript code execution
        if (source !== null && source !== "") {
            if (window.JSON) {
                var data = JSON.parse(source);
            }
            else{
                // fallback to eval
                var obj;
                eval("obj=" + source);
                var data = obj;
            }
            if (data && data.id == this.id) {
                return data;
            }
        }
    }catch(e){}
    // doHandleException will handle or trigger j01.jsonrpc.exception
    return null;
}

JSONRPCMethod.prototype.doHandleSuccess = function(resp) {
    // handle status 200 succes response
    // apply isPushState marker to result (response) if not given
    // in response and given from calling method
    if (typeof resp.result.isPushState === 'undefined') {
        resp.result.isPushState = this.isPushState
    }
    // async calling onSuccess
    if (this.useFullResponse) {
        // use the full response as data
        this.onSuccess(resp);
    }else{
        // by default we use response.result as data
        this.onSuccess(resp.result);
    }
}

JSONRPCMethod.prototype.doHandleError = function(resp) {
    // handle status 200 error response
    // non status 200 error handler
    // Note: response could be none on connection error
    if (typeof(this.onError) === 'function') {
        // custom error handler method given
        if (typeof resp.error.isPushState === 'undefined') {
            // apply isPushState marker to error
            resp.error.isPushState = this.isPushState;
        }
        if (this.useFullResponse) {
            // use the full response as data
            this.onError(resp);
        }else{
            // by default we use response.error as data
            this.onError(resp.error);
        }
    }
    else if (resp.error.data && resp.error.data.nextURL &&
        !this.skipNextURLOnError) {
        // support j01.jsonrpc unautorized data.nextURL handling
        // use a custom onError handler if you like to skip implicit
        // Unauthorized error redirect handling
        window.location.href = resp.error.data.nextURL;
    } else {
        // by default, trigger 'j01.proxy.error' event
        $(document).trigger({
            type: 'j01.proxy.error',
            method: this.name,
            msg: 'Server Error',
            error: resp.error,
            isPushState: this.isPushState
        });
    }
}

JSONRPCMethod.prototype.doHandleResponse = function(resp) {
    // handle status 200 response, dispatch to onSucces or onError
    // this works for jsonrpc response version 1.0, 1.1 and 2.0
    if (typeof(resp) === 'undefined') {
        this.doHandleException();
    }
    else if (typeof(resp.result) !== 'undefined') {
        this.doHandleSuccess(resp);
    }
    else if (typeof(resp.error) !== 'undefined') {
        this.doHandleError(resp);
    }else{
        this.doHandleException(resp);
    }
}

JSONRPCMethod.prototype.doHandleDirectResponse = function(resp) {
    // non async response processing. Note: we do not return an error
    // repsonse for any use case.
    // handle status 200 response, return success, error ro full response
    // this works for jsonrpc response version 1.0, 1.1 and 2.0
    if (typeof(resp) === 'undefined') {
        this.doHandleException();
    }
    else if (typeof(resp.result) !== 'undefined') {
        // success
        if (typeof resp.result.isPushState === 'undefined') {
            resp.result.isPushState = this.isPushState
        }
        // async calling onSuccess
        if (this.useFullResponse) {
            // use the full response as data
            return resp;
        }else{
            // by default we use response.result as data
            return resp.result;
        }
    }
    else if (typeof(resp.error) !== 'undefined') {
        if (typeof(this.onError) === 'function') {
            // custom error handler method given
            if (typeof resp.error.isPushState === 'undefined') {
                // apply isPushState marker to error
                resp.error.isPushState = this.isPushState;
            }
            if (this.useFullResponse) {
                // use the full response as data
                this.onError(resp);
            }else{
                // by default we use response.error as data
                this.onError(resp.error);
            }
        }
        else if (resp.error.data && resp.error.data.nextURL &&
            !this.skipNextURLOnError) {
            // support j01.jsonrpc unautorized data.nextURL handling
            // use a custom onError handler if you like to skip implicit
            // Unauthorized error redirect handling
            window.location.href = resp.error.data.nextURL;
        } else if (this.useFullResponse) {
            // if useFullRepsonse is used, we return the repsone.
            return resp;
        } else {
            // if  not useFullRepsonse is used, we return the repsone.
            return resp.error;
        }
    }else{
        this.doHandleException(resp);
    }
}




JSONRPCMethod.prototype.doHandleException = function(resp) {
    // handle NON status 200 response
    // non status 200 error handler
    // Note: response could be none on connection error
    if (typeof(this.onException) === 'function') {
        // custom exception handler method given
        this.onException(resp);
    } else {
        // by default, trigger 'j01.proxy.exception' event
        $(document).trigger({
            type: 'j01.proxy.exception',
            method: this.name,
            msg: 'Server Error',
            resp: resp,
            isPushState: this.isPushState
        });
    }
}

JSONRPCMethod.prototype.postData = function(url, data, onCallback) {
    var xmlhttp = new XMLHttp(url);
    xmlhttp.onLoading = this.onLoading;
    xmlhttp.onLoaded = this.onLoaded;
    xmlhttp.onInteractive = this.onInteractive;
    xmlhttp.onTimeout = this.onTimeout;
    xmlhttp.timeout = this.timeout;
    xmlhttp.contentType = this.contentType;
    xmlhttp.argString = data;
    if (typeof(onCallback) === "function") {
        xmlhttp.onCallback = onCallback;
    }
    return xmlhttp.post();
}


JSONRPCMethod.prototype.notify = function(){
    var args=new Array();
    for(var i=0;i<arguments.length;i++){
        args.push(arguments[i]);
    }
    var data = this.getRequestData(null, this.name, args);
    this.postData(this.url, data, function(xhr){});
}

JSONRPCMethod.prototype.getRequestData = function(id, name, args){
    // all version (including 1.0)
    var data = {
        "id": id,
        "method": name,
        "params": args
    }
    if (this.version == '1.1'){
        // version 1.1
        data.version = this.version;
    }else if (this.version == '2.0'){
        // version 2.0
        data.jsonrpc = this.version;
    }
    if (window.JSON) {
        // use JSON2 for json dump
        return JSON.stringify(data)
    }else{
        // fallback if no JSON2
        return j01ToJSON(data);
    }
}

function j01EscapeJSONChar(c) {
    if(c == "\"" || c == "\\") return "\\" + c;
    else if (c == "\b") return "\\b";
    else if (c == "\f") return "\\f";
    else if (c == "\n") return "\\n";
    else if (c == "\r") return "\\r";
    else if (c == "\t") return "\\t";
    var hex = c.charCodeAt(0).toString(16);
    if(hex.length == 1) return "\\u000" + hex;
    else if(hex.length == 2) return "\\u00" + hex;
    else if(hex.length == 3) return "\\u0" + hex;
    else return "\\u" + hex;
}

function j01EscapeJSONString(s) {
    var parts = s.split("");
    for(var i=0; i < parts.length; i++) {
    var c =parts[i];
    if(c == '"' ||
       c == '\\' ||
       c.charCodeAt(0) < 32 ||
       c.charCodeAt(0) >= 128)
        parts[i] = j01EscapeJSONChar(parts[i]);
    }
    return "\"" + parts.join("") + "\"";
}

function j01ToJSON(o) {
    if(o == null) {
        return "null";
    } else if(o.constructor == String) {
        return j01EscapeJSONString(o);
    } else if(o.constructor == Number) {
        return o.toString();
    } else if(o.constructor == Boolean) {
        return o.toString();
    } else if(o.constructor == Date) {
        return o.valueOf().toString();
    } else if(o.constructor == Array) {
        var v = [];
        for(var i = 0; i < o.length; i++) v.push(j01ToJSON(o[i]));
        return "[" + v.join(", ") + "]";
    }
    else {
        var v = [];
        for(attr in o) {
            if(o[attr] == null) v.push("\"" + attr + "\": null");
            else if(typeof o[attr] == "function"); // skip
            else v.push(j01EscapeJSONString(attr) + ": " + j01ToJSON(o[attr]));
        }
        return "{" + v.join(", ") + "}";
    }
}
