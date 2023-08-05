//----------------------------------------------------------------------------
/**
 * @fileoverview Cross browser XMLHttpRequest implementation
 * Make sure the response set the Header to 'no-cache'.
 *
 * @author Roger Ineichen dev at projekt01 dot ch
 * @version 1.0.1
 *
 * changes compared with z3c.xmlhttp and z3c.jsonrpcproxy:
 *
 * - removed username, password
 * - support getMethod for apply readyState handler per json-rpc method
 * - use application/json-rpc as default content-type
 *   (this allows us to use the jsonrpc server only for this content-type
 *    and using the default http server for application/json)
 * - support handleErrors method for non 200 status err response
 *   per method including alert as default handler and supporting nextURL for
 *   unauthorized error view
 * - removed callbackArgs
 * - use json2 stringify instead of own converter methods
 */
//----------------------------------------------------------------------------

//----------------------------------------------------------------------------
// public API
//----------------------------------------------------------------------------

/**
 * Construct a new XMLHttp.
 * @class This is the basic XMLHttp class.
 * @constructor
 * @param {string} url URL pointing to the server
 * @return A new XMLHttp
 */
function XMLHttp(url) {
    this.url = url;
    this.method = 'GET';
    this.async = false;
    this.timeout = null;
    this.argString = "";
    this.parameters = new Array();
    this.headers = new Array();
    this.headers['Content-Type'] = 'application/x-www-form-urlencoded'

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
    this.onComplete = null;      // if readyState 4
    this.onError = null;         // if readyState 4 and status != 200
    this.onTimeout = null;       // if timeout reached
    this.callback = null;        // if readyState 4 and status == 200

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

/**
 * Process a 'POST' request.
 * @param {function} callback callback funtion
 */
XMLHttp.prototype.post = function(callback) {
    this.method = 'POST';
    this.async = false;
    if (typeof(callback)=="function") {
        this.callback = callback;
        this.async = true
    }
    if (this.async) {
        this.process();
    }
    else {
        return this.process();
    }
}

/**
 * Process a 'GET' request.
 * @param {function} callback callback funtion
 */
XMLHttp.prototype.get = function(callback) {
    this.method = 'GET';
    this.async = false;
    if (typeof(callback)=="function") {
        this.callback = callback;
        this.async = true
    }
    if (this.async) {
        this.process();
    }
    else {
        return this.process();
    }
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
        if (typeof(this.xmlhttp.setRequestHeader)!="undefined" && this.xmlhttp.readyState == 1) {
            for (var i in this.headers) {
                this.xmlhttp.setRequestHeader(i, this.headers[i]);
            }
        }
        if (this.timeout > 0) {
            setTimeout(this._doTimeout, this.timeout);
        }
        this.xmlhttp.send(args);
    }
    catch(z) { return false; }
    /* on async call we return false and on sync calls we return the xmlhttp request */
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
    if (typeof(self.onLoading)=="function") {
        self.onLoading(self.xmlhttp);
        }
    self.isLoading = true;
}

/** @private */
XMLHttp.prototype._doLoaded = function(self) {
    if (self.isLoaded) { return; }
    if (typeof(self.onLoaded)=="function") {
        self.onLoaded(self.xmlhttp);
    }
    self.isLoaded = true;
}

/** @private */
XMLHttp.prototype._doInteractive = function(self) {
    if (self.isInteractive) { return; }
    if (typeof(self.onInteractive)=="function") {
        self.onInteractive(self.xmlhttp);
    }
    self.isInteractive = true;
}

