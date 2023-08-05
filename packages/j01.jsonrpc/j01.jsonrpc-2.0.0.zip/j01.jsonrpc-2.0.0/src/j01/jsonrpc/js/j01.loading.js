/* j01.loading.js, */

(function($) {
$.fn.j01Loading = function(o) {
    // loading bar and handler

    var loading = null;

    function start() {
        // start loading bar
        if (!loading && $("#j01Loading").length === 0) {
            loading  = true;
            $("body").append("<div id='j01Loading'></div>")
            $("#j01Loading").addClass("waiting").append($("<dt/><dd/>"));
            $("#j01Loading").width((50 + Math.random() * 30) + "%");
        }
    }

    function stop() {
        // start loading bar
        $("#j01Loading").width("101%").delay(200).fadeOut(400, function() {
            $(this).remove();
            loading = false;
        });
    }

    function setup() {
        // setup loading bar event handler et.
        if (o.events) {
            $(document).bind('j01.jsonrpc.loading', function(event) {
                start();
            });
            $(document).bind('j01.jsonrpc.loaded', function(event) {
                stop();
            });
        }
    }

    // setup option or process start/stop command
    return this.each(function() {
        if (o === false) {
            start();
        }
        else if (o === true) {
            stop();
        }
        else  {
            o = $.extend({
                events: false
            }, o);
            // setup handler
            setup();
        }
    });
};
})(jQuery);
