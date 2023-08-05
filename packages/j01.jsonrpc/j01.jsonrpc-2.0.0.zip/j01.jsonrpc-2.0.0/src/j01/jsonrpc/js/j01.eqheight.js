// equal column height javacsript
// use the equal column as jquery selector
// $('.eqHeight').eqHeight();
(function() {
$.fn.eqHeight = function(o) {
    // equalize columns per row
    o = $.extend({
        columns: '.eqHeightRow',
        events: 'load resize orientationchange j01.jsonrpc.loaded',
        timeout: 100,
        resizable: true,
        breakpoint: 991
    }, o);

    $(this).each(function(){
        // setup columns as inner variable so each row can define it's own
        // columns and apply it's own resizer
        var timer = null;
        var columns = $();

        function equalizeColumns(){
            // equalize height using row as context
            var cols = $(".eqHeightMarker");
            var maxHeight = 0;
            cols.each(function() {
                return maxHeight = Math.max($(this).height(), maxHeight);
            });
            cols.height(maxHeight);
            return $(".eqHeightMarker").removeClass("eqHeightMarker");
        }

        function doEqualize() {
            // first detroy column height
            columns.height("auto");
            // check responsive breakpoint
            if (o.breakpoint && o.breakpoint < $(document).width()) {
                // equalize height if larger then breakpoint
                var rTop = columns.first().position().top;
                columns.each(function() {
                    var cTop = $(this).position().top;
                    if (cTop !== rTop) {
                        equalizeColumns();
                        rTop = $(this).position().top;
                    }
                    return $(this).addClass("eqHeightMarker");
                });
                return equalizeColumns();
            }else{
                // reset height to auto
                columns.each(function() {
                    $(this).height("auto");
                });
                return true;
            }
        };

        function doResize() {
            clearTimeout(timer);
            return timer = setTimeout(doEqualize, o.timeout);
        };

        function setUpEqualizer(){
            // conditions
            if (columns.length === 0) {
                return;
            }
            // setup onload handler
            if (o.resizable) {
                $(window).bind(o.events, doResize);
            }
        };

        function setUpColumns(self){
            // setup columns per row
            $(self).find(''+o.columns).each(function() {
                columns.push(this);
            });
        };
        // setup columns per row
        setUpColumns(this);
        // setup equalizer
        setUpEqualizer();
    });
    return $(this);

};
})(jQuery);
