(function ($) {
$.fn.j01Header = function (o) {
    // responsive navigation concept supporting different concepts like:
    // - expand/collaps on breakpoint (width)
    // - collaps on resize and orientationchange
    // - optional close on click outside expanded menu
    // - applies classes on body, container and toggler for different states
    //   the classes at the body tag can get used for stick to a fixed layout
    //   or use a relative layout if navigation is expanded
    // - close (other) expanded instances based on JQuery event trigger on
    //   navigation open
    o = $.extend({
        target: '.toggable',
        container: '#header',
        breakpoint: 9999,
        closeOnClickOutside: false,
        closeOnOpen: true,
        scrollTopOffset: 0,
        scrollTopSpeed: 0,
        resizable: true,
        mode: 'responsive',
        speed: 250,
    }, o || {});

    var body = null;
    var toggler = null;
    var toggable = null;
    var container = null;
    var timer = null;

    // event handler
    function tearDownCloseOnClickOutSide(toggler) {
        if (o.closeOnClickOutside) {
            $("html").unbind( "click.j01.header.outside" );
        }
    }

    function setUpCloseOnClickOutSide(toggler) {
        if (o.closeOnClickOutside) {
            $("html").bind("click.j01.header.outside", function(event) {
                var status = toggler.data('j01-header-status');
                if (status == 'open' && !$(event.target).parents(o.target).length) {
                    closeToggable(self, o.speed);
                    event.preventDefault();
                    return false;
                }
            });
        }
    }

    function setUpCloseOnOpen() {
        if (o.closeOnOpen) {
            $("html").bind("j01.header.open", function(event) {
                var status = toggler.data('j01-header-status');
                if (status == 'open' && !$(event.target).parents(o.target).length) {
                    closeToggable(self, o.speed);
                    event.preventDefault();
                    return false;
                }
            });
        }
    }

    function tearDownCloseOnOpen() {
        if (o.closeOnOpen) {
            $("html").unbind("j01.header.open");
        }
    }

    function setUpCLickHandler() {
        // click handler
        var self = this;
        toggler.click(function(event) {
            if (toggler.data('j01-header-status') === 'close'){
                openToggable(self, o.speed);
            } else  {
                closeToggable(self, o.speed);
            }
            event.preventDefault();
            return false;
        });
    }

    // style marker
    function addClassMarker(status) {
        if (status === 'open') {
            toggler.removeClass('close').addClass('open');
            container.removeClass('close').addClass('open');
            body.removeClass('j01HeaderClose j01HeaderDestroy').addClass(
                'j01HeaderOpen');
        }
        else if (status === 'close') {
            toggler.removeClass('open').addClass('close');
            container.removeClass('open').addClass('close');
            body.removeClass('j01HeaderOpen j01HeaderDestroy').addClass(
                'j01HeaderClose');
        }
        else if (status === 'destroy') {
            toggler.removeClass('open close');
            container.removeClass('open').addClass('close');
            body.removeClass('j01HeaderOpen j01HeaderClose').addClass(
                'j01HeaderDestroy');
        }
    }

    // toggler
    function openToggable(self, speed) {
        // expand toggable
        if (toggler.data('j01-header-status') === 'close') {
            // trigger open event for close other toggler
            $("html").trigger('j01.header.open')
            // open toggler
            toggler.data('j01-header-status', 'open');
            toggable.slideDown(speed, function() {
                addClassMarker('open');
                // scroll to top
                if (o.scrollTopOffset !== null && o.scrollTopSpeed !== null) {
                    $('html, body').animate({scrollTop: o.scrollTopOffset}, o.scrollTopSpeed);
                }
                // setup our toggler click outside handler
                setUpCloseOnClickOutSide(toggler);
                setUpCloseOnOpen();
            });
        }
    }

    function closeToggable(self, speed) {
        // collapse toggable
        if (toggler.data('j01-header-status') === 'open') {
            toggler.data('j01-header-status', 'close');
            tearDownCloseOnOpen();
            tearDownCloseOnClickOutSide();
            toggable.slideUp(speed, function() {
                addClassMarker('close');
            });
        }
    }

    function destroyToggable(self) {
        // destroy togglable
        if (toggler.data('j01-header-status') === 'destroy') {
            toggable.show();
            addClassMarker('destroy');
            tearDownCloseOnOpen();
            tearDownCloseOnClickOutSide();
        }
    }

    // resize
    function doResize() {
        var self = this;
        // find collaps condition
        if (o.breakpoint && o.breakpoint > container.width()) {
            // mobile, container is smaller then breakpoint, close on resize
            if (toggler.data('j01-header-status') === 'destroy') {
                toggler.data('j01-header-status', 'open');
            }
            closeToggable(self, 0);
        }else{
            // browser, non breakpoint or container is larger then breakpoint
            if (toggler.data('j01-header-status') !== 'destroy') {
                // only if not destroyed already
                toggler.data('j01-header-status', 'destroy');
                destroyToggable(self);
            }
        }
    }

    function startResizer() {
        var self = this;
        clearTimeout(timer);
        timer = setTimeout(doResize, 0);
    }

    // setup
    function setUpState() {
        var self = this;
        // find collaps condition
        if (o.breakpoint && o.breakpoint > container.width()) {
            // mobile, container is smaller then breakpoint
            toggler.data('j01-header-status', 'open');
            closeToggable(self, 0);
        }else{
            // browser, non breakpoint or container is larger then breakpoint
            toggler.data('j01-header-status', 'destroy');
            destroyToggable(self);
        }
    }

    return this.each(function () {
        body = $('body');
        toggler = $(this);
        toggable = $(o.target);
        container = $(o.container);
        setUpCLickHandler();
        setUpState();
        if (o.resizable) {
            // only support resizable for expandable navigation
            $(window).bind('resize orientationchange', startResizer);
        }
    });
};
})(jQuery);
