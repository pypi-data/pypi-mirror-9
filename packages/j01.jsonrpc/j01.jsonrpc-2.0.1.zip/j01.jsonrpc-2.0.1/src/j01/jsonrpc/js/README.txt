======
README
======


j01.proxy.js
------------

The j01.proxy.js javascript provides a jsonrpc proxy implementation useing
an XMLHttpRequest for send and receive conten from a jsonrpc server. This is
the base implementation used for our j01.jsonrpc.js library. This libary
uses the browsers built-in JSON support for serialize or deserialze or the
json2 script if provided or falls back to internal methods.


j01.json2.js
------------

This javascript provides a fallback for old browsers if JSON is not supported.

This file creates a JSON property in the global object, if there
isn't already one, setting its value to an object containing a stringify
method and a parse method. The parse method uses the eval method to do the
parsing, guarding it with several regular expressions to defend against
accidental code execution hazards. On current browsers, this file does nothing,
prefering the built-in JSON object. For more information see:
https://github.com/douglascrockford/JSON-js


j01.button.js
-------------

This javascript provides a ``prevent submit a button twice`` concept by disable
the button action. See the button implementation in j01/jsonrpc/btn for more
information.


j01.loading.js
--------------

This javascript provides a loading spinner which can get shown for the time
abutton get submitted and the returned content get rendered. This script is
using the spin.js javascript from Felix Gnass. For mor information see:
http://fgnass.github.io/spin.js/


j01.jsonrpc.js
--------------

The j01.jsonrpc.js provides methods for get content from or post form data
and get the result from a jsonrpc server. The handling is done using the
j01.proxy javascript library.

Usage:

register callback handler:

  function doitFunction(response){
      alert(response.content); // p01.checker.silence
  }
  j01RegisterCallback('doit', doitFunction);


without event delegation:

  $('a.click').j01LoadContent({'callbackName': 'doit'})

with event delegation:

  $('document').j01LoadContentOn('hoover', 'a.load', {'callbackName': 'doit'})

  $('#content').j01LoadContentOnClick('a.loadOnClick', {'callbackName': 'doit'})

or enhance the J01ContentLoader with prototype and use the new method:

  J01ContentLoader.prototype.update = function(self) {
      // fade out, load content, fade in
  };
  var loader = new J01ContentLoader({'callbackName': 'doit'});
  loader.update('foo bar');


General setup:

  global setup during loading the script
    1. setup a callback handler registry
    3. setup statechange handler if global History.enabled

  optional setup in your project scripts
    1. implement custom callback method if not default j01RenderContent is used
    2. register custom callback

You can setup links without history support with:

  $('#foo').j01LoadContent({'enableHistory': false})

  link setup
    1. apply j01LoadContentProcessor click handler to links

  on click
    1. get url from link element (this)
    2. get callback from registry by callbackName
    3. call j01LoadContentProcessor with url and callback
    4. render response with callback method (asynchron)
    5. render content based on contentTargetExpression or default
    6. process error if any with built-in error handler in callback

You can setup links with history support (default) like:

  $('#foo').j01LoadContent()

  link setup
    1. apply notifyClick click handler to links

  on click
    1. get url from link element (this)
    2. add j=1 param to url (mark as j01LoadContent state url)
    3. optional add callbackName as 'c' param to url
    4. setup state with url
    5. call History.pushState which will notify statechange

  on statechange (this get called on any statechange)
    1. get state
    2. check 'j' param (condition for our state processing)
    3. get callback method based on 'c' param if state is for us
    4. call j01LoadContentProcessor with url, callback
    5. remove j, c params from url
    6. process response with callback method (asynchron)
    7. render content based on contentTargetExpression or default
    8. process error if any with built-in error handler in callback