/** @private */
XMLHttp.prototype._doComplete = function(self) {
    if (self.isComplete || self.isAborted) { return; }
    self.isComplete = true;
    self.status = self.xmlhttp.status;
    self.statusText = self.xmlhttp.statusText;
    self.responseText = self.xmlhttp.responseText;
    self.responseXML = self.xmlhttp.responseXML;
    if (self.xmlhttp.status==200 && typeof(self.callback)=="function") {
        self.callback(self.xmlhttp);
    }
    else if (self.xmlhttp.status==200 && typeof(self.onComplete)=="function") {
        self.onComplete(self.xmlhttp);
    }
    else if (self.xmlhttp.status!=200 && typeof(self.onError)=="function") {
        self.onError(self.xmlhttp);
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
    if (self.xmlhttp!=null && !self.isComplete) {
        self.xmlhttp.abort();
        self.isAborted = true;
        if (typeof(self.onTimeout)=="function") {
            self.onTimeout(self.xmlhttp);
        }
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
 * @version 0.5.0 supports JSON-RPC 1.0, 1.1 and 2.0
 *
 * usage:
 *
 * var myProxy = getJSONRPCProxy('getSomething', renderResult);
 * myProxy.getSomething();
 *
 * var addToTable = function(response) {
 *     // just return {'content': 'something'} in your z3c.jsonrpc method,
 *     // everything else is implicit added by the z3c.jsonrpc implementation
 *     // and the response will provide your content attr/value as
 *     // respone.content
 *     $('#myTarget').append(response.content);
 * }
 * var myProxy = getJSONRPCProxy('addPerson', addToTable);
 * data = {'firstName': 'Roger, 'lastName': 'Ineichen'}
 * myProxy.addPerson(data);
 *
 */
//----------------------------------------------------------------------------

function JSONRPC(url, version) {
    this._url = url;
    // uses specification version 2.0 by default
    this._version = '2.0'
    if (typeof(version) != 'undefined') {
        this._version = version;
    }
    this._methods = new Array();
}

function getJSONRPCProxy(url, version) {
    return new JSONRPC(url, version);
}

JSONRPC.prototype.addMethod = function(name, callback, requestId, onError, isPushState) {
    if (typeof(requestId) == 'undefined') {
        requestId = "jsonRequest";
    }
    var self = this;
    if(!self[name]){
        var method = new JSONRPCMethod(self, this._url, name, callback, requestId, this._version, onError, isPushState);
        self[name] = method;
    }
}

JSONRPC.prototype.getMethod = function(methodName) {
    var self = this;
    for (var i in self._methods) {
        if (methodName === self._methods[i].methodName) {
            return self._methods[i];
        }
    }
}

function JSONRPCMethod(proxy, url, methodName, callback, requestId, version, handleErrors, isPushState) {
    this.methodName = methodName;
    this.callback = callback;
    this.requestId = requestId;
    this.url = url;
    this.version = version;
    this.handleErrors = handleErrors;
    this.isPushState = isPushState;

    // keep reference to method and support getMethod for apply on*
    // (state change) handler
    var self = this;
    proxy._methods.push(self);

    var fn = function(){
        // setup and return callable function
        var oldVersion = false;
        if (self.version == '1.0' || self.version == '1.1') {
            oldVersion = true;
        }
        if (!oldVersion && arguments.length == 1 && typeof arguments[0] === "object"){
            // we've got version 2.0 and an associative array as argument
            var args = arguments[0];
        } else {
            // we've got positional arguments
            var args = new Array();
            for(var i=0;i<arguments.length;i++){
                args.push(arguments[i]);
            }
        }
        if(self.callback) {
            // process async callback
            var data = self.jsonRequest(self.requestId, self.methodName, args);
            self.postData(self.url, data, function(resp){
                try {
                    // handle response
                    var res = self.handleResponse(resp);
                    self.callback(res, self.isPushState);
                } catch (e){}
                args = null;
                resp = null;
            });
        } else {
            // process sync response
            var data = self.jsonRequest(self.requestId, self.methodName, args);
            var resp = self.postData(self.url, data);
            return self.handleResponse(resp);
        }
    }
    return fn;
}

JSONRPCMethod.prototype._doHandleErrors = function(resp) {
    // handle non status 200 errors
    if (typeof(self.handleErrors) == "function") {
        self.handleErrors(resp);
    }
    else if (resp.data && resp.data.nextURL) {
        // support j01.jsonrpc unautorized nextURL handling
        window.location.href = resp.data.nextURL;
    } else {
        // by default, alert jsonrpc server error message from response
        alert("callback method error: " + resp.message); // p01.checker.silence
    }
}

JSONRPCMethod.prototype.postData = function(url, data, callback) {
    var xmlhttp = new XMLHttp(url);
    xmlhttp.onLoading = self.onLoading;
    xmlhttp.onLoaded = self.onLoaded;
    xmlhttp.onInteractive = self.onInteractive;
    xmlhttp.onComplete = self.onComplete;
    xmlhttp.onError = self.onError;
    xmlhttp.onTimeout = self.onTimeout;
    var header = new Array()
    header["Content-Type"] = "application/json-rpc";
    xmlhttp.setHeaders(header);
    xmlhttp.argString = data;
    if(callback == null){
        return xmlhttp.post();
    }else{
        xmlhttp.post(callback);
    }
}

JSONRPCMethod.prototype.jsonRequest = function(id, methodName, args){
    // all version (including 1.0)
    var data = {
        "id": id,
        "method": methodName,
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
        // fallback to toJSON
        return toJSON(data);
    }
}


JSONRPCMethod.prototype.notify = function(){
    var args=new Array();
    for(var i=0;i<arguments.length;i++){
        args.push(arguments[i]);
    }
    var data = this.jsonRequest(null, this.methodName, args);
    this.postData(this.url, data, function(resp){});
}

JSONRPCMethod.prototype.handleResponse = function(resp){
    // TODO: Implement better error handling support since we have error codes
    // offer an argument xmlhttp.onError which defines a function for custom
    // error handling.
    var status = null;
    try {
        status = resp.status;
    } catch(e){}
    if(status == 200){
        var respTxt = "";
        try {
            respTxt = resp.responseText;
        }catch(e){}
        if(respTxt == null || respTxt == ""){
            alert("The server responded with an empty document."); // p01.checker.silence
        } else {
            var res = this.unmarshall(respTxt);
            if(res.error != null){
                return res.error
            }
            else if (res.id != this.requestId) {
                alert("Wrong json id returned."); // p01.checker.silence
            }
            else {
                return res.result;
            }
        }
    }else{
        // handle none status 200 errors
        this._doHandleErrors(resp);
    }
}

JSONRPCMethod.prototype.unmarshall = function(source){
    // unmarshalling given response. NOTE, this includes executing included
    // javascript code
    try {
        if (window.JSON) {
            return JSON.parse(source);
        }
        else{
            // fallback to eval
            var obj;
            eval("obj=" + source);
            return obj;
        }
    }catch(e){
        alert("The server's response could not be parsed."); // p01.checker.silence
    }
}

function escapeJSONChar(c) {
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

function escapeJSONString(s) {
    var parts = s.split("");
    for(var i=0; i < parts.length; i++) {
    var c =parts[i];
    if(c == '"' ||
       c == '\\' ||
       c.charCodeAt(0) < 32 ||
       c.charCodeAt(0) >= 128)
        parts[i] = escapeJSONChar(parts[i]);
    }
    return "\"" + parts.join("") + "\"";
}

function toJSON(o) {
    if(o == null) {
        return "null";
    } else if(o.constructor == String) {
        return escapeJSONString(o);
    } else if(o.constructor == Number) {
        return o.toString();
    } else if(o.constructor == Boolean) {
        return o.toString();
    } else if(o.constructor == Date) {
        return o.valueOf().toString();
    } else if(o.constructor == Array) {
        var v = [];
        for(var i = 0; i < o.length; i++) v.push(toJSON(o[i]));
        return "[" + v.join(", ") + "]";
    }
    else {
        var v = [];
        for(attr in o) {
            if(o[attr] == null) v.push("\"" + attr + "\": null");
            else if(typeof o[attr] == "function"); // skip
            else v.push(escapeJSONString(attr) + ": " + toJSON(o[attr]));
        }
        return "{" + v.join(", ") + "}";
    }
}
