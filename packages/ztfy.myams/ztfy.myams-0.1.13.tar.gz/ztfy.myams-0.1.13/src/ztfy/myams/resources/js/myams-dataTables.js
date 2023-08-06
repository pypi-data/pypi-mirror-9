/*
 * MyAMS extensions to jquery-dataTables plug-in
 * Version 0.1.0
 * ©2014-2015 Thierry Florac <tflorac@ulthar.net>
 */


(function($) {

	/**
	 * Update default values for DataTables initialization
	 */
	$.extend(true, $.fn.dataTable.defaults, {
		"sDom": "R<'dt-top-row'CLF>r<'dt-wrapper't><'dt-row dt-bottom-row'<'row'<'col-sm-6'i><'col-sm-6 text-right'p>>",
		"sPaginationType": "bootstrap",
		"oLanguage": {
			"sLengthMenu": "_MENU_",
			"sSearch": "_INPUT_"
		}
	});


	/**
	 * Default class modification
	 */
	$.extend($.fn.dataTableExt.oStdClasses, {
		"sWrapper": "dataTables_wrapper form-inline"
	});


	/**
	 * API method to get paging information
	 */
	$.fn.dataTableExt.oApi.fnPagingInfo = function (oSettings) {
		return {
			"iStart":         oSettings._iDisplayStart,
			"iEnd":           oSettings.fnDisplayEnd(),
			"iLength":        oSettings._iDisplayLength,
			"iTotal":         oSettings.fnRecordsTotal(),
			"iFilteredTotal": oSettings.fnRecordsDisplay(),
			"iPage":          oSettings._iDisplayLength === -1 ? 0 : Math.ceil( oSettings._iDisplayStart / oSettings._iDisplayLength ),
			"iTotalPages":    oSettings._iDisplayLength === -1 ? 0 : Math.ceil( oSettings.fnRecordsDisplay() / oSettings._iDisplayLength )
		};
	};


	/**
	 * Bootstrap style pagination control
	 */
	$.extend($.fn.dataTableExt.oPagination, {
		"bootstrap": {
			"fnInit": function(oSettings, nPaging, fnDraw) {
				var oLang = oSettings.oLanguage.oPaginate;
				var fnClickHandler = function (e) {
					e.preventDefault();
					if (oSettings.oApi._fnPageChange(oSettings, e.data.action))
						fnDraw(oSettings);
				};

				$(nPaging).append(
					'<ul class="pagination">' +
						'<li class="prev disabled"><a href="#">' + oLang.sPrevious + '</a></li>' +
						'<li class="next disabled"><a href="#">' + oLang.sNext + '</a></li>' +
					'</ul>'
				);
				var els = $('a', nPaging);
				$(els[0]).on('click.DT', { action: "previous" }, fnClickHandler);
				$(els[1]).on('click.DT', { action: "next" }, fnClickHandler);
			},

			"fnUpdate": function (oSettings, fnDraw) {
				var iListLength = 5;
				var oPaging = oSettings.oInstance.fnPagingInfo();
				var an = oSettings.aanFeatures.p;
				var i,
					j,
					sClass,
					iStart,
					iEnd,
					iLen,
					iHalf=Math.floor(iListLength/2);

				if (oPaging.iTotalPages < iListLength) {
					iStart = 1;
					iEnd = oPaging.iTotalPages;
				} else if (oPaging.iPage <= iHalf) {
					iStart = 1;
					iEnd = iListLength;
				} else if (oPaging.iPage >= (oPaging.iTotalPages-iHalf)) {
					iStart = oPaging.iTotalPages - iListLength + 1;
					iEnd = oPaging.iTotalPages;
				} else {
					iStart = oPaging.iPage - iHalf + 1;
					iEnd = iStart + iListLength - 1;
				}

				for (i=0, iLen=an.length ; i<iLen ; i++) {
					// Remove the middle elements
					$('li:gt(0)', an[i]).filter(':not(:last)').remove();

					// Add the new list items and their event handlers
					for (j=iStart ; j<=iEnd ; j++) {
						sClass = (j==oPaging.iPage+1) ? 'class="active"' : '';
						$('<li '+sClass+'><a href="#">'+j+'</a></li>')
							.insertBefore( $('li:last', an[i])[0] )
							.on('click', function (e) {
								e.preventDefault();
								oSettings._iDisplayStart = (parseInt($('a', this).text(),10)-1) * oPaging.iLength;
								fnDraw( oSettings );
							});
					}

					// Add / remove disabled classes from the static elements
					if (oPaging.iPage === 0)
						$('li:first', an[i]).addClass('disabled');
					else
						$('li:first', an[i]).removeClass('disabled');

					if (oPaging.iPage === oPaging.iTotalPages-1 || oPaging.iTotalPages === 0)
						$('li:last', an[i]).addClass('disabled');
					else
						$('li:last', an[i]).removeClass('disabled');
				}
			}
		}
	});


	/**
	 * Bootstrap style full pagination control
	 */
	$.extend( $.fn.dataTableExt.oPagination, {
		"bootstrap_full": {
			"fnInit": function(oSettings, nPaging, fnDraw) {
				var oLang = oSettings.oLanguage.oPaginate;
				var fnClickHandler = function (e) {
					e.preventDefault();
					if (oSettings.oApi._fnPageChange(oSettings, e.data.action))
						fnDraw(oSettings);
				};

				$(nPaging).append(
					'<ul class="pagination">' +
						'<li class="first disabled"><a href="#">' + oLang.sFirst + '</a></li>' +
						'<li class="prev disabled"><a href="#">' + oLang.sPrevious + '</a></li>' +
						'<li class="next disabled"><a href="#">' + oLang.sNext + '</a></li>' +
						'<li class="last disabled"><a href="#">' + oLang.sLast + '</a></li>' +
					'</ul>'
				);
				var els = $('a', nPaging);
				$(els[0]).on('click.DT', { action: "first" }, fnClickHandler);
				$(els[1]).on('click.DT', { action: "previous" }, fnClickHandler);
				$(els[2]).on('click.DT', { action: "next" }, fnClickHandler);
				$(els[3]).on('click.DT', { action: "last" }, fnClickHandler);
			},

			"fnUpdate": function (oSettings, fnDraw) {
				var iListLength = 5;
				var oPaging = oSettings.oInstance.fnPagingInfo();
				var an = oSettings.aanFeatures.p;
				var i,
					j,
					sClass,
					iStart,
					iLen,
					iEnd,
					iHalf=Math.floor(iListLength/2);

				if (oPaging.iTotalPages < iListLength) {
					iStart = 1;
					iEnd = oPaging.iTotalPages;
				} else if (oPaging.iPage <= iHalf) {
					iStart = 1;
					iEnd = iListLength;
				} else if (oPaging.iPage >= (oPaging.iTotalPages-iHalf)) {
					iStart = oPaging.iTotalPages - iListLength + 1;
					iEnd = oPaging.iTotalPages;
				} else {
					iStart = oPaging.iPage - iHalf + 1;
					iEnd = iStart + iListLength - 1;
				}

				for (i=0, iLen=an.length ; i<iLen ; i++) {
					// Remove the middle elements
					$('li', an[i]).filter(":not(.first)").filter(":not(.last)").filter(":not(.prev)").filter(":not(.next)").remove();

					// Add the new list items and their event handlers
					for (j=iStart ; j<=iEnd ; j++) {
						sClass = (j==oPaging.iPage+1) ? 'class="active"' : '';
						$('<li '+sClass+'><a href="#">'+j+'</a></li>')
							.insertBefore( $('li.next', an[i])[0] )
							.on('click', function (e) {
								e.preventDefault();
								oSettings._iDisplayStart = (parseInt($('a', this).text(),10)-1) * oPaging.iLength;
								fnDraw( oSettings );
							} );
					}

					// Add / remove disabled classes from the static elements
					if (oPaging.iPage === 0) {
						$('li.first', an[i]).addClass('disabled');
						$('li.prev', an[i]).addClass('disabled');
					} else {
						$('li.prev', an[i]).removeClass('disabled');
						$('li.first', an[i]).removeClass('disabled');
					}

					if (oPaging.iPage === oPaging.iTotalPages-1 || oPaging.iTotalPages === 0) {
						$('li.last', an[i]).addClass('disabled');
						$('li.next', an[i]).addClass('disabled');
					} else {
						$('li.next', an[i]).removeClass('disabled');
						$('li.last', an[i]).removeClass('disabled');
					}
				}
			}
		}
	} );


	/**
	 * Bootstrap style pagination control with only previous/next buttons
	 */
	$.extend($.fn.dataTableExt.oPagination, {
		"bootstrap_prevnext": {
			"fnInit": function(oSettings, nPaging, fnDraw) {
				var oLang = oSettings.oLanguage.oPaginate;
				var fnClickHandler = function (e) {
					e.preventDefault();
					if (oSettings.oApi._fnPageChange(oSettings, e.data.action))
						fnDraw(oSettings);
				};

				$(nPaging).append(
					'<ul class="pagination">' +
						'<li class="first disabled"><a href="#"><i class="fa fa-fw fa-fast-backward"></i></a></li>' +
						'<li class="prev disabled"><a href="#"><i class="fa fa-fw fa-step-backward"></i></a></li>' +
						'<li class="next disabled"><a href="#"><i class="fa fa-fw fa-step-forward"></i></a></li>' +
						'<li class="last disabled"><a href="#"><i class="fa fa-fw fa-fast-forward"></i></a></li>' +
					'</ul>'
				);
				var els = $('a', nPaging);
				$(els[0]).on('click.DT', { action: "first" }, fnClickHandler);
				$(els[1]).on('click.DT', { action: "previous" }, fnClickHandler);
				$(els[2]).on('click.DT', { action: "next" }, fnClickHandler);
				$(els[3]).on('click.DT', { action: "last" }, fnClickHandler);
			},

			"fnUpdate": function (oSettings, fnDraw) {
				var iListLength = 5;
				var oPaging = oSettings.oInstance.fnPagingInfo();
				var an = oSettings.aanFeatures.p;
				var i,
					j,
					sClass,
					iStart,
					iEnd,
					iLen,
					iHalf=Math.floor(iListLength/2);

				if (oPaging.iTotalPages < iListLength) {
					iStart = 1;
					iEnd = oPaging.iTotalPages;
				} else if (oPaging.iPage <= iHalf) {
					iStart = 1;
					iEnd = iListLength;
				} else if (oPaging.iPage >= (oPaging.iTotalPages-iHalf)) {
					iStart = oPaging.iTotalPages - iListLength + 1;
					iEnd = oPaging.iTotalPages;
				} else {
					iStart = oPaging.iPage - iHalf + 1;
					iEnd = iStart + iListLength - 1;
				}

				for (i=0, iLen=an.length ; i<iLen ; i++) {
					// Add / remove disabled classes from the static elements
					if (oPaging.iPage === 0) {
						$('li.first', an[i]).addClass('disabled');
						$('li.prev', an[i]).addClass('disabled');
					} else {
						$('li.prev', an[i]).removeClass('disabled');
						$('li.first', an[i]).removeClass('disabled');
					}

					if (oPaging.iPage === oPaging.iTotalPages-1 || oPaging.iTotalPages === 0) {
						$('li.last', an[i]).addClass('disabled');
						$('li.next', an[i]).addClass('disabled');
					} else {
						$('li.next', an[i]).removeClass('disabled');
						$('li.last', an[i]).removeClass('disabled');
					}
				}
			}
		}
	});


	/*
	 * TableTools Bootstrap compatibility
	 * Required TableTools 2.1+
	 */
	if ($.fn.DataTable.TableTools) {
		// Set the classes that TableTools uses to something suitable for Bootstrap
		$.extend( true, $.fn.DataTable.TableTools.classes, {
			"container": "DTTT btn-group",
			"buttons": {
				"normal": "btn btn-default btn-sm",
				"disabled": "disabled"
			},
			"collection": {
				"container": "DTTT_dropdown dropdown-menu",
				"buttons": {
					"normal": "",
					"disabled": "disabled"
				}
			},
			"print": {
				"info": "DTTT_print_info modal"
			},
			"select": {
				"row": "active"
			}
		} );

		// Have the collection use a bootstrap compatible dropdown
		$.extend(true, $.fn.DataTable.TableTools.DEFAULTS.oTags, {
			"collection": {
				"container": "ul",
				"button": "li",
				"liner": "a"
			}
		});
	}


	/**
	 * Length and filter extensions
	 * Just replace 'l' and 'f' in sDom property by 'L' and 'F' to use them
	 */

	/**
	 * Bootstrap length factory
	 */
	var bl_factory = function($, DataTable) {

		var BootstrapLength = function(oSettings, oInit) {

			if (!this.CLASS || this.CLASS != 'BootstrapLength')
				alert("Warning: BootstrapLength must be initialized with the 'new' keyword");
			if (typeof(oInit) == 'undefined')
				oInit = {};
			if ($.fn.dataTable.camelToHungarian)
				$.fn.dataTable.camelToHungarian(BootstrapLength.defaults, oInit);

			this.s = {
				dt: null,
				oInit: oInit,
				hidden: true,
				abOriginal: []
			};
			this.dom = {
				wrapper: null,
				input: null
			};
			BootstrapLength.aInstances.push(this);

			this.s.dt = $.fn.dataTable.Api
				? new $.fn.dataTable.Api(oSettings).settings()[0]
				: oSettings;

			this._fnConstruct(oInit);
			return this;
		};

		BootstrapLength.prototype = {

			input: function() {
				return this.dom.wrapper;
			},

			fnRebuild: function() {
				return this.rebuild();
			},

			rebuild: function() {
			},

			_fnConstruct: function(init) {
				var self = this;
				var dt = self.s.dt;
				if (dt.oScroll.bInfinite)
					return;
				var sName = dt.sTableId + '_length';
				var sMenu = $('<select size="1"></select>').attr('name', sName);
				var i, iLen;
				var aLengthMenu = dt.aLengthMenu;
				if (aLengthMenu.length == 2 && typeof(aLengthMenu[0]) == 'object' && typeof(aLengthMenu[1]) == 'object') {
					for (i=0, iLen=aLengthMenu[0].length; i < iLen; i++)
						$('<option />').attr('value', aLengthMenu[0][i])
									   .text(aLengthMenu[1][i])
									   .appendTo(sMenu);
				} else {
					for (i=0, iLen=aLengthMenu.length; i < iLen; i++)
						$('<option />').attr('value', aLengthMenu[i])
									   .text(aLengthMenu[i])
									   .appendTo(sMenu);
				}
				var nLength = $('<div>').addClass(dt.oClasses.sLength)
										.append($('<span></span>').addClass('ams-form')
																  .append($('<label></label>').addClass('select')
																							  .css('width', 60)
																							  .append(sMenu)
																							  .append($('<i></i>'))));
				if (!dt.aanFeatures.L)
					nLength.attr('id', dt.sTableId + '_length');
				this.dom.wrapper = nLength.get(0);

				$('select option[value="' + dt._iDisplayLength + '"]', nLength).attr("selected", true);
				$("select", nLength).on('change.DT', function(e) {
					var iVal = $(this).val();
					var n = dt.aanFeatures.L;
					for (i = 0, iLen = n.length; i < iLen; i++) {
						if (n[i] != this.parentNode)
						  $("select", n[i]).val(iVal);
					}
					dt._iDisplayLength = parseInt(iVal, 10);
					dt.oInstance._fnCalculateEnd(dt);
					if (dt.fnDisplayEnd() == dt.fnRecordsDisplay()) {
						dt._iDisplayStart = dt.fnDisplayEnd() - dt._iDisplayLength;
						if (dt._iDisplayStart < 0)
							dt._iDisplayStart = 0;
					}
					if (dt._iDisplayLength == -1)
						dt._iDisplayStart = 0;
					dt.oInstance._fnDraw();
				});
				$("select", nLength).attr("aria-controls", dt.sTableId);
			}
		};

		BootstrapLength.fnRebuild = function(oTable) {};

		BootstrapLength.defaults = {};
		BootstrapLength.aInstances = [];
		BootstrapLength.prototype.CLASS = 'BootstrapLength';

		BootstrapLength.VERSION = '1.0.0';
		BootstrapLength.prototype.VERSION = BootstrapLength.VERSION;

		if ((typeof($.fn.dataTable) == 'function') &&
			(typeof($.fn.dataTableExt.fnVersionCheck) == 'function') &&
			$.fn.dataTableExt.fnVersionCheck('1.7.0')) {
			$.fn.dataTableExt.aoFeatures.push({
				fnInit: function(oSettings) {
					var init = oSettings.oInit;
					var Length = new BootstrapLength(oSettings, init.bootstrapLength || init.oBootstrapLength || {});
					return Length.input();
				},
				cFeature: 'L',
				sFeature: "BootstrapLength"
			});
		} else {
			alert("Warning: BootstrapLength required DataTables 1.7 or greater...");
		}

		$.fn.dataTable.BootstrapLength = BootstrapLength;
		return BootstrapLength;

	};

	if (!jQuery.fn.dataTable.BootstrapLength) {
		bl_factory($, $.fn.dataTable);
	}


	/**
	 * Bootstrap filter factory
	 */
	var bf_factory = function($, DataTable) {

		var BootstrapFilter = function(oSettings, oInit) {

			if (!this.CLASS || this.CLASS != 'BootstrapFilter')
				alert("Warning: BootstrapFilter must be initialized with the 'new' keyword");
			if (typeof(oInit) == 'undefined')
				oInit = {};
			if ($.fn.dataTable.camelToHungarian)
				$.fn.dataTable.camelToHungarian(BootstrapFilter.defaults, oInit);

			this.s = {
				dt: null,
				oInit: oInit,
				hidden: true,
				abOriginal: []
			};
			this.dom = {
				wrapper: null,
				input: null
			};
			BootstrapFilter.aInstances.push(this);

			this.s.dt = $.fn.dataTable.Api
				? new $.fn.dataTable.Api(oSettings).settings()[0]
				: oSettings;

			this._fnConstruct(oInit);
			return this;
		};

		BootstrapFilter.prototype = {

			input: function() {
				return this.dom.wrapper;
			},

			fnRebuild: function() {
				return this.rebuild();
			},

			rebuild: function() {
			},

			_fnConstruct: function(init) {
				var self = this;
				var dt = self.s.dt;
				var oPreviousSearch = dt.oPreviousSearch;
				var sSearchStr = '<input type="text">';
				var nFilter = $('<div>').addClass(dt.oClasses.sFilter)
										.html('<div class="input-group">' +
													'<span class="input-group-addon"><i class="fa fa-search"></i></span>' +
													sSearchStr +
											  '</div>');
				if (!dt.aanFeatures.F)
					nFilter.attr('id', dt.sTableId + '_filter');
				this.dom.wrapper = nFilter.get(0);

				var jqFilter = $('input[type="text"]', nFilter);
				nFilter.data('DT_Input', jqFilter[0]);
				jqFilter.val(oPreviousSearch.sSearch.replace('"', "&quot;"))
						.addClass('form-control')
						.attr('placeholder', dt.oLanguage.sSearch)
						.attr('aria-control', dt.sTableId)
						.on('keyup.DT', function(e) {
							var n = dt.aanFeatures.F;
							var val = $(this).val();
							for (var i = 0, iLen = n.length; i < iLen; i++) {
								if (n[i] != $(this).parents("div.dataTables_filter")[0])
									$(n[i]).data('DT_Input').val(val);
							}
							if (val != oPreviousSearch.sSearch) {
								dt.oInstance._fnFilterComplete({
									sSearch: val,
									bRegex: oPreviousSearch.bRegex,
									bSmart: oPreviousSearch.bSmart,
									bCaseInsensitive: oPreviousSearch.bCaseInsensitive
								});
							}
						})
						.on('keypress.DT', function(e) {
							if (e.keyCode == 13) {
								return false;
							}
						});
			}
		};

		BootstrapFilter.fnRebuild = function(oTable) {};

		BootstrapFilter.defaults = {};
		BootstrapFilter.aInstances = [];
		BootstrapFilter.prototype.CLASS = 'BootstrapFilter';

		BootstrapFilter.VERSION = '1.0.0';
		BootstrapFilter.prototype.VERSION = BootstrapFilter.VERSION;

		if ((typeof($.fn.dataTable) == 'function') &&
			(typeof($.fn.dataTableExt.fnVersionCheck) == 'function') &&
			$.fn.dataTableExt.fnVersionCheck('1.7.0')) {
			$.fn.dataTableExt.aoFeatures.push({
				fnInit: function(oSettings) {
					var init = oSettings.oInit;
					var filter = new BootstrapFilter(oSettings, init.bootstrapFilter || init.oBootstrapFilter || {});
					return filter.input();
				},
				cFeature: 'F',
				sFeature: "BootstrapFilter"
			});
		} else {
			alert("Warning: BootstrapFilter required DataTables 1.7 or greater...");
		}

		$.fn.dataTable.BootstrapFilter = BootstrapFilter;
		return BootstrapFilter;

	};

	if (!jQuery.fn.dataTable.BootstrapFilter) {
		bf_factory($, $.fn.dataTable);
	}

})(jQuery);
