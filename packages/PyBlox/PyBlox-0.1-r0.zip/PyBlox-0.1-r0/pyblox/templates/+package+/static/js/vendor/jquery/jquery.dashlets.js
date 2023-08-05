;(function ($, window, document, undefined) {

    var pluginName = 'dashlets';

    function Dashlet(element, options) {
        this.$el = $(element);
        this.options = $.extend({}, $.fn[pluginName].defaults, options);
        this.dashlets = this.$el.find(this.options.dashlets);
        this.init();
    }

    Dashlet.prototype = {
        constructor: Dashlet,

        init: function () {
            var self = this;

        },

        _storeState: function () {

        },

        _retrieveState: function () {

        },

        fetchContent: function (url) {

        },

        destroy: function() {
        }

    };

    $.fn.dashlet = function (option) {
        return this.each(function () {
            var $this = $(this);
            var options = typeof option === 'object' && option;
            var data = $this.data('dashlet');

            if (!data) $this.data('dashlet', (data = new Dashlet(this, options)));
            if (typeof option === 'string') data[option]();
        });
    };

    $.fn.dashlet.defaults = {
        hasMinimize:    true,
        hasClose:   true,
        hasFullScreen:  false,
        contentUrl: ''
    };

    $.fn.dashlet.Constructor = Dashlet;

})(jQuery, window, document);