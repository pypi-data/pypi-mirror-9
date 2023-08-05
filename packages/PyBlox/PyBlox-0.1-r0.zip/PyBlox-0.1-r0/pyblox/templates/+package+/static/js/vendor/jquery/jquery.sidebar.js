;(function ($, window, document, undefined) {

    var Sidebar = function (element, options) {
        this.$el = $(element);
        this.options = $.extend({}, $.fn.sidebar.defaults, options);

        this.init();
    };

    Sidebar.prototype = {

        init: function () {
            var $this = $(this.$el);
            var $toggle = this.options.toggle;
            $this.find('li.active').has('ul').children('ul').addClass('collapse in');
            $this.find('li').not('.active').has('ul').children('ul').addClass('collapse');

            $this.find('li').has('ul').children('a').on('click', function (e) {
                e.preventDefault();
                $(this).parent('li').toggleClass('active').children('ul').collapse('toggle');
                if ($toggle) {
                    $(this).parent('li').siblings().removeClass('active').children('ul.in').collapse('hide');
                }
            });
        },
        _destroy: function () {

        }
    };

    $.fn.sidebar = function (option) {
        return this.each(function () {
            var $this = $(this);
            var options = typeof option === 'object' && option;
            var data = $this.data('sidebar');

            if (!data) $this.data('sidebar', (data = new Sidebar(this, options)));
            if (typeof option === 'string') data[option]();
        });
    };

    $.fn.sidebar.defaults = {
        toggle: '.parent'
    };

    $.fn.sidebar.Constructor = Sidebar;

})(jQuery, window, document);
