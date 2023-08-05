;(function ($, window, document, undefined) {

    //"use strict"; // jshint ;_;
    var pluginName = 'dashlets';

    function Dashlet(element, options) {
        /**
         * Variables.
         **/
        this.$el = $(element);
        this.options = $.extend({}, $.fn[pluginName].defaults, options);
        this.dashletId = this.$el.attr('id');
        this.dashlet = this.$el.find(this.options.dashlets);

        this.init();
    }

    Dashlet.prototype = {

        /**
         * Important settings like storage and touch support.
         *
         * @param:
         **/
        _settings: function () {
            var self = this;

            //*****************************************************************//
            //////////////////////// LOCALSTORAGE CHECK /////////////////////////
            //*****************************************************************//

            storage = !! function () {
                var result, uid = +new Date;
                try {
                    localStorage.setItem(uid, uid);
                    result = localStorage.getItem(uid) == uid;
                    localStorage.removeItem(uid);
                    return result;
                } catch (e) {}
            }() && localStorage;

            //*****************************************************************//
            /////////////////////////// SET/GET KEYS ////////////////////////////
            //*****************************************************************//

            if (storage && self.options.localStorage) {

                if (self.options.ajaxnav === true) {
                    dashlet_url = location.hash.replace(/^#/, '')

                    keySettings = 'Dashlet_settings_' + dashlet_url + '_' + self.objId;
                    getKeySettings = localStorage.getItem(keySettings);

                    keyPosition = 'Dashlet_position_' + dashlet_url + '_' + self.objId;
                    getKeyPosition = localStorage.getItem(keyPosition);
                    //console.log(self.options.ajaxnav + " if")

                } else {

                    keySettings = 'pbx_settings_' + location.pathname + '_' + self.objId;
                    getKeySettings = localStorage.getItem(keySettings);

                    keyPosition = 'pbx_position_' + location.pathname + '_' + self.objId;
                    getKeyPosition = localStorage.getItem(keyPosition);
                    //console.log(self.options.ajaxnav + " else")

                } // end else
            } // end if

            //*****************************************************************//
            ////////////////////////// TOUCH SUPPORT ////////////////////////////
            //*****************************************************************//

            /**
             * Check for touch support and set right click events.
             **/
            if (('ontouchstart' in window) || window.DocumentTouch && document instanceof DocumentTouch) {
                clickEvent = 'touchstart';
                //click tap
            } else {
                clickEvent = 'click';
            }

        },

        /**
         * Function for the indicator image.
         *
         * @param:
         **/
        _runLoaderDashlet: function (elm) {
            var self = this;
            if (self.options.indicator === true) {
                elm.parents(self.options.dashlets)
                    .find('.dashlet-loading')
                    .stop(true, true)
                    .fadeIn(100)
                    .delay(self.options.indicatorTime)
                    .fadeOut(100);
            }
        },

        /**
         * AJAX load File, which get and shows the .
         *
         * @param: adashlet | object  | The dashlet.
         * @param: file    | file    | The file thats beeing loaded.
         * @param: loader  | object  | The dashlet.
         **/
        _loadAjaxFile: function (adashlet, file, loader) {

            var self = this;

            adashlet.find('.dashlet-body')
                .load(file, function (response, status, xhr) {

                    var $this = $(this);

                    /**
                     * If action runs into an error display an error msg.
                     **/
                    if (status == "error") {
                        $this.html('<h4 class="alert alert-danger">' + self.options.labelError + '<b> ' +
                            xhr.status + " " + xhr.statusText + '</b></h4>');
                    }

                    /**
                     * Run if there are no errors.
                     **/
                    if (status == "success") {

                        /**
                         * Show a timestamp.
                         **/
                        var aPalceholder = adashlet.find(self.options.timestampPlaceholder);

                        if (aPalceholder.length) {

                            aPalceholder.html(self._getPastTimestamp(new Date()));
                        }

                        /**
                         * Run the callback function.
                         **/
                        if (typeof self.options.afterLoad == 'function') {
                            self.options.afterLoad.call(this, adashlet);
                        }
                    }
                });

            /**
             * Run function for the indicator image.
             **/
            self._runLoaderDashlet(loader);

        },

        /**
         * Save all settings to the localStorage.
         *
         * @param:
         **/
        _saveSettingsDashlet: function () {

            var self = this;

            self._settings();

            if (storage && self.options.localStorage) {
                var storeSettings = [];

                self.obj.find(self.options.dashlets)
                    .each(function () {
                        var storeSettingsStr = {};
                        storeSettingsStr['id'] = $(this)
                            .attr('id');
                        storeSettingsStr['style'] = $(this)
                            .attr('data-dashlet-attstyle');
                        storeSettingsStr['title'] = $(this)
                            .children('header')
                            .children('h2')
                            .text();
                        storeSettingsStr['hidden'] = ($(this)
                            .is(':hidden') ? 1 : 0);
                        storeSettingsStr['collapsed'] = ($(this)
                            .hasClass('dashlet-collapsed') ? 1 : 0);
                        storeSettings.push(storeSettingsStr);
                    });

                var storeSettingsObj = JSON.stringify({
                    'dashlet': storeSettings
                });

                /* Place it in the storage(only if needed) */
                if (getKeySettings != storeSettingsObj) {
                    localStorage.setItem(keySettings, storeSettingsObj);
                }
            }

            /**
             * Run the callback function.
             **/
            if (typeof self.options.onSave == 'function') {
                self.options.onSave.call(this, null, storeSettingsObj);
            }
        },

        /**
         * Save positions to the localStorage.
         *
         * @param:
         **/
        _savePositionDashlet: function () {

            var self = this;

            self._settings();

            if (storage && self.options.localStorage) {
                var mainArr = [];

                self.obj.find(self.options.grid + '.sortable-grid')
                    .each(function () {
                        var subArr = [];
                        $(this)
                            .children(self.options.dashlets)
                            .each(function () {
                                var subObj = {};
                                subObj['id'] = $(this)
                                    .attr('id');
                                subArr.push(subObj);
                            });
                        var out = {
                            'section': subArr
                        }
                        mainArr.push(out);
                    });

                var storePositionObj = JSON.stringify({
                    'grid': mainArr
                });

                /* Place it in the storage(only if needed) */
                if (getKeyPosition != storePositionObj) {
                    localStorage.setItem(keyPosition, storePositionObj, null);
                }
            }

            /**
             * Run the callback function.
             **/
            if (typeof self.options.onSave == 'function') {
                self.options.onSave.call(this, storePositionObj);
            }
        },

        /**
         * Code that we run at the start.
         *
         * @param:
         **/
        init: function () {

            var self = this;
            self._settings();
            /**
             * Add RTL support.
             **/
            if (self.options.rtl === true) {
                $('body')
                    .addClass('rtl');
            }

            /**
             * This will add an extra class that we use to store the
             * dashlets in the right order.(savety)
             **/

            $(self.options.grid).each(function () {
                if ($(this).find(self.options.dashlets).length) {
                    $(this).addClass('sortable-grid');
                }
            });

            //*****************************************************************//
            //////////////////////// SET POSITION WIDGET ////////////////////////
            //*****************************************************************//

            /**
             * Run if data is present.
             **/
            if (storage && self.options.localStorage && getKeyPosition) {

                var jsonPosition = JSON.parse(getKeyPosition);

                /**
                 * Loop the data, and put every dashlet on the right place.
                 **/
                for (var key in jsonPosition.grid) {
                    var changeOrder = self.obj.find(self.options.grid + '.sortable-grid')
                        .eq(key);
                    for (var key2 in jsonPosition.grid[key].section) {
                        changeOrder.append($('#' + jsonPosition.grid[key].section[key2].id));
                    }
                }

            }

            //*****************************************************************//
            /////////////////////// SET SETTINGS WIDGET /////////////////////////
            //*****************************************************************//
            /**
             * Run if data is present.
             **/
            if (storage && self.options.localStorage && getKeySettings) {

                var jsonSettings = JSON.parse(getKeySettings);

                /**
                 * Loop the data and hide/show the dashlets and set the inputs in
                 * panel to checked(if hidden) and add an indicator class to the div.
                 * Loop all labels and update the dashlet titles.
                 **/
                for (var key in jsonSettings.dashlet) {
                    var dashletId = $('#' + jsonSettings.dashlet[key].id);

                    /**
                     * Set a style(if present).
                     **/
                    if (jsonSettings.dashlet[key].style) {
                        //console.log("test");
                        dashletId.removeClassPrefix('dashlet-color-')
                            .addClass(jsonSettings.dashlet[key].style)
                            .attr('data-dashlet-attstyle', '' + jsonSettings.dashlet[key].style + '');
                    }

                    /**
                     * Hide/show dashlet.
                     **/
                    if (jsonSettings.dashlet[key].hidden == 1) {
                        dashletId.hide(1);
                    } else {
                        dashletId.show(1)
                            .removeAttr('data-dashlet-hidden');
                    }

                    /**
                     * Toggle content dashlet.
                     **/
                    if (jsonSettings.dashlet[key].collapsed == 1) {
                        dashletId.addClass('dashlet-collapsed')
                            .children('div')
                            .hide(1);
                    }

                    /**
                     * Update title dashlet (if needed).
                     **/
                    if (dashletId.children('titlebar')
                        .children('h2')
                        .text() != jsonSettings.dashlet[key].title) {
                        dashletId.children('header')
                            .children('h2')
                            .text(jsonSettings.dashlet[key].title);
                    }
                }
            }

            //*****************************************************************//
            ////////////////////////// LOOP ALL WIDGETS //////////////////////////
            //*****************************************************************//
            /**
             * This will add/edit/remove the settings to all dashlets
             **/
            self.dashlet.each(function () {

                var tDashlet = $(this);
                var thisHeader = $(this)
                    .children('header');

                /**
                 * Dont double wrap(check).
                 **/
                if (!thisHeader.parent()
                    .attr('role')) {

                    /**
                     * Hide the dashlet if the dataset 'dashlet-hidden' is set to true.
                     **/
                    if (tDashlet.data('dashlet-hidden') === true) {
                        tDashlet.hide();
                    }

                    /**
					 * Hide the content of the dashlet if the dataset
					 * 'dashlet-collapsed' is set to true.

					 **/
                    if (tDashlet.data('dashlet-collapsed') === true) {
                        tDashlet.addClass('dashlet-collapsed')
                            .children('div')
                            .hide();
                    }

                    /**
                     * Check for the dataset 'dashlet-icon' if so get the icon
                     * and attach it to the dashlet header.
                     * NOTE: MOVED THIS TO PHYSICAL for more control
                     **/
                    //if(tDashlet.data('dashlet-icon')){
                    //	thisHeader.prepend('<i class="dashlet-icon '+tDashlet.data('dashlet-icon')+'"></i>');
                    //}

                    /**
                     * Add a delete button to the dashlet header (if set to true).
                     **/
                    if (self.options.customButton === true && tDashlet.data('dashlet-custombutton') ===
                        undefined && self.customClass[0].length != 0) {
                        var customBtn =
                            '<a href="javascript:void(0);" class="button-icon dashlet-custom-btn"><i class="' + self.customClass[0] + '"></i></a>';
                    } else {
                        customBtn = '';
                    }

                    /**
                     * Add a delete button to the dashlet header (if set to true).
                     **/
                    if (self.options.deleteButton === true && tDashlet.data('dashlet-deletebutton') ===
                        undefined) {
                        var deleteBtn =
                            '<a href="javascript:void(0);" class="button-icon dashlet-delete-btn" rel="tooltip" title="Delete" data-placement="bottom"><i class="' +
                            self.options.deleteClass + '"></i></a>';
                    } else {
                        deleteBtn = '';
                    }

                    /**
                     * Add a delete button to the dashlet header (if set to true).
                     **/
//                    if (self.options.editButton === true && tDashlet.data('dashlet-editbutton') === undefined) {
//                        var editBtn =
//                            '<a href="javascript:void(0);" class="button-icon dashlet-edit-btn" rel="tooltip" title="Edit Title" data-placement="bottom"><i class="' +
//                            self.editClass[0] + '"></i></a>';
//                    } else {
                        editBtn = '';
//                    }

                    /**
                     * Add a delete button to the dashlet header (if set to true).
                     **/
                    if (self.options.fullscreenButton === true && tDashlet.data('dashlet-fullscreenbutton') ===
                        undefined) {
                        var fullscreenBtn =
                            '<a href="javascript:void(0);" class="button-icon dashlet-fullscreen-btn" rel="tooltip" title="Fullscreen" data-placement="bottom"><i class="' +
                            self.fullscreenClass[0] + '"></i></a>';
                    } else {
                        fullscreenBtn = '';
                    }

                    /**
                     * Add a delete button to the dashlet header (if set to true).
                     **/
                    if (self.options.colorButton === true && tDashlet.data('dashlet-colorbutton') ===
                        undefined) {
                        var dashletcolorBtn =
                            '<a data-toggle="dropdown" class="dropdown-toggle color-box selector" href="javascript:void(0);"></a><ul class="dropdown-menu arrow-box-up-right color-select pull-right"><li><span class="bg-color-green" data-dashlet-setstyle="dashlet-color-green" rel="tooltip" data-placement="left" data-original-title="Green Grass"></span></li><li><span class="bg-color-greenDark" data-dashlet-setstyle="dashlet-color-greenDark" rel="tooltip" data-placement="top" data-original-title="Dark Green"></span></li><li><span class="bg-color-greenLight" data-dashlet-setstyle="dashlet-color-greenLight" rel="tooltip" data-placement="top" data-original-title="Light Green"></span></li><li><span class="bg-color-purple" data-dashlet-setstyle="dashlet-color-purple" rel="tooltip" data-placement="top" data-original-title="Purple"></span></li><li><span class="bg-color-magenta" data-dashlet-setstyle="dashlet-color-magenta" rel="tooltip" data-placement="top" data-original-title="Magenta"></span></li><li><span class="bg-color-pink" data-dashlet-setstyle="dashlet-color-pink" rel="tooltip" data-placement="right" data-original-title="Pink"></span></li><li><span class="bg-color-pinkDark" data-dashlet-setstyle="dashlet-color-pinkDark" rel="tooltip" data-placement="left" data-original-title="Fade Pink"></span></li><li><span class="bg-color-blueLight" data-dashlet-setstyle="dashlet-color-blueLight" rel="tooltip" data-placement="top" data-original-title="Light Blue"></span></li><li><span class="bg-color-teal" data-dashlet-setstyle="dashlet-color-teal" rel="tooltip" data-placement="top" data-original-title="Teal"></span></li><li><span class="bg-color-blue" data-dashlet-setstyle="dashlet-color-blue" rel="tooltip" data-placement="top" data-original-title="Ocean Blue"></span></li><li><span class="bg-color-blueDark" data-dashlet-setstyle="dashlet-color-blueDark" rel="tooltip" data-placement="top" data-original-title="Night Sky"></span></li><li><span class="bg-color-darken" data-dashlet-setstyle="dashlet-color-darken" rel="tooltip" data-placement="right" data-original-title="Night"></span></li><li><span class="bg-color-yellow" data-dashlet-setstyle="dashlet-color-yellow" rel="tooltip" data-placement="left" data-original-title="Day Light"></span></li><li><span class="bg-color-orange" data-dashlet-setstyle="dashlet-color-orange" rel="tooltip" data-placement="bottom" data-original-title="Orange"></span></li><li><span class="bg-color-orangeDark" data-dashlet-setstyle="dashlet-color-orangeDark" rel="tooltip" data-placement="bottom" data-original-title="Dark Orange"></span></li><li><span class="bg-color-red" data-dashlet-setstyle="dashlet-color-red" rel="tooltip" data-placement="bottom" data-original-title="Red Rose"></span></li><li><span class="bg-color-redLight" data-dashlet-setstyle="dashlet-color-redLight" rel="tooltip" data-placement="bottom" data-original-title="Light Red"></span></li><li><span class="bg-color-white" data-dashlet-setstyle="dashlet-color-white" rel="tooltip" data-placement="right" data-original-title="Purity"></span></li><li><a href="javascript:void(0);" class="dashlet-remove-colors" data-dashlet-setstyle="" rel="tooltip" data-placement="bottom" data-original-title="Reset dashlet color to default">Remove</a></li></ul>';
                        thisHeader.prepend('<div class="dashlet-toolbar">' + dashletcolorBtn + '</div>');

                    } else {
                        dashletcolorBtn = '';
                    }

                    /**
                     * Add a toggle button to the dashlet header (if set to true).
                     **/
                    if (tDashlet.data('dashlet-togglebutton') ===
                        undefined) {
                        if (tDashlet.data('dashlet-collapsed') === true || tDashlet.hasClass(
                            'dashlet-collapsed')) {
                            var toggleSettings = self.toggleClass[1];
                        } else {
                            toggleSettings = self.toggleClass[0];
                        }
                        var toggleBtn =
                            '<a href="#" class="button-icon dashlet-toggle-btn" rel="tooltip" title="Collapse" data-placement="bottom"><i class="' +
                            toggleSettings + '"></i></a>';
                    } else {
                        toggleBtn = '';
                    }

                    /**
                     * Add a refresh button to the dashlet header (if set to true).
                     **/
                    if (self.options.refreshButton === true && tDashlet.data('dashlet-refreshbutton') !=
                        false && tDashlet.data('dashlet-load')) {
                        var refreshBtn =
                            '<a href="#" class="button-icon dashlet-refresh-btn" data-loading-text="&nbsp;&nbsp;Loading...&nbsp;" rel="tooltip" title="Refresh" data-placement="bottom"><i class="' +
                            self.options.refreshButtonClass + '"></i></a>';
                    } else {
                        refreshBtn = '';
                    }

                    /**
                     * Set the buttons order.
                     **/
                    var formatButtons = self.options.buttonOrder.replace(/%refresh%/g, refreshBtn)
                        .replace(/%delete%/g, deleteBtn)
                        .replace(/%custom%/g, customBtn)
                        .replace(/%fullscreen%/g, fullscreenBtn)
                        .replace(/%edit%/g, editBtn)
                        .replace(/%toggle%/g, toggleBtn);

                    /**
                     * Add a button wrapper to the header.
                     **/
                    if (refreshBtn != '' || deleteBtn != '' || customBtn != '' || fullscreenBtn != '' || editBtn != '' || toggleBtn != '') {
                        thisHeader.prepend('<div class="dashlet-ctrls">' + formatButtons + '</div>');
                    }

                    /**
                     * Adding a helper class to all sortable dashlets, this will be
                     * used to find the dashlets that are sortable, it will skip the dashlets
                     * that have the dataset 'dashlet-sortable="false"' set to false.
                     **/
                    if (self.options.sortable === true && tDashlet.data('dashlet-sortable') === undefined) {
                        tDashlet.addClass('dashlet-sortable');
                    }

                    /**
                     * If the edit box is present copy the title to the input.
                     **/
                    if (tDashlet.find(self.options.editPlaceholder)
                        .length) {
                        tDashlet.find(self.options.editPlaceholder)
                            .find('input')
                            .val($.trim(thisHeader.children('h2')
                                .text()));
                    }

                    /**
                     * Prepend the image to the dashlet header.
                     **/
                    thisHeader.append(
                        '<span class="dashlet-loader"><i class="fa fa-refresh fa-spin"></i></span>'
                    );

                    /**
                     * Adding roles to some parts.
                     **/
                    tDashlet.attr('role', 'dashlet')
                        .children('div')
                        .attr('role', 'content')
                        .prev('header')
                        .attr('role', 'heading')
                        .children('div')
                        .attr('role', 'menu');
                }
            });

            /**
             * Hide all buttons if option is set to true.
             **/
            if (self.options.buttonsHidden === true) {
                $(self.options.pwCtrls)
                    .hide();
            }

            /* activate all tooltips */
            $(".dashlet header [rel=tooltip]")
                .tooltip();

            //******************************************************************//
            //////////////////////////////// AJAX ////////////////////////////////
            //******************************************************************//

            /**
             * Loop all ajax dashlets.
             **/
            self.obj.find('[data-dashlet-load]')
                .each(function () {

                    /**
                     * Variables.
                     **/
                    var thisItem = $(this),
                        thisItemHeader = thisItem.children(),
                        pathToFile = thisItem.data('dashlet-load'),
                        reloadTime = thisItem.data('dashlet-refresh') * 1000,
                        ajaxLoader = thisItem.children();

                    if (!thisItem.find('.dashlet-ajax-placeholder')
                        .length) {

                        /**
                         * Append a AJAX placeholder.
                         **/
                        thisItem.children('dashlet-body')
                            .append('<div class="dashlet-ajax-placeholder">' + self.options.loadingLabel + '</div>');

                        /**
                         * If dashlet has a reload time refresh the dashlet, if the value
                         * has been set to 0 dont reload.
                         **/
                        if (thisItem.data('dashlet-refresh') > 0) {

                            /**
                             * Load file on start.
                             **/
                            self._loadAjaxFile(thisItem, pathToFile, thisItemHeader);

                            /**
                             * Set an interval to reload the content every XXX seconds.
                             **/
                            setInterval(function () {

                                self._loadAjaxFile(thisItem, pathToFile, thisItemHeader);
                            }, reloadTime);
                        } else {

                            /**
                             * Load the content just once.
                             **/
                            self._loadAjaxFile(thisItem, pathToFile, thisItemHeader);

                        }
                    }
                });

            //******************************************************************//
            ////////////////////////////// SORTABLE //////////////////////////////
            //******************************************************************//

            /**
             * jQuery UI sortable, this allows users to sort the dashlets.
             * Notice that this part needs the jquery-ui core to work.
             **/
            if (self.options.sortable === true && jQuery.ui) {
                var sortItem = self.obj.find('.sortable-grid').not('[data-dashlet-excludegrid]');

                sortItem.sortable({
                    items: sortItem.find('.dashlet-sortable'),
                    connectWith: sortItem,
                    placeholder: self.options.placeholderClass,
                    cursor: 'move',
                    revert: true,
                    opacity: self.options.opacity,
                    delay: 200,
                    cancel: '.button-icon, #dashlet-fullscreen-mode > div',
                    zIndex: 10000,
                    handle: self.options.dragHandle,
                    forcePlaceholderSize: true,
                    forceHelperSize: true,
                    update: function (event, ui) {
                        /* run pre-loader in the dashlet */
                        self._runLoaderDashlet(ui.item.children());
                        /* store the positions of the plugins */
                        self._savePositionDashlet();
                        /**
                         * Run the callback function.
                         **/
                        if (typeof self.options.onChange == 'function') {
                            self.options.onChange.call(this, ui.item);
                        }
                    }
                });
            }

            //*****************************************************************//
            ////////////////////////// BUTTONS VISIBLE //////////////////////////
            //*****************************************************************//

            /**
             * Show and hide the dashlet control buttons, the buttons will be
             * visible if the users hover over the dashlets header. At default the
             * buttons are always visible.
             **/
            if (self.options.buttonsHidden === true) {

                /**
                 * Show and hide the buttons.
                 **/
                self.dashlet.children('header')
                    .hover(function () {
                        $(this)
                            .children(self.options.pwCtrls)
                            .stop(true, true)
                            .fadeTo(100, 1.0);
                    }, function () {
                        $(this)
                            .children(self.options.pwCtrls)
                            .stop(true, true)
                            .fadeTo(100, 0.0);
                    });
            }

            //*****************************************************************//
            ///////////////////////// CLICKEVENTS //////////////////////////
            //*****************************************************************//

            self._clickEvents();

            //*****************************************************************//
            ///////////////////// DELETE LOCAL STORAGE KEYS /////////////////////
            //*****************************************************************//

            /**
             * Delete the settings key.
             **/
            $(self.options.deleteSettingsKey)
                .on(clickEvent, this, function (e) {
                    if (storage && self.options.localStorage) {
                        var cleared = confirm(self.options.settingsKeyLabel);
                        if (cleared) {
                            localStorage.removeItem(keySettings);
                        }
                    }
                    e.preventDefault();
                });

            /**
             * Delete the position key.
             **/
            $(self.options.deletePositionKey)
                .on(clickEvent, this, function (e) {
                    if (storage && self.options.localStorage) {
                        var cleared = confirm(self.options.positionKeyLabel);
                        if (cleared) {
                            localStorage.removeItem(keyPosition);
                        }
                    }
                    e.preventDefault();
                });

            //*****************************************************************//
            ///////////////////////// CREATE NEW KEYS  //////////////////////////
            //*****************************************************************//

            /**
             * Create new keys if non are present.
             **/
            if (storage && self.options.localStorage) {

                /**
                 * If the local storage key (keySettings) is empty or
                 * does not excite, create one and fill it.
                 **/
                if (getKeySettings === null || getKeySettings.length < 1) {
                    self._saveSettingsDashlet();
                }

                /**
                 * If the local storage key (keyPosition) is empty or
                 * does not excite, create one and fill it.
                 **/
                if (getKeyPosition === null || getKeyPosition.length < 1) {
                    self._savePositionDashlet();
                }
            }

        },

        /**
         * All of the click events.
         *
         * @param:
         **/
        _clickEvents: function () {

            var self = this;

            self._settings();

            //*****************************************************************//
            /////////////////////////// TOGGLE WIDGETS //////////////////////////
            //*****************************************************************//

            /**
             * Allow users to toggle the content of the dashlets.
             **/
            self.dashlet.on(clickEvent, '.dashlet-toggle-btn', function (e) {

                var tDashlet = $(this);
                var pDashlet = tDashlet.parents(self.options.dashlets);

                /**
                 * Run function for the indicator image.
                 **/
                self._runLoaderDashlet(tDashlet);

                /**
                 * Change the class and hide/show the dashlets content.
                 **/
                if (pDashlet.hasClass('dashlet-collapsed')) {
                    tDashlet.children()
                        .removeClass(self.toggleClass[1])
                        .addClass(self.toggleClass[0])
                        .parents(self.options.dashlets)
                        .removeClass('dashlet-collapsed')
                        .children('[role=content]')
                        .slideDown(self.options.toggleSpeed, function () {
                            self._saveSettingsDashlet();
                        });
                } else {
                    tDashlet.children()
                        .removeClass(self.toggleClass[0])
                        .addClass(self.toggleClass[1])
                        .parents(self.options.dashlets)
                        .addClass('dashlet-collapsed')
                        .children('[role=content]')
                        .slideUp(self.options.toggleSpeed, function () {
                            self._saveSettingsDashlet();
                        });
                }

                /**
                 * Run the callback function.
                 **/
                if (typeof self.options.onToggle == 'function') {
                    self.options.onToggle.call(this, pDashlet);
                }

                e.preventDefault();
            });

            //*****************************************************************//
            ///////////////////////// FULLSCREEN WIDGETS ////////////////////////
            //*****************************************************************//

            /**
             * Set fullscreen height function.
             **/
            function heightFullscreen() {
                if ($('#dashlet-fullscreen-mode').length) {

                    /**
                     * Setting height variables.
                     **/
                    var heightWindow = $(window).height();
                    var heightHeader = $('#dashlet-fullscreen-mode')
                        .find(self.options.dashlets)
                        .children('header')
                        .height();

                    /**
                     * Setting the height to the right dashlet.
                     **/
                    $('#dashlet-fullscreen-mode')
                        .find(self.options.dashlets)
                        .children('div')
                        .height(heightWindow - heightHeader - 15);
                }
            }

            /**
             * On click go to fullscreen mode.
             **/
            self.dashlet.on(clickEvent, '.dashlet-fullscreen-btn', function (e) {

                var thisDashlet = $(this)
                    .parents(self.options.dashlets);
                var thisDashletContent = thisDashlet.children('div');

                /**
                 * Run function for the indicator image.
                 **/
                self._runLoaderDashlet($(this));

                /**
                 * Wrap the dashlet and go fullsize.
                 **/
                if ($('#dashlet-fullscreen-mode').length) {

                    /**
                     * Remove class from the body.
                     **/
                    $('.nooverflow')
                        .removeClass('nooverflow');

                    /**
                     * Unwrap the dashlet, remove the height, set the right
                     * fullscreen button back, and show all other buttons.
                     **/
                    thisDashlet.unwrap('<div>')
                        .children('div')
                        .removeAttr('style')
                        .end()
                        .find('.dashlet-fullscreen-btn')
                        .children()
                        .removeClass(self.fullscreenClass[1])
                        .addClass(self.fullscreenClass[0])
                        .parents(self.pwCtrls)
                        .children('a')
                        .show();

                    /**
                     * Reset collapsed dashlets.
                     **/
                    if (thisDashletContent.hasClass('dashlet-visible')) {
                        thisDashletContent.hide()
                            .removeClass('dashlet-visible');
                    }

                } else {
                    /**
                     * Prevent the body from scrolling.
                     **/
                    $('body')
                        .addClass('nooverflow');

                    /**
					 * Wrap, append it to the body, show the right button

					 * and hide all other buttons.
					 **/
                    thisDashlet.wrap('<div id="dashlet-fullscreen-mode"/>')
                        .parent()
                        .find('.dashlet-fullscreen-btn')
                        .children()
                        .removeClass(self.fullscreenClass[0])
                        .addClass(self.fullscreenClass[1])
                        .parents(self.pwCtrls)
                        .children('a:not(.dashlet-fullscreen-btn)')
                        .hide();

                    /**
                     * Show collapsed dashlets.
                     **/
                    if (thisDashletContent.is(':hidden')) {
                        thisDashletContent.show()
                            .addClass('dashlet-visible');
                    }
                }

                /**
                 * Run the set height function.
                 **/
                heightFullscreen();

                /**
                 * Run the callback function.
                 **/
                if (typeof self.options.onFullscreen == 'function') {
                    self.options.onFullscreen.call(this, thisDashlet);
                }

                e.preventDefault();
            });

            /**
             * Run the set fullscreen height function when the screen resizes.
             **/
            $(window)
                .resize(function () {

                    /**
                     * Run the set height function.
                     **/
                    heightFullscreen();
                });

            //*****************************************************************//
            //////////////////////////// EDIT WIDGETS ///////////////////////////
            //*****************************************************************//

            /**
             * Allow users to show/hide a edit box.
             **/
            self.dashlet.on(clickEvent, '.dashlet-edit-btn', function (e) {

                var tDashlet = $(this)
                    .parents(self.options.dashlets);

                /**
                 * Run function for the indicator image.
                 **/
                self._runLoaderDashlet($(this));

                /**
                 * Show/hide the edit box.
                 **/
                if (tDashlet.find(self.options.editPlaceholder)
                    .is(':visible')) {
                    $(this)
                        .children()
                        .removeClass(self.editClass[1])
                        .addClass(self.editClass[0])
                        .parents(self.options.dashlets)
                        .find(self.options.editPlaceholder)
                        .slideUp(self.options.editSpeed, function () {
                            self._saveSettingsDashlet();
                        });
                } else {
                    $(this)
                        .children()
                        .removeClass(self.editClass[0])
                        .addClass(self.editClass[1])
                        .parents(self.options.dashlets)
                        .find(self.options.editPlaceholder)
                        .slideDown(self.options.editSpeed);
                }

                /**
                 * Run the callback function.
                 **/
                if (typeof self.options.onEdit == 'function') {
                    self.options.onEdit.call(this, tDashlet);
                }

                e.preventDefault();
            });

            /**
             * Update the dashlets title by using the edit input.
             **/
            $(self.options.editPlaceholder)
                .find('input')
                .keyup(function () {
                    $(this)
                        .parents(self.options.dashlets)
                        .children('header')
                        .children('h2')
                        .text($(this)
                            .val());
                });

            /**
             * Set a custom style.
             **/
            self.dashlet.on(clickEvent, '[data-dashlet-setstyle]', function (e) {

                var val = $(this)
                    .data('dashlet-setstyle');
                var styles = '';

                /**
                 * Get all other styles, in order to remove it.
                 **/
                $(this)
                    .parents(self.options.editPlaceholder)
                    .find('[data-dashlet-setstyle]')
                    .each(function () {
                        styles += $(this)
                            .data('dashlet-setstyle') + ' ';
                    });

                /**
                 * Set the new style.
                 **/
                $(this)
                    .parents(self.options.dashlets)
                    .attr('data-dashlet-attstyle', '' + val + '')
                    .removeClassPrefix('dashlet-color-')
                    .addClass(val);

                /**
                 * Run function for the indicator image.
                 **/
                self._runLoaderDashlet($(this));

                /**
                 * Lets save the setings.
                 **/
                self._saveSettingsDashlet();

                e.preventDefault();
            });

            //*****************************************************************//
            /////////////////////////// CUSTOM ACTION ///////////////////////////
            //*****************************************************************//

            /**
             * Allow users to show/hide a edit box.
             **/
            self.dashlet.on(clickEvent, '.dashlet-custom-btn', function (e) {

                var w = $(this)
                    .parents(self.options.dashlets);

                /**
                 * Run function for the indicator image.
                 **/
                self._runLoaderDashlet($(this));

                /**
                 * Start and end custom action.
                 **/
                if ($(this)
                    .children('.' + self.customClass[0])
                    .length) {
                    $(this)
                        .children()
                        .removeClass(self.customClass[0])
                        .addClass(self.customClass[1]);

                    /**
                     * Run the callback function.
                     **/
                    if (typeof self.options.customStart == 'function') {
                        self.options.customStart.call(this, w);
                    }
                } else {
                    $(this)
                        .children()
                        .removeClass(self.customClass[1])
                        .addClass(self.customClass[0]);

                    /**
                     * Run the callback function.
                     **/
                    if (typeof self.options.customEnd == 'function') {
                        self.options.customEnd.call(this, w);
                    }
                }

                /**
                 * Lets save the setings.
                 **/
                self._saveSettingsDashlet();

                e.preventDefault();
            });

            //*****************************************************************//
            /////////////////////////// DELETE WIDGETS //////////////////////////
            //*****************************************************************//

            /**
             * Allow users to delete the dashlets.
             **/
            self.dashlet.on(clickEvent, '.dashlet-delete-btn', function (e) {

                var tDashlet = $(this)
                    .parents(self.options.dashlets);
                var removeId = tDashlet.attr('id');
                var widTitle = tDashlet.children('header')
                    .children('h2')
                    .text();

                /**
                 * Delete the dashlets with a confirm popup.
                 **/

                        /**
                         * Run function for the indicator image.
                         **/
                        self._runLoaderDashlet($(this));

                        /**
                         * Delete the right dashlet.
                         **/
                        $('#' + removeId)
                            .fadeOut(self.options.deleteSpeed, function () {

                                $(this)
                                    .remove();

                                /**
                                 * Run the callback function.
                                 **/
                                if (typeof self.options.onDelete == 'function') {
                                    self.options.onDelete.call(this, tDashlet);
                                }
                            });

                e.preventDefault();
            });

            //******************************************************************//
            /////////////////////////// REFRESH BUTTON ///////////////////////////
            //******************************************************************//

            /**
             * Refresh ajax upon clicking refresh link.
             **/
            self.dashlet.on(clickEvent, '.dashlet-refresh-btn', function (e) {

                /**
                 * Variables.
                 **/
                var rItem = $(this)
                    .parents(self.options.dashlets),
                    pathToFile = rItem.data('dashlet-load'),
                    ajaxLoader = rItem.children(),
                    btn = $(this);

                /**
                 * Run the ajax function.
                 **/
                btn.button('loading');
                ajaxLoader.addClass("dashlet-body-ajax-loading");
                setTimeout(function () {
                    btn.button('reset');
                    ajaxLoader.removeClass("dashlet-body-ajax-loading");
                    self._loadAjaxFile(rItem, pathToFile, ajaxLoader);

                }, 1000)

                e.preventDefault();
            });
        },

        /**
         * Destroy.
         *
         * @param:
         **/
        destroy: function () {
            var self = this;
            self.dashlet.off('click', self._clickEvents());
            self.obj.removeData(pluginName);
        }
    };

    $.fn[pluginName] = function (option) {
        return this.each(function () {
            var $this = $(this);
            var data = $this.data(pluginName);
            var options = typeof option == 'object' && option;
            if (!data) {
                $this.data(pluginName, (data = new Dashlet(this, options)))
            }
            if (typeof option == 'string') {
                data[option]();
            }
        });
    };

    /**
     * Default settings(dont change).
     * You can globally override these options
     * by using $.fn.pluginName.key = 'value';
     **/

    $.fn[pluginName].defaults = {
        grid: 'section',
        dashlets: '.dashlet',
        localStorage: true,
        deleteSettingsKey: '',
        settingsKeyLabel: 'Reset settings?',
        deletePositionKey: '',
        positionKeyLabel: 'Reset position?',
        sortable: true,
        buttonsHidden: false,
        toggleButton: true,
        toggleClass: 'min-10 | plus-10',
        toggleSpeed: 200,
        onToggle: function () {},
        deleteButton: true,
        deleteClass: 'trashcan-10',
        deleteSpeed: 200,
        onDelete: function () {},
        editButton: true,
        editPlaceholder: '.dashlet-editbox',
        editClass: 'pencil-10 | delete-10',
        editSpeed: 200,
        onEdit: function () {},
        colorButton: true,
        fullscreenButton: true,
        fullscreenClass: 'fullscreen-10 | normalscreen-10',
        fullscreenDiff: 3,
        onFullscreen: function () {},
        customButton: true,
        customClass: '',
        customStart: function () {},
        customEnd: function () {},
        buttonOrder: '%refresh% %delete% %custom% %edit% %fullscreen% %toggle%',
        opacity: 1.0,
        dragHandle: '> header',
        placeholderClass: 'dashlet-placeholder',
        indicator: true,
        indicatorTime: 600,
        ajax: true,
        loadingLabel: 'loading...',
        timestampPlaceholder: '.dashlet-timestamp',
        timestampFormat: 'Last update: %m%/%d%/%y% %h%:%i%:%s%',
        refreshButton: true,
        refreshButtonClass: 'refresh-10',
        labelError: 'Sorry but there was a error:',
        labelUpdated: 'Last Update:',
        labelRefresh: 'Refresh',
        labelDelete: 'Delete dashlet:',
        afterLoad: function () {},
        rtl: false,
        onChange: function () {},
        onSave: function () {},
        ajaxnav: true
    };

    /*
     * REMOVE CSS CLASS WITH PREFIX
     * Description: Remove classes that have given prefix. You have an element with classes
     * 				"dashlet dashlet-color-red"
     * Usage: $elem.removeClassPrefix('dashlet-color-');
     */

    $.fn.removeClassPrefix = function (prefix) {

        this.each(function (i, it) {
            var classes = it.className.split(" ")
                .map(function (item) {
                    return item.indexOf(prefix) === 0 ? "" : item;
                });
            //it.className = classes.join(" ");
            it.className = $.trim(classes.join(" "));

        });

        return this;
    }
})(jQuery, window, document);