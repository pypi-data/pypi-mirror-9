/*
 * MyAMS extensions for widgets handling
 * Version 0.1.0
 * ©2014 Thierry Florac <tflorac@ulthar.net>
 */

(function($) {

	/* Private functions */
	function checkValue(value) {
		if (value < 10)
			value = '0' + value;
		return value;
	}

	function getPastTimeStamp(value, options) {
		var date = new Date(value);
		var month = checkValue(date.getMonth() + 1);
		var day = checkValue(date.getDate());
		var year = checkValue(date.getFullYear());
		var hours = checkValue(date.getHours());
		var minutes = checkValue(date.getMinutes());
		var seconds = checkValue(date.getSeconds());
		return options.timestampFormat.replace(/%d%/g, day)
									  .replace(/%m%/g, month)
									  .replace(/%y%/g, year)
									  .replace(/%h%/g, hour)
									  .replace(/%i%/g, minutes)
									  .replace(/%s%/g, seconds);
	}


	function Widget(element, options) {
		this.widget = element;
		this.options = $.extend({}, MyAMSWidget.defaults, options);
		this.grid = this.widget.parents(this.options.grid);
		this.hasGrid = this.grid.exists();
		this.gridId = this.grid.attr('id');
		this.controls = this.options.controls;
		this.toggleClass = this.options.toggleClass.split('|');
		this.editClass = this.options.editClass.split('|');
		this.fullscreenClass = this.options.fullscreenClass.split('|');
		this.customClass = this.options.customClass.split('|');
		this.init();
	}


	Widget.prototype = {

		init: function() {
			var self = this;
			if (self.options.rtl === true)
				$('body').addClass('rtl');
			self.grid.each(function() {
				$(this).addClass('sortable-grid');
			});
			self._getSettings();
			if (self.hasGrid && self.storage) {
				if (self.position) {
					var position = JSON.parse(self.position);
					for (var key in position.grid) {
						var changeOrder = self.grid.find(self.options.subgrid + '.sortable-grid').eq(key);
						for (var key2 in position.grid[key].section)
							changeOrder.append($('#' + position.grid[key].section[key2].id));
					}
				}
				if (self.settings) {
					var settings = JSON.parse(self.settings);
					for (var key in settings.widget) {
						var widget = settings.widget[key];
						var widgetId = $('#' + widget.id);
						if (widget.style)
							widgetId.removeClassPrefix('ams-widget-color-')
									.addClass(widget.style)
									.attr('data-widget-attstyle', widget.style);
						if (widget.hidden == 1)
							widgetId.hide(1);
						else
							widgetId.show(1)
									.removeAttr('data-widget-hidden');
						if (widget.collapsed == 1)
							widgetId.addClass('ams-widget-collapsed')
									.children('div')
									.hide(1);
						var title = widgetId.children('header').children('h2');
						if (title.text() != widget.title)
							title.text(widget.title);
					}
				}
			}
			var widget = self.widget;
			var data = widget.data();
			var data_options = {
				grid: data.amsWidgetGrid,
				subgrid: data.amsWudgetSubgrid,
				widgets: data.amsWidgetWidgets,
				controls: data.amsWidgetControls,
				storage: data.amsWidgetStorage,
				deleteSettingsKey: data.amsWidgetDeleteSettingsKey,
				deletePositionKey: data.amsWidgetDeletePositionKey,
				sortable: data.amsWidgetSortable,
				hiddenButtons: data.amsWidgetHiddenButtons,
				toggleButton: data.amsWidgetToggleButton,
				toggleClass: data.amsWidgetToggleClass,
				onToggle: MyAMS.getFunctionByName(data.amsWidgetToggleCallback),
				deleteButton: data.amsWidgetDeleteButton,
				deleteClass: data.amsWidgetDeleteClass,
				onDelete: MyAMS.getFunctionByName(data.amsWidgetDeleteCallback),
				editButton: data.amsWidgetEditButton,
				editPlaceholder: data.amsWidgetEditPlaceholder,
				editClass: data.amsWidgetEditClass,
				onEdit: MyAMS.getFunctionByName(data.amsWidgetEditCallback),
				fullscreenButton: data.amsWidgetFullscreenButton,
				fullscreenClass: data.amsWidgetFullscreenClass,
				fullscreenDiff: data.amsWidgetFullscreenDiff,
				onFullscreen: MyAMS.getFunctionByName(data.amsWidgetFullscreenCallback),
				customButton: data.amsWidgetCustomButton,
				customClass: data.amsWidgetCustomClass,
				customStart: MyAMS.getFunctionByName(data.amsWidgetCustomStartCallback),
				customEnd: MyAMS.getFunctionByName(data.amsWidgetCustomEndCallback),
				buttonsOrder: data.amsWidgetButtonsOrder,
				opacity: data.amsWidgetOpacity,
				dragHandle: data.amsWidgetDragHandle,
				placeholderClass: data.amsWidgetPlaceholderClass,
				indicator: data.amsWidgetIndicator,
				indicatorTime: data.amsWidgetIndicatorTime,
				ajax: data.amsWidgetAjax,
				timestampPlaceholder : data.amsWidgetTimestampPlaceholder,
				timestampFormat : data.amsWidgetTimestampFormat,
				refreshButton : data.amsWidgetRefreshButton,
				refreshClass : data.amsWidgetRefreshClass,
				errorLabel : data.amsWidgetErrorLabel,
				updatedLabel : data.amsWidgetUpdatedLabel,
				refreshLabel : data.amsWidgetRefreshLabel,
				deleteLabel : data.amsWidgetDeleteLabel,
				afterLoad : MyAMS.getFunctionByName(data.amsWidgetAfterLoadCallback),
				rtl : data.amsWidgetRtl,
				onChange : MyAMS.getFunctionByName(data.amsWidgetChangeCallback),
				onSave : MyAMS.getFunctionByName(data.amsWidgetSaveCallback),
				ajax_nav : MyAMS.ajax_nav
			};
			var widgetOptions = $.extend({}, self.options, data_options);
			var header = widget.children('header');
			if (!header.parent().attr('role')) {
				if (data.widgetHidden === true)
					widget.hide();
				if (data.widgetCollapsed === true)
					widget.addClass('ams-widget-collapsed')
						  .children('div').hide();
				if (widgetOptions.customButton &&
					(data.widgetCustombutton === undefined) &&
					(self.customClass[0].length != 0))
					var customBtn = '<a href="#" class="button-icon ams-widget-custom-btn"><i class="' + self.customClass[0] + '"></i></a>';
				else
					customBtn = "";
				if (widgetOptions.deleteButton && (data.widgetDeleteButton === undefined))
					var deleteBtn = '<a href="#" class="button-icon ams-widget-delete-btn hint" title="' + MyAMSWidget.i18n.DELETE_BTN + '" data-ams-hint-gravity="se">' +
									'<i class="' + widgetOptions.deleteClass + '"></i></a>';
				else
					deleteBtn = "";
				if (widgetOptions.editButton && (data.widgetEditButton === undefined)) {
					var editClass = widgetOptions.editClass.split('|')[0];
					var editBtn = '<a href="#" class="button-icon ams-widget-edit-btn hint" title="' + MyAMSWidget.i18n.EDIT_BTN + '" data-ams-hint-gravity="se">' +
								  '<i class="' + editClass + '"></i></a>';
				} else
					editBtn = "";
				if (widgetOptions.fullscreenButton && (data.widgetFullscreenButton === undefined)) {
					var fullscreenClass = widgetOptions.fullscreenClass.split('|')[0];
					var fullscreenBtn = '<a href="#" class="button-icon ams-widget-fullscreen-btn hint" title="' + MyAMSWidget.i18n.FULLSCREEN_BTN + '" data-ams-hint-gravity="se">' +
										'<i class="' + fullscreenClass + '"></i></a>';
				} else
					fullscreenBtn = "";
				if (widgetOptions.toggleButton && (data.widgetToggleButton === undefined)) {
					var toggleClass = widgetOptions.toggleClass.split('|');
					if ((widget.dataWidgetCollapsed === true) ||
						widget.hasClass('ams-widget-collapsed'))
						var toggleSettings = toggleClass[1];
					else
						toggleSettings = toggleClass[0];
					var toggleBtn = '<a href="#" class="button-icon ams-widget-toggle-btn hint" title="' + MyAMSWidget.i18n.COLLAPSE_BTN + '" data-ams-hint-gravity="se">' +
									'<i class="' + toggleSettings + '"></i></a>';
				} else
					toggleBtn = "";
				if (widgetOptions.refreshButton &&
					(data.widgetRefreshButton === undefined) &&
					data.widgetLoad)
					var refreshBtn = '<a href="#" class="button-icon ams-widget-refresh-btn hint" title="' + MyAMSWidget.i18n.REFRESH_BTN + '" data-loading-text="&nbsp;&nbsp;' + MyAMSWidget.i18n.LOADING_MSG + '&nbsp;" data-ams-hint-gravity="se">' +
									 '<i class="' + widgetOptions.refreshClass + '"></i></a>';
				else
					refreshBtn = "";
				var buttons = widgetOptions.buttonsOrder.replace(/%refresh%/, refreshBtn)
														 .replace(/%custom%/, customBtn)
														 .replace(/%edit%/, editBtn)
														 .replace(/%toggle%/, toggleBtn)
														 .replace(/%fullscreen%/, fullscreenBtn)
														 .replace(/%delete%/, deleteBtn);
				if (refreshBtn || customBtn || editBtn || toggleBtn || fullscreenBtn || deleteBtn)
					header.prepend('<div class="ams-widget-ctrls">' + buttons + '</div>');
				if (widgetOptions.sortable && (data.widgetSortable === undefined))
					widget.addClass('ams-widget-sortable');
				var placeholder = widget.find(widgetOptions.editPlaceholder);
				if (placeholder.length > 0)
					placeholder.find('input').val($.trim(header.children('h2').text()));
				header.append('<span class="ams-widget-loader"><i class="fa fa-refresh fa-spin"></i></span>');
				widget.attr('role', 'widget')
					  .children('div').attr('role', 'content')
					  .prev('header').attr('role', 'heading')
					  .children('div').attr('role', 'menu');
				MyAMS.plugins.enabled.hint(header);
			}
			widget.data('widget-options', widgetOptions);
			if (self.options.hiddenButtons)
				$(self.controls).hide();
			widget.find("[data-widget-load]").each(function() {
				var item = $(this),
					header = item.children(),
					path = item.data('widget-load'),
					reloadTime = item.data('widget-refresh') * 1000,
					loader = header;
				if (item.find('.ams-widget-ajax-placeholder').length <= 0) {
					item.children('widget-body').append('<div class="ams-widget-ajax-placeholder">' + self.options.loadingLabel + "</div>");
					if (reloadTime > 0) {
						self.loadAjaxFile(item, path, header);
						setInterval(function() {
							self._loadAjaxFile(item, path, header);
						}, reloadTime);
					} else
						self._loadAjaxFile(item, path, header);
				}
			});
			if (self.options.hiddenButtons) {
				self.widget.children('header').hover(function() {
					$(this).children(self.controls).stop(true, true).fadeTo(100, 1);
				}, function() {
					$(this).children(self.controls).stop(true, true).fadeTo(100, 0);
				});
			}
			self._setClickEvents();
			$(self.options.deleteSettingsKey).on(self.clickEvent, this, function(e) {
				if (self.storage) {
					var cleared = confirm(self.options.settingsKeyLabel);
					if (cleared)
						self.storage.removeItem(self.settingsKey);
				}
				e.preventDefault();
			});
			$(self.options.deletePositionKey).on(self.clickEvent, this, function(e) {
				if (self.storage) {
					var cleared = confirm(self.options.positionKeyLabel);
					if (cleared)
						self.storage.removeItem(self.positionKey);
				}
				e.preventDefault();
			});
			if (self.storage) {
				if (self.settingsKey === null || self.settingsKey.length < 1)
					self._saveWidgetSettings();
				if (self.positionKey === null || self.positionKey.length < 1)
					self._saveWidgetPosition();
			}
			self.grid.data('ams-widgets-loaded', true);
		},

		destroy: function() {
			var self = this;
			self.widgets.off('click', self._setClickEvents());
			self.element.removeData('AMSWidget');
		},

		_getSettings: function() {
			var self = this;
			if (!self.hasGrid || !self.gridId)
				self.storage = null;
			else {
				switch (self.options.storage) {
					case 'local':
						self.storage = localStorage;
						break;
					case 'session':
						self.storage = sessionStorage;
						break;
					default:
						self.storage = null;
				}
			}
			var use_storage = (self.storage != null) && function() {
				var result,
					uid = +new Date;
				try {
					self.storage.setItem(uid, uid);
					result = self.storage.getItem(uid) == uid;
					self.storage.removeItem(uid);
					return result
				} catch (e) {}
			}();
			if (use_storage) {
				self.settingsKey = "AMS_settings_" + location.pathname + location.hash + "_" + self.gridId;
				self.settings = self.storage.getItem(self.settingsKey);
				self.positionKey = "AMS_position_" + location.pathname + location.hash + "_" + self.gridId;
				self.position = self.storage.getItem(self.positionKey);
			}
			if (("ontouchstart" in window) || window.DocumentTouch && document instanceof DocumentTouch) {
				self.clickEvent = "touchstart"
			} else {
				self.clickEvent = "click"
			}
		},

		_runLoaderWidget: function(widget) {
			var self = this;
			if (self.options.indicator)
				widget.find('.ams-widget-loader')
					  .stop(true, true)
					  .fadeIn(100)
					  .delay(self.options.indicatorTime)
					  .fadeOut(100);
		},

		_loadAjaxFile: function(url, widget, loader) {
			MyAMS.skin.loadURL(url, widget.find('.widget-body'));
		},

		_saveWidgetSettings: function() {
			var self = this;
			self._getSettings();
			if (self.storage) {
				var gridSettings = [];
				self.grid.find(self.options.widgets).each(function() {
					var widget = $(this);
					var widgetSettings = {};
					widgetSettings.id = widget.attr('id');
					widgetSettings.style = widget.attr('data-widget-attstyle');
					widgetSettings.title = widget.children('header').children('h2').text();
					widgetSettings.hidden = widget.is(':hidden') ? 1 : 0;
					widgetSettings.collapsed = widget.hasClass('ams-widget-collapsed') ? 1 : 0;
					gridSettings.push(widgetSettings);
				});
				var gridSettingsStr = JSON.stringify({widget: gridSettings});
				if (self.settings != gridSettingsStr)
					self.storage.setItem(self.settingsKey, gridSettingsStr);
				if (typeof(self.options.onSave) == 'function')
					self.options.onSave.call(this, null, gridSettings);
			}
		},

		_saveWidgetPosition: function() {
			var self = this;
			self._getSettings();
			if (self.storage) {
				var gridPosition = [];
				self.grid.find(self.options.subgrid + ".sortable-grid").each(function () {
					var subgridPosition = [];
					$(this).children(self.options.widgets).each(function () {
						var subObj = {};
						subObj.id = $(this).attr("id");
						subgridPosition.push(subObj)
					});
					var out = {section: subgridPosition};
					gridPosition.push(out)
				});
				var gridPositionStr = JSON.stringify({grid: gridPosition});
				if (self.position != gridPositionStr)
					self.storage.setItem(self.positionKey, gridPositionStr);
				if (typeof(self.options.onSave) == 'function')
					self.options.onSave.call(this, null, gridPosition);
			}
		},

		_setClickEvents: function() {

			function setFullscreenHeight() {
				if ($('#ams-widget-fullscreen-mode').length > 0) {
					var widgets = $('#ams-widget-fullscreen-mode').find(self.options.widgets);
					var windowHeight = $(window).height();
					var headerHeight = widgets.children('header')
											  .height();
					widgets.children('div')
						   .height(windowHeight - headerHeight - 15);
				}
			}

			var self = this;
			self._getSettings();

			// Toggle button
			self.widget.on(self.clickEvent, '.ams-widget-toggle-btn', function(e) {
				e.preventDefault();
				var button = $(this);
				var widget = button.parents(self.options.widgets);
				var widgetOptions = widget.data('widget-options');
				var toggleClass = widgetOptions.toggleClass.split('|');
				self._runLoaderWidget(widget);
				var canToggle = true;
				if (widget.hasClass('ams-widget-collapsed')) {
					if (widgetOptions.onToggle)
						canToggle = widgetOptions.onToggle.call(this, widget, 'expand');
					if (canToggle !== false) {
						button.children().removeClass(toggleClass[1])
										 .addClass(toggleClass[0]);
						widget.removeClass('ams-widget-collapsed')
							  .children('[role=content]').slideDown(widgetOptions.toggleSpeed, function() {
									self._saveWidgetSettings();
							  });
					}
				} else {
					if (widgetOptions.onToggle)
						canToggle = widgetOptions.onToggle.call(this, widget, 'collapse');
					if (canToggle !== false) {
						button.children().removeClass(toggleClass[0])
										 .addClass(toggleClass[1]);
						widget.addClass('ams-widget-collapsed')
							  .children('[role=content]').slideUp(widgetOptions.toggleSpeed, function() {
								self._saveWidgetSettings();
							  });
					}
				}
			});
			self.widget.on('dblclick', 'header', function(e) {
				$('.ams-widget-toggle-btn', this).click();
			});

			// Fullscreen button
			self.widget.on(self.clickEvent, '.ams-widget-fullscreen-btn', function(e) {
				e.preventDefault();
				var button = $(this);
				var widget = button.parents(self.options.widgets);
				var widgetOptions = widget.data('widget-options');
				var fullscreenClass = widgetOptions.fullscreenClass.split('|');
				var content = widget.children('div');
				self._runLoaderWidget(widget);
				if ($('#ams-widget-fullscreen-mode').length > 0) {
					$('.nooverflow').removeClass('nooverflow');
					widget.unwrap('<div>')
						  .children('div')
						  .removeAttr('style')
						  .end()
						  .find('.ams-widget-fullscreen-btn')
						  .children()
						  .removeClass(fullscreenClass[1])
						  .addClass(fullscreenClass[0])
						  .parents(self.controls)
						  .children('a')
						  .show();
					if (content.hasClass('ams-widget-visible'))
						content.hide()
							   .removeClass('ams-widget-visible');
				} else {
					$('body').addClass('nooverflow');
					widget.wrap('<div id="ams-widget-fullscreen-mode"></div>')
						  .parent()
						  .find('.ams-widget-fullscreen-btn')
						  .children()
						  .removeClass(fullscreenClass[0])
						  .addClass(fullscreenClass[1])
						  .parents(self.controls)
						  .children('a:not(.ams-widget-fullscreen-btn)')
						  .hide();
					if (content.is(':hidden'))
						content.show()
							   .addClass('ams-widget-visible');
				}
				setFullscreenHeight();
				if (typeof(widgetOptions.onFullscreen) == 'function')
					widgetOptions.onFullscreen.call(this, widget);
			});
			$(window).resize(function() {
				setFullscreenHeight();
			});

			// Edit button
			self.widget.on(self.clickEvent, '.ams-widget-edit-btn', function(e) {
				e.preventDefault();
				var button = $(this);
				var widget = button.parents(self.options.widgets);
				var widgetOptions = widget.data('widget-options');
				var editClass = widgetOptions.editClass.split('|');
				self._runLoaderWidget(widget);
				var placeholder = widget.find(widgetOptions.editPlaceholder);
				if (placeholder.is(':visible')) {
					button.children()
						  .removeClass(editClass[1])
						  .addClass(editClass[0]);
					placeholder.slideUp(widgetOptions.editSpeed, function() {
						self._saveWidgetSettings();
					});
				} else {
					button.children()
						  .removeClass(editClass[0])
						  .addClass(editClass[1]);
					placeholder.slideDown(widgetOptions.editSpeed);
				}
				if (typeof(widgetOptions.onEdit) == 'function')
					widgetOptions.onEdit.call(this, widget);
			});
			$(self.options.editPlaceholder).find('input').keyup(function() {
				$(this).parents(self.options.widgets)
					   .children('header')
					   .children('h2')
					   .text($(this).val());
			});

			// Custom button
			self.widget.on(self.clickEvent, '.ams-widget-custom-btn', function(e) {
				e.preventDefault();
				var button = $(this);
				var widget = button.parents(self.options.widgets);
				var widgetOptions = widget.data('widget-options');
				var customClass = widgetOptions.customClass.split('|');
				self._runLoaderWidget(widget);
				if (button.children('.' + customClass[0]).length > 0) {
					button.children()
						  .removeClass(customClass[0])
						  .addClass(customClass[1]);
					if (typeof(widgetOptions.customStart) == 'function')
						widgetOptions.customStart.call(this, widget);
				} else {
					button.children('.' + customClass[1])
						  .addClass(customClass[0]);
					if (typeof(widgetOptions.customEnd) == 'function')
						widgetOptions.customEnd.call(this, widget);
				}
				self._saveWidgetSettings();
			});

			// Delete button
			self.widget.on(self.clickEvent, '.ams-widget-delete-btn', function(e) {
				e.preventDefault();
				var button = $(this);
				var widget = button.parents(self.options.widgets);
				var widgetOptions = widget.data('widget-options');
				var wId = widget.attr('id');
				var title = widget.children('header').children('h2').text();
				MyAMS.ajax.check(MyAMS.notify,
								   MyAMS.baseURL + 'myams-notify' + (MyAMS.devmode ? '.js' : '.min.js'),
								   function() {
										MyAMS.notify.messageBox({
											title: '<i class="fa fa-times" style="color: #ed1c24;"></i> ' + widgetOptions.deleteLabel + ' "' + title + '"',
											content: MyAMSWidget.i18n.DELETE_MSG,
											buttons: "[" + MyAMS.i18n.BTN_OK + "][" + MyAMS.i18n.BTN_CANCEL + "]"
										}, function(buttonPressed) {
											if (buttonPressed == MyAMS.i18n.BTN_OK) {
												self._runLoaderWidget(widget);
												$('#' + wId).fadeOut(widgetOptions.deleteSpeed, function() {
													button.remove();
													if (typeof(widgetOptions.onDelete) == 'function')
														widgetOptions.onDelete.call(this, widget);
												});
											}
										});
								   });
			});

			// Refresh button
			self.widget.on(self.clickEvent, '.ams-widget-refresh-btn', function(e) {
				e.preventDefault();
				var button = $(this);
				var widget = button.parents(self.options.widgets);
				var path = widget.data('widget-load');
				var loader = widget.children();
				button.button('loading');
				loader.addClass('widget-body-ajax-loading');
				setTimeout(function() {
					button.button('reset');
					loader.removeClass('widget-body-ajax-loading');
					self._loadAjaxFile(widget, path, loader);
				}, 1000);
			});
		}
	}


	MyAMSWidget = {

		i18n: $.extend({
			SETTINGS_KEY_LABEL: "Reset settings?",
			POSITION_KEY_LABEL: "Reset position?",
			TIMESTAMP_FORMAT: "Last update: %d%/%m%/%y% %h%:%i%:%s",
			ERROR_LABEL: "An error occured: ",
			UPDATED_LABEL: "Last update: ",
			REFRESH_LABEL: "Refresh",
			EDIT_BTN: "Edit title",
			DELETE_BTN: "Delete",
			DELETE_LABEL: "Remove component: ",
			DELETE_MSG: "WARNING: this action can't be undone!",
			FULLSCREEN_BTN: "Fullscreen",
			COLLAPSE_BTN: "Collapse",
			REFRESH_BTN: "Reload content",
			LOADING_MSG: "Loading..."
		}, MyAMS.plugins.i18n.widgets),

		initWidgetsGrid: function(grid) {
			if (!grid.exists())
				return;
			var options = $('.ams-widget:first', grid).data('AMSWidget').options;
			if (options.sortable && $.ui) {
				var sortItem = grid.find('.sortable-grid').not("[data-widget-excludegrid]");
				sortItem.sortable({
					items: sortItem.find('.ams-widget-sortable'),
					connectWith: sortItem,
					placeholder: options.placeholderClass,
					cursor: 'move',
					revert: true,
					opacity: options.opacity,
					delay: 200,
					cancel: '.button-icon, #ams-widget-fullscreen-mode >div',
					zIndex: 10000,
					handle: options.dragHandle,
					forcePlaceholderSize: true,
					forceHelperSize: true,
					update: function(event, ui) {
						var widget = ui.item.data('AMSWidget');
						widget._runLoaderWidget(widget.widget);
						widget._saveWidgetPosition();
						if (typeof(options.onChange) == 'function')
							options.onChange.call(this, ui.item);
					}
				});
			}
		}
	}


	MyAMSWidget.defaults = {
		grid: '.ams-widget-grid',
		subgrid: 'section',
		widgets: '.ams-widget',
		controls: '.ams-widget-ctrls',
		storage: 'local',
		deleteSettingsKey: '',
		settingsKeyLabel: MyAMSWidget.i18n.SETTINGS_KEY_LABEL,
		deletePositionKey: '',
		positionKeyLabel: MyAMSWidget.i18n.POSITION_KEY_LABEL,
		sortable: true,
		hiddenButtons: false,
		// Toggle button
		toggleButton: true,
		toggleClass: 'fa fa-minus|fa fa-plus',
		toggleSpeed: 200,
		onToggle: null,
		// Delete button
		deleteButton: false,
		deleteClass: 'fa fa-times',
		deleteSpeed: 200,
		onDelete: null,
		// Edit button
		editButton: false,
		editPlaceholder: '.ams-widget-editbox',
		editClass: 'fa fa-cog|fa fa-save',
		editSpeed: 200,
		onEdit: null,
		// Fullscreen button
		fullscreenButton: false,
		fullscreenClass: 'fa fa-expand|fa fa-compress',
		fullscreenDiff: 3,
		onFullscreen: null,
		// Custom button
		customButton: false,
		customClass: 'folder-10|next-10',
		customStart: null,
		customEnd: null,
		// Buttons order
		buttonsOrder: '%refresh% %custom% %edit% %toggle% %fullscreen% %delete%',
		opacity: 1.0,
		dragHandle: '> header',
		placeholderClass: 'ams-widget-placeholder',
		indicator: true,
		indicatorTime: 600,
		ajax: true,
		timestampPlaceholder : '.ams-widget-timestamp',
		timestampFormat : MyAMSWidget.i18n.TIMESTAMP_FORMAT,
		refreshButton : true,
		refreshButtonClass : 'fa fa-refresh',
		errorLabel : MyAMSWidget.i18n.ERROR_LABEL,
		updatedLabel : MyAMSWidget.i18n.UPDATED_LABEL,
		refreshLabel : MyAMSWidget.i18n.REFRESH_LABEL,
		deleteLabel : MyAMSWidget.i18n.DELETE_LABEL,
		afterLoad : null,
		rtl : false,
		onChange : null,
		onSave : null,
		ajax_nav : MyAMS.ajax_nav
	}


	$.fn.extend({

		MyAMSWidget: function(options) {
			return this.each(function() {
				var widget = $(this);
				var data = widget.data('AMSWidget');
				if (!data) {
					var grid = widget.parents(options.grid || MyAMSWidget.defaults.grid);
					var grid_options = {};
					if (grid.exists()) {
						var grid_data = grid.data();
						grid_options = {
							grid: grid_data.amsWidgetGrid,
							subgrid: grid_data.amsWidgetSubgrid,
							controls: grid_data.amsWidgetControls,
							storage: grid_data.amsWidgetStorage,
							deleteSettingsKey: grid_data.amsWidgetDeleteSettingsKey,
							deletePositionKey: grid_data.amsWidgetDeletePositionKey,
							sortable: grid_data.amsWidgetSortable,
							hiddenButtons: grid_data.amsWidgetHiddenButtons,
							toggleButton: grid_data.amsWidgetToggleButton,
							toggleClass: grid_data.amsWidgetToggleClass,
							onToggle: MyAMS.getFunctionByName(grid_data.amsWidgetToggleCallback),
							deleteButton: grid_data.amsWidgetDeleteButton,
							deleteClass: grid_data.amsWidgetDeleteClass,
							onDelete: MyAMS.getFunctionByName(grid_data.amsWidgetDeleteCallback),
							editButton: grid_data.amsWidgetEditButton,
							editPlaceholder: grid_data.amsWidgetEditPlaceholder,
							editClass: grid_data.amsWidgetEditClass,
							onEdit: MyAMS.getFunctionByName(grid_data.amsWidgetEditCallback),
							fullscreenButton: grid_data.amsWidgetFullscreenButton,
							fullscreenClass: grid_data.amsWidgetFullscreenClass,
							fullscreenDiff: grid_data.amsWidgetFullscreenDiff,
							onFullscreen: MyAMS.getFunctionByName(grid_data.amsWidgetFullscreenCallback),
							customButton: grid_data.amsWidgetCustomButton,
							customClass: grid_data.amsWidgetCustomClass,
							customStart: MyAMS.getFunctionByName(grid_data.amsWidgetCustomStartCallback),
							customEnd: MyAMS.getFunctionByName(grid_data.amsWidgetCustomStartCallback),
							buttonsOrder: grid_data.amsWidgetButtonsOrder,
							opacity: grid_data.amsWidgetOpacity,
							dragHandle: grid_data.amsWidgetDragHandle,
							placeholderClass: grid_data.amsWidgetPlaceholderClass,
							indicator: grid_data.amsWidgetIndicator,
							indicatorTime: grid_data.amsWidgetIndicatorTime,
							ajax: grid_data.amsWidgetAjax,
							timestampPlaceholder : grid_data.amsWidgetTimestampPlaceholder,
							timestampFormat : grid_data.amsWidgetTimestampFormat,
							refreshButton : grid_data.amsWidgetRefreshButton,
							refreshClass : grid_data.amsWidgetRefreshClass,
							errorLabel : grid_data.amsWidgetErrorLabel,
							updatedLabel : grid_data.amsWidgetUpdatedLabel,
							refreshLabel : grid_data.amsWidgetRefreshLabel,
							deleteLabel : grid_data.amsWidgetDeleteLabel,
							afterLoad : MyAMS.getFunctionByName(grid_data.amsWidgetAfterLoadCallback),
							rtl : grid_data.amsWidgetRtl,
							onChange : MyAMS.getFunctionByName(grid_data.amsWidgetChangeCallback),
							onSave : MyAMS.getFunctionByName(grid_data.amsWidgetSaveCallback),
							ajax_nav : MyAMS.ajax_nav
						};
					}
					var settings = $.fn.extend({}, grid_options, widget.data('ams-widget-options') || {}, options);
					widget.data('AMSWidget', new Widget(widget, settings));
				}
			});
		}

	});

})(jQuery);
