/* j01.button.js, disable and enable button on submit

   usage:

   enable button:

     $('#form.buttons.submit').j01ButtonDisabler(false);

   disable button:

     $('#form.buttons.submit').j01ButtonDisabler(true);

   apply generic click event handler:

     $('body').j01ButtonDisabler();

     or

     $('body').j01ButtonDisabler({'duraction': 2000});

   NOTE: Hyphenated names become camel-cased. For example, data-foo-bar=""
   becomes element.dataset.fooBar.
   see: http://www.w3.org/html/wg/drafts/html/master/dom.html#embedding-custom-non-visible-data-with-the-data-*-attributes
*/

(function($) {
$.fn.j01ButtonDisabler = function(o, duration) {
    var timeout = 5000
    if (o !== false && o !== true) {
        o = $.extend({
            duration: timeout
        }, o);
        timeout = o.duration
    }else if (typeof duration !== 'undefined') {
        timeout = duration;
    }

    function disableButton(selector) {
        var $btn = $(selector);
        if ($btn.prop('disabled') === false) {
            $btn.prop('disabled', true);
            // get loading text
            var txt = null;
            if ($btn.is('input')) {
                txt = $btn.prop('value');
            }else{
                txt = $btn.html();
            }
            if (txt) {
                // use loading text
                $btn.data('j01OriginalText', txt);
                var loading = $btn.data('j01LoadingText');
                if (loading) {
                    $btn.prop('value', loading);
                }
            }
            setTimeout(function(){
                doEnableButtonBySelector(selector);
            }, timeout);
        }
    }

    function doEnableButton($btn){
        var txt = $btn.data('j01OriginalText');
        if (txt) {
            if ($btn.is('input')) {
                $btn.prop('value', txt);
            }else{
                $btn.html(txt);
            }
        }
        if ($btn.prop('disabled')) {
            $btn.prop('disabled', false);
        }
    }

    function doEnableButtonBySelector(selector){
        var $btn = $(selector);
        if ($btn) {
            doEnableButton($btn);
        }
    }

    function doDisableButtonEventHandler(e) {
        // disableButton(selector);
        setTimeout(function(){
            // we use a timeout because it could conflict with a second call
            // if we use $('#btn').j01ButtonDisabler(true);
            // in a form for disable asap
            var selector = '#' + e.action;
            disableButton(selector);
        }, 50);
    }

    return this.each(function(){
        if (o === false) {
            // enable referenced buttons
            var $btn = $(this);
            doEnableButton($btn);
        }else if (o === true) {
            // disable referenced button
            var selector = '#' + $(this).prop('id');
            disableButton(selector);
        }else{
            $(this).off('j01.form.button.click', doDisableButtonEventHandler);
            $(this).on('j01.form.button.click', doDisableButtonEventHandler)
        }
    });
};
})(jQuery);
