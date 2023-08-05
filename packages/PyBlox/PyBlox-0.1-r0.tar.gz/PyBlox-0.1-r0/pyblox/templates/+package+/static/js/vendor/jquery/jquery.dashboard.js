/*
    The MIT License (MIT)

    The Original Code is `Jquery Dashboard`

    The Initial Developer of the Original Code is Noel Morgan.
    Copyright (c) 2014 Noel Morgan <noel@morganix.com>

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.

*/
;(function ($, window, document, undefined) {

    var Dashboard = function (element, options) {
        this.$el = $(element);
        this.options = $.extend({}, $.fn.dashboard.defaults, options);
        this.columns = this.$el.find(this.options.columns);
        this.dashlets = this.$el.find(this.options.items);
        this.init();
    };

    Dashboard.prototype = {
        constructor: Dashboard,

        init: function () {
            var self = this;

//            $('.dashboard').each(function () {
//                if ($(this).find(self.options.items).length) {
//                    $(this).addClass('dashboard-grid');
//                }
//            });

            $('.dashboard').sortable({
                connectWith: self.options.connectWith,
                items: self.options.items,
                handle: self.options.handle,
                cursor: self.options.cursor,
                zIndex: self.options.zIndex,
                placeholder: self.options.placeholder,
                forcePlaceholderSize: self.options.forcePlaceholderSize,
                forceHelperSize: self.options.forceHelperSize,
                revert: self.options.revert,
                dropOnEmpty: self.options.dropOnEmpty,
                update: function(event, ui) {
                    self._storeState(event, ui);
                }

            });

            self._retrieveState();
        },
        _storeState: function (event, ui)  {
            var self = this;

            if (typeof(Storage) != "undefined") {
                var dashData = [];

                $.each(self.columns, function (i, column) {
                    var columnData = [];

                    $('#'+column.id).each(function () {
                        $.each($(this).find('.dashlet'), function (x, dashlet) {
                            var dashletDom = $("#"+dashlet.id);
                            columnData.push({'id': dashletDom.attr('id'), 'orderIndex': x++,
                                'cssClass': $(this).attr('class')});
                        });
                    });
                    dashData.push({'columnId': column.id, 'columnIndex': i++, 'columnData': columnData});
                });
                localStorage.setItem("dashboardData", JSON.stringify(dashData));
            } else {
                console.log("HTML5 localStorage Not Enabled. Can't save anything!");
            }
        },
        _retrieveState: function () {
            var self = this;
            var data = localStorage.getItem("dashboardData");
            if (!data) return;
            var dashData =  JSON.parse(data);

            $.each(dashData, function (index, column) {
                $.each(column.columnData, function (i, dashlet) {
                    var d = $('#'+dashlet.id);
                    d.attr('class', dashlet.cssClass);
                    d.appendTo($('#'+column.columnId));
                });
            });
        },
        destroy: function () {
            var self = this;
            // XXX:
        }
    };

    $.fn.dashboard = function (option) {
        return this.each(function () {
            var $this = $(this);
            var options = typeof option === 'object' && option;
            var data = $this.data('dashboard');

            if (!data) $this.data('dashboard', (data = new Dashboard(this, options)));
            if (typeof option === 'string') data[option]();
        });
    };

    $.fn.dashboard.defaults = {
        connectWith: '.dashboard',
        columns: '.column',
        items: '.dashlet',
        handle: '.dashlet-header',
        cursor: 'move',
        zIndex: 9999,
        placeholder: 'dashlet-placeholder',
        forcePlaceholderSize: true,
        forceHelperSize: true,
        revert: true,
        dropOnEmpty: true
    };

    $.fn.dashboard.Constructor = Dashboard;

})(jQuery, window, document);