/*
 * MyAMS
 * « My Application Management Skin »
 *
 * $Tag: 0.1.7 $
 * A bootstrap based application/administration skin
 *
 * Custom administration and application skin tools
 * Released under Zope Public License ZPL 1.1
 * ©2014 Thierry Florac <tflorac@ulthar.net>
 */

(function($) {

	/**
	 * String prototype extensions
	 */
	String.prototype.startsWith = function(str) {
		var slen = this.length;
		var dlen = str.length;
		if (slen < dlen) {
			return false;
		}
		return (this.substr(0,dlen) == str);
	};

	String.prototype.endsWith = function(str) {
		var slen = this.length;
		var dlen = str.length;
		if (slen < dlen) {
			return false;
		}
		return (this.substr(slen-dlen) == str);
	};


	/**
	 * Array prototype extensions
	 */
	if (!Array.prototype.indexOf) {
		Array.prototype.indexOf = function(elt /*, from*/) {
			var len = this.length;

			var from = Number(arguments[1]) || 0;
			from = (from < 0) ? Math.ceil(from) : Math.floor(from);
			if (from < 0)
				from += len;

			for (; from < len; from++) {
				if (from in this &&
					this[from] === elt)
					return from;
			}
			return -1;
		};
	}


	/**
	 * JQuery 'econtains' expression
	 * Case insensitive contains expression
	 */
	$.expr[":"].econtains = function(obj, index, meta /*, stack*/) {
		return (obj.textContent || obj.innerText || $(obj).text() || "").toLowerCase() == meta[3].toLowerCase();
	};


	/**
	 * JQuery 'withtext' expression
	 * Case sensitive exact search expression
	 */
	$.expr[":"].withtext = function(obj, index, meta /*, stack*/) {
		return (obj.textContent || obj.innerText || $(obj).text() || "") == meta[3];
	};


	/**
	 * JQuery filter on parents class
	 */
	$.expr[':'].parents = function(obj, index, meta /*, stack*/) {
		return $(obj).parents(meta[3]).length > 0;
	};


	/**
	 * JQuery 'scrollbarWidth' function
	 * Get width of vertical scrollbar
	 */
	if ($.scrollbarWidth === undefined) {
		$.scrollbarWidth = function() {
			var parent = $('<div style="width:50px;height:50px;overflow:auto"><div/></div>').appendTo('body');
			var child = parent.children();
			var width = child.innerWidth() - child.height(99).innerWidth();
			parent.remove();
			return width;
		};
	}


	/**
	 * MyAMS JQuery extensions
	 */
	$.fn.extend({

		/*
		 * Check if current object is empty or not
		 */
		exists: function() {
			return $(this).length > 0;
		},

		/*
		 * CSS style function
		 * Code from Aram Kocharyan on stackoverflow.com
		 */
		style: function(styleName, value, priority) {
			// DOM node
			var node = this.get(0);
			// Ensure we have a DOM node
			if (typeof node == 'undefined') {
				return;
			}
			// CSSStyleDeclaration
			var style = this.get(0).style;
			// Getter/Setter
			if (typeof styleName != 'undefined') {
				if (typeof value != 'undefined') {
					// Set style property
					priority = typeof priority != 'undefined' ? priority : '';
					style.setProperty(styleName, value, priority);
					return this;
				} else {
					// Get style property
					return style.getPropertyValue(styleName);
				}
			} else {
				// Get CSSStyleDeclaration
				return style;
			}
		},

		/*
		 * Remove CSS classes starting with a given prefix
		 */
		removeClassPrefix: function (prefix) {
			this.each(function (i, it) {
				var classes = it.className.split(" ").map(function(item) {
					return item.startsWith(prefix) ? "" : item
				});
				it.className = $.trim(classes.join(" "))
			});
			return this;
		},

		/*
		 * Main menus manager
		 */
		myams_menu: function(options) {
			// Extend our default options with those provided
			var defaults = {
				accordion : 'true',
				speed : 200,
				closedSign : '<em class="fa fa-angle-down"></em>',
				openedSign : '<em class="fa fa-angle-up"></em>'
			};
			var settings = $.extend({}, defaults, options);

			// Assign current element to variable, in this case is UL element
			var menu = $(this);

			// Add a mark [+] to a multilevel menu
			menu.find("LI").each(function() {
				var menu_item = $(this);
				if (menu_item.find("UL").size() > 0) {

					// add the multilevel sign next to the link
					menu_item.find("A:first")
							 .append("<b class='collapse-sign'>" + settings.closedSign + "</b>");

					// avoid jumping to the top of the page when the href is an #
					var first_link = menu_item.find("A:first");
					if (first_link.attr('href') == "#") {
						first_link.click(function() {
							return false;
						});
					}
				}
			});

			// Open active level
			menu.find("LI.active").each(function() {
				var active_parent = $(this).parents('UL');
				var active_item = active_parent.parent('LI');
				active_parent.slideDown(settings.speed);
				active_item.find("b:first").html(settings.openedSign);
				active_item.addClass("open")
			});

			menu.find("LI A").on('click', function() {
				var link = $(this);
				var parent_ul = link.parent().find("UL");
				if (parent_ul.size() != 0) {
					if (settings.accordion) {
						// Do nothing when the list is open
						if (!parent_ul.is(':visible')) {
							var parents = link.parent().parents("UL");
							var visible = menu.find("UL:visible");
							visible.each(function(visibleIndex) {
								var close = true;
								parents.each(function(parentIndex) {
									if (parents[parentIndex] == visible[visibleIndex]) {
										close = false;
										return false;
									}
								});
								if (close) {
									if (parent_ul != visible[visibleIndex]) {
										$(visible[visibleIndex]).slideUp(settings.speed, function() {
											link.parent("LI")
												.find("b:first")
												.html(settings.closedSign);
											link.parent("LI")
												.removeClass("open");
										});
									}
								}
							});
						}
					}
					var first_ul = link.parent().find("UL:first");
					if (!link.attr('href').replace(/^#/,'') &&
						first_ul.is(":visible") &&
						!first_ul.hasClass("active")) {
						first_ul.slideUp(settings.speed, function() {
							link.parent("LI")
								.removeClass("open")
								.find("B:first")
								.delay(settings.speed)
								.html(settings.closedSign);
						});
					} else /*if (link.attr('href') != location.hash)*/ {
						first_ul.slideDown(settings.speed, function() {
							link.parent("LI")
								.addClass("open")
								.find("B:first")
								.delay(settings.speed)
								.html(settings.openedSign);
						});
					}
				}
			});
		}
	});


	/**
	 * UTF-8 encoding class
	 * Mainly used by IE...
	 */
	$.UTF8 = {

		// public method for url encoding
		encode : function (string) {
			string = string.replace(/\r\n/g,"\n");
			var utftext = "";

			for (var n = 0; n < string.length; n++) {

				var c = string.charCodeAt(n);

				if (c < 128) {
					utftext += String.fromCharCode(c);
				}
				else if((c > 127) && (c < 2048)) {
					utftext += String.fromCharCode((c >> 6) | 192);
					utftext += String.fromCharCode((c & 63) | 128);
				}
				else {
					utftext += String.fromCharCode((c >> 12) | 224);
					utftext += String.fromCharCode(((c >> 6) & 63) | 128);
					utftext += String.fromCharCode((c & 63) | 128);
				}
			}
			return utftext;
		},

		// public method for url decoding
		decode : function (utftext) {
			var string = "";
			var i = 0,
				c = 0,
				c2 = 0,
				c3 = 0;

			while ( i < utftext.length ) {

				c = utftext.charCodeAt(i);

				if (c < 128) {
					string += String.fromCharCode(c);
					i++;
				}
				else if((c > 191) && (c < 224)) {
					c2 = utftext.charCodeAt(i+1);
					string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
					i += 2;
				}
				else {
					c2 = utftext.charCodeAt(i+1);
					c3 = utftext.charCodeAt(i+2);
					string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
					i += 3;
				}
			}
			return string;
		}
	}; /** $.UTF8 */


	/**
	 * MyAMS extensions to JQuery
	 */
	if (window.MyAMS === undefined) {
		window.MyAMS = {
			devmode: true,
			throttle_delay: 350,
			menu_speed: 235,
			navbar_height: 49,
			ajax_nav: true,
			enable_widgets: true,
			enable_mobile: false,
			enable_fastclick: false,
			warn_on_form_change: false,
			ismobile: (/iphone|ipad|ipod|android|blackberry|mini|windows\sce|palm/i.test(navigator.userAgent.toLowerCase()))
		};
	}
	var ams = MyAMS;

	/**
	 * Get MyAMS base URL
	 * Copyright Andrew Davy: https://forrst.com/posts/Get_the_URL_of_the_current_javascript_file-Dst
	 */
	MyAMS.baseURL = (function () {
		var script = $('script[src$="/myams.js"], script[src$="/myams.min.js"]');
		var src = script.attr("src");
		return src.substring(0, src.lastIndexOf('/') + 1);
	})();


	/**
	 * Extract parameter value from given query string
	 */
	MyAMS.getQueryVar = function(src, varName) {
		// Check src
		if (src.indexOf('?') < 0)
			return false;
		if (!src.endsWith('&'))
			src += '&';
		// Dynamic replacement RegExp
		var regex = new RegExp('.*?[&\\?]' + varName + '=(.*?)&.*');
		// Apply RegExp to the query string
		var val = src.replace(regex, "$1");
		// If the string is the same, we didn't find a match - return false
		return val == src ? false : val;
	};


	/**
	 * Color conversion function
	 */
	MyAMS.rgb2hex = function(color) {
		return "#" + $.map(color.match(/\b(\d+)\b/g), function(digit) {
			return ('0' + parseInt(digit).toString(16)).slice(-2)
		}).join('');
	};


	/**
	 * Generate a random ID
	 *
	 * @param length
	 */
	MyAMS.generateId = function() {
		function s4() {
			return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
		}
		return s4() + s4() + s4() + s4();
	};


	/**
	 * Get and execute a function given by name
	 * Small piece of code by Jason Bunting
	 */
	MyAMS.getFunctionByName = function(functionName, context) {
		if (functionName === undefined)
			return undefined;
		else if (typeof(functionName) == 'function')
			return functionName;
		var namespaces = functionName.split(".");
		var func = namespaces.pop();
		context = (context === undefined || context === null) ? window : context;
		for (var i=0; i < namespaces.length; i++) {
			try {
				context = context[namespaces[i]];
			} catch (e) {
				return undefined;
			}
		}
		try {
			return context[func];
		} catch (e) {
			return undefined;
		}
	};

	MyAMS.executeFunctionByName = function(functionName, context /*, args */) {
		var func = ams.getFunctionByName(functionName, window);
		if (typeof(func) == 'function') {
			var args = Array.prototype.slice.call(arguments, 2);
			return func.apply(context, args);
		}
	};


	/**
	 * Get script or CSS file using browser cache
	 * Script or CSS URLs can include variable names, given between braces, as in
	 * {MyAMS.baseURL}
	 */
	MyAMS.getSource = function(url) {
		return url.replace(/{[^{}]*}/g, function(match) {
			return ams.getFunctionByName(match.substr(1, match.length-2));
		});
	};

	MyAMS.getScript = function(url, callback, options) {
		var defaults = {
			dataType: 'script',
			url: ams.getSource(url),
			success: callback,
			error: ams.error.show,
			cache: true,
			async: true
		};
		var settings = $.extend({}, defaults, options);
		return $.ajax(settings);
	};

	MyAMS.getCSS = function(url, id) {
		var head = $('HEAD');
		var css = $('link[data-ams-id="' + id + '"]', head);
		if (css.length == 0) {
			$('<link />').attr({rel: 'stylesheet',
								type: 'text/css',
								href: ams.getSource(url),
								'data-ams-id': id})
						 .appendTo(head);
		}
	};


	/**
	 * Events management
	 */
	MyAMS.event = {

		stop: function(event) {
			if (!event) {
				event = window.event;
			}
			if (event) {
				if (event.stopPropagation) {
					event.stopPropagation();
					event.preventDefault();
				} else {
					event.cancelBubble = true;
					event.returnValue = false;
				}
			}
		}
	};


	/**
	 * Browser testing functions; mostly for IE...
	 */
	MyAMS.browser = {

		getInternetExplorerVersion: function() {
			var rv = -1;
			if (navigator.appName == "Microsoft Internet Explorer") {
				var ua = navigator.userAgent;
				var re = new RegExp("MSIE ([0-9]{1,}[.0-9]{0,})");
				if (re.exec(ua) != null)
					rv = parseFloat(RegExp.$1);
			}
			return rv;
		},

		checkVersion: function() {
			var msg = "You're not using Windows Internet Explorer.";
			var ver = this.getInternetExplorerVersion();
			if (ver > -1) {
				if (ver >= 8)
					msg = "You're using a recent copy of Windows Internet Explorer.";
				else
					msg = "You should upgrade your copy of Windows Internet Explorer.";
			}
			alert(msg);
		},

		isIE8orlower: function() {
			var msg = "0";
			var ver = this.getInternetExplorerVersion();
			if (ver > -1) {
				if (ver >= 9)
					msg = 0;
				else
					msg = 1;
			}
			return msg;
		}
	};


	/**
	 * Errors management features
	 */
	MyAMS.error = {

		/**
		 * Default JQuery AJAX error handler
		 */
		ajax: function(event, request /*, settings*/) {
			if (request.statusText == 'OK')
				return;
			var response = ams.ajax.getResponse(request);
			if (response.content_type == 'json') {
				ams.ajax.handleJSON(response.data);
			} else {
				var title = event.statusText || event.type;
				var message = request.responseText;
				ams.skin.messageBox('error', {
					title: ams.i18n.ERROR_OCCURED,
					content: '<h4>' + title + '</h4><p>' + message + '</p>',
					icon: 'fa fa-warning animated shake',
					timeout: 10000
				});
			}
			if (window.console) {
				console.error(event);
				console.debug(request);
			}
		},

		/**
		 * Show AJAX error
		 */
		show: function(request, status, error) {
			if (!error)
				return;
			var response = ams.ajax.getResponse(request);
			if (response.content_type == 'json') {
				ams.ajax.handleJSON(response.data);
			} else {
				ams.skin.messageBox('error', {
					title: ams.i18n.ERRORS_OCCURED,
					content: '<h4>' + status + '</h4><p>' + error + '</p>',
					icon: "fa fa-warning animated shake",
					timeout: 10000
				});
			}
			if (window.console) {
				console.error(error);
				console.debug(request);
			}
		}
	};


	/**
	 * AJAX helper functions
	 */
	MyAMS.ajax = {

		/**
		 * Check for given feature and download script if necessary
		 *
		 * @checker: pointer to a javascript object which will be downloaded in undefined
		 * @source: URL of a javascript file containing requested feature
		 * @callback: pointer to a function which will be called after the script is downloaded. The first
		 *   argument of this callback is a boolean value indicating if the script was just downloaded (true)
		 *   or if the requested object was already loaded (false)
		 * @options: callback options
		 */
		check: function(checker, source, callback, options) {
			if (typeof(callback) == 'object') {
				options = callback;
				callback = undefined;
			}
			var defaults = {
				async: typeof(callback) == 'function'
			};
			var settings = $.extend({}, defaults, options);
			if (checker === undefined) {
				ams.getScript(source, function() {
					if (typeof(callback) == 'function')
						callback(true, options);
				}, settings);
			} else {
				if (typeof(callback) == 'function')
					callback(false, options);
			}
		},

		/**
		 * Get address relative to current page
		 */
		getAddr: function(addr) {
			var href = addr || $('HTML HEAD BASE').attr('href') || window.location.href;
			return href.substr(0, href.lastIndexOf("/") + 1);
		},

		/**
		 * Handle AJAX upload and download progress
		 *
		 * @param event: the source event
		 * @param request: the request
		 * @param options: AJAX options
		 */
		progress: function(event) {
			if (!event.lengthComputable)
				return;
			if (event.loaded >= event.total)
				return;
			console.log(parseInt((event.loaded / event.total * 100), 10) + "%");
		},

		/**
		 * Post data to given URL
		 */
		post: function(url, data, options, callback) {
			if (url.startsWith(window.location.protocol))
				var addr = url;
			else
				addr = this.getAddr() + url;
			if (typeof(options) == 'function') {
				callback = options;
				options = {}
			} else if (!options) {
				options = {};
			}
			if (typeof(callback) == 'undefined')
				callback = options.callback;
			if (typeof(callback) == 'string')
				callback = ams.getFunctionByName(callback);
			delete options.callback;

			var result = undefined;
			var defaults = {
				url: addr,
				type: 'post',
				cache: false,
				async: typeof(callback) == 'function',
				data: $.param(data, true),
				dataType: 'json',
				success: callback || function(data /*, status*/) {
					result = data.result;
				},
				error: ams.error.show
			};
			var settings = $.extend({}, defaults, options);
			$.ajax(settings);
			return result;
		},

		/**
		 * Extract data type and result from response
		 */
		getResponse: function(request) {
			var content_type = request.getResponseHeader('content-type'),
				data_type,
				result;
			if (content_type) {
				// Got server response
				if (content_type.startsWith('application/javascript')) {
					data_type = 'script';
					result = request.responseText;
				} else if (content_type.startsWith('text/html')) {
					data_type = 'html';
					result = request.responseText;
				} else if (content_type.startsWith('text/xml')) {
					data_type = 'xml';
					result = request.responseText;
				} else {
					result = request.responseJSON;
					if (result)
						data_type = 'json';
					else {
						try {
							result = JSON.parse(request.responseText);
							data_type = 'json';
						} catch (e) {
							result = request.responseText;
							data_type = 'text';
						}
					}
				}
			} else {
				// Probably no response from server...
				data_type = 'json';
				result = {
					status: 'alert',
					alert: {
						title: ams.i18n.ERROR_OCCURED,
						content: ams.i18n.NO_SERVER_RESPONSE
					}
				};
			}
			return {content_type: data_type,
					data: result};
		},

		/**
		 * Handle server response in JSON format
		 *
		 * Result is made of several JSON attributes:
		 *  - status: error, success, callback, callbacks, reload or redirect
		 *  - close_form: boolean indicating if current modal should be closed
		 *  - location: target URL for reload or redirect status
		 *  - target: target container's selector for loaded content ('#content' by default)
		 *  - content: available for any status producing output content:
		 *        {target: target container's selector (source form by default)
		 *         html: HTML result}
		 *  - message: available for any status producing output message:
		 *        {target: target message container's selector
		 *         status: message status
		 *         header: message header
		 *         subtitle: message subtitle,
		 *         body: message body}
		 *
		 * For errors data structure, please see MyAMS.form.showErrors function
		 */
		handleJSON: function(result, form, target) {
			var status = result.status;
			var url;
			switch (status) {
				case 'alert':
					alert(result.alert.title + '\n\n' + result.alert.content);
					break;
				case 'error':
					ams.form.showErrors(form, result);
					break;
				case 'success':
					if (result.close_form != false)
						ams.dialog.close(form);
					break;
				case 'message':
				case 'messagebox':
					break;
				case 'notify':
				case 'callback':
				case 'callbacks':
					if (result.close_form != false)
						ams.dialog.close(form);
					break;
				case 'modal':
					ams.dialog.open(result.location);
					break;
				case 'reload':
					if (result.close_form != false)
						ams.dialog.close(form);
					url = result.location;
					if (url.startsWith('#'))
						url = url.substr(1);
					ams.skin.loadURL(url, result.target || target || '#content');
					break;
				case 'redirect':
					if (result.close_form == true)
						ams.dialog.close(form);
					url = result.location;
					if (result.window) {
						window.open(url, result.window, result.options);
					} else {
						window.location.href = url;
					}
					break;
				default:
					console.log("Unhandled status: " + status);
					break;
			}
			if (result.content) {
				var content = result.content;
				var container = $(content.target || target || form || '#content');
				container.html(content.html);
				ams.initContent(container);
			}
			if (result.message) {
				var message = result.message;
				if (typeof(message) == 'string')
					ams.skin.alert($(form || '#content'),
								   status, '', message);
				else
					ams.skin.alert($(message.target || target || form || '#content'),
								   message.status || 'success',
								   message.header,
								   message.body,
								   message.subtitle);
			}
			if (result.messagebox) {
				message = result.messagebox;
				if (typeof(message) == 'string')
					ams.skin.messageBox('info',
										{title: ams.i18n.ERROR_OCCURED,
										 content: message,
										 timeout: 10000});
				else {
					var message_status = message.status || 'info';
					if (message_status == 'error' && form && target)
						ams.executeFunctionByName(form.data('ams-form-submit-error') || 'MyAMS.form.finalizeSubmitOnError', form, target);
					ams.skin.messageBox(message_status,
										{title: message.title || ams.i18n.ERROR_OCCURED,
										 content: message.content,
										 icon: message.icon,
										 number: message.number,
										 timeout: message.timeout || 10000});
				}
			}
			if (result.event)
				form.trigger(result.event, result.event_options);
			if (result.callback)
				ams.executeFunctionByName(result.callback, form, result.options);
			if (result.callbacks) {
				for (var index in result.callbacks) {
					if (!$.isNumeric(index))
						continue;
					var callback = result.callbacks[index];
					ams.executeFunctionByName(callback, form, callback.options);
				}
			}
		}
	};


	/**
	 * JSON-RPC helper functions
	 */
	MyAMS.jsonrpc = {

		/**
		 * Get address relative to current page
		 */
		getAddr: function(addr) {
			var href = addr || $('HTML HEAD BASE').attr('href') || window.location.href;
			var target = href.replace(/\+\+skin\+\+\w+\//, '');
			return target.substr(0, target.lastIndexOf("/") + 1);
		},

		/**
		 * Execute JSON-RPC request on given method
		 *
		 * Query can be given as a simple "query" string or as an object containing all query parameters.
		 * Parameters:
		 *  - @query: query string (posted as "query" parameter) or object containing all parameters
		 *  - @method: name of JSON-RPC procedure to call
		 *  - @options: additional JSON-RPC procedure parameters
		 *  - @callback: name of a callback which will be called on server response
		 */
		query: function(query, method, options, callback) {
			ams.ajax.check($.jsonRpc,
						   ams.baseURL + 'ext/jquery-jsonrpc' + (ams.devmode ? '.js' : '.min.js'),
						   function() {
								var result;
								if (typeof(options) == 'function') {
									callback = options;
									options = {};
								}
								else if (!options)
									options = {};
								if (typeof(callback) == 'undefined')
									callback = options.callback;
								if (typeof(callback) == 'string')
									callback = ams.getFunctionByName(callback);
								delete options.callback;

								var params = {};
								if (typeof(query) == 'string')
									params['query'] = query;
								else if (typeof(query) == 'object')
									$.extend(params, query);
								$.extend(params, options);

								var settings = {
									url: ams.jsonrpc.getAddr(options.url),
									type: 'post',
									cache: false,
									method: method,
									params: params,
									async: typeof(callback) == 'function',
									success: callback || function(data /*, status*/) {
										result = data.result;
									},
									error: ams.error.show
								};
								$.jsonRpc(settings);
								return result;
						   });
		},

		/**
		 * Execute given JSON-RPC post on given method
		 *
		 * Parameters:
		 *  - @method: name of JSON-RPC procedure to call
		 *  - @options: additional JSON-RPC procedure parameters
		 *  - @callback: name of a callback which will be called on server response
		 */
		post: function(method, data, options, callback) {
			ams.ajax.check($.jsonRpc,
						   ams.baseURL + 'ext/jquery-jsonrpc' + (ams.devmode ? '.js' : '.min.js'),
						   function() {
								var result;
								if (typeof(options) == 'function') {
									callback = options;
									options = {};
								}
								else if (!options)
									options = {};
								if (typeof(callback) == 'undefined')
									callback = options.callback;
								if (typeof(callback) == 'string')
									callback = ams.getFunctionByName(callback);
								delete options.callback;

								var defaults = {
									url: ams.jsonrpc.getAddr(options.url),
									type: 'post',
									cache: false,
									method: method,
									params: data,
									async: typeof(callback) == 'function',
									success: callback || function(data /*, status*/) {
										result = data.result;
									},
									error: ams.error.show
								};
								var settings = $.extend({}, defaults, options);
								$.jsonRpc(settings);
								return result;
						   });
		}
	};


	/**
	 * Forms helper functions
	 */
	MyAMS.form = {

		/**
		 * Init forms to activate form change listeners
		 *
		 * @param element: the parent element
		 */
		init: function(element) {
			// Activate form changes if required
			if (ams.warn_on_form_change)
				var forms = $('FORM[data-ams-warn-on-change!="false"]', element);
			else
				forms = $('FORM[data-ams-warn-on-change="true"]', element);
			forms.each(function() {
				var form = $(this);
				$('INPUT[type="text"], ' +
				  'INPUT[type="checkbox"], ' +
				  'INPUT[type="radio"], ' +
				  'SELECT, ' +
				  'TEXTAREA, ' +
				  '[data-ams-changed-event]', form).each(function() {
						var source = $(this);
						if (source.data('ams-ignore-change') !== true) {
							var event = source.data('ams-changed-event') || 'change';
							source.on(event, function () {
								$(this).parents('FORM').attr('data-ams-form-changed', true);
							});
						}
				});
				form.on('reset', function() {
					$(this).removeAttr('data-ams-form-changed');
				});
			});
		},

		/**
		 * Check for modified forms before exiting
		 */
		checkBeforeUnload: function() {
			var forms = $('FORM[data-ams-form-changed="true"]');
			if (forms.exists()) {
				return ams.i18n.FORM_CHANGED_WARNING;
			}
		},

		/**
		 * Check for modified forms before loading new inner content
		 */
		confirmChangedForm: function(element, callback) {
			if (typeof(element) == 'function') {
				callback = element;
				element = undefined;
			}
			var forms = $('FORM[data-ams-form-changed="true"]', element);
			if (forms.exists()) {
				ams.skin.bigBox({
					title: ams.i18n.WARNING,
					content: '<i class="text-danger fa fa-2x fa-bell shake animated"></i>&nbsp; ' + ams.i18n.FORM_CHANGED_WARNING,
					buttons: ams.i18n.BTN_OK_CANCEL
				}, function(button) {
					if (button == ams.i18n.BTN_OK)
						callback.call(element);
				});
			} else {
				callback.call(element);
			}
		},

		/**
		 * Submit given form
		 */
		submit: function(form, handler, submit_options) {
			// Check params
			form = $(form);
			if (!form.exists())
				return false;
			if (typeof(handler) == 'object') {
				submit_options = handler;
				handler = undefined;
			}
			// Prevent multiple submits of the same form
			if (form.data('submitted')) {
				ams.skin.messageBox('warning', {
					title: ams.i18n.WAIT,
					content: ams.i18n.FORM_SUBMITTED,
					icon: 'fa fa-save shake animated',
					timeout: 5000
				});
				return false;
			}
			// Check submit validators
			if (!ams.form._checkSubmitValidators(form))
				return false;
			// Remove remaining status messages
			$('.alert, SPAN.state-error', form).remove();
			$('.state-error', form).removeClassPrefix('state-');
			// Check submit button
			var button = $(form.data('ams-submit-button'));
			if (button)
				button.button('loading');
			ams.ajax.check($.fn.ajaxSubmit,
						   ams.baseURL + 'ext/jquery-form-3.49' + (ams.devmode ? '.js' : '.min.js'),
						   function() {

								function _submitAjaxForm(form, options) {

									var button;
									var data = form.data();
									var form_options = data.amsFormOptions;

									if (submit_options)
										var form_data_callback = submit_options.formDataInitCallback;
									if (form_data_callback)
										delete submit_options.formDataInitCallback;
									else
										form_data_callback = data.amsFormDataInitCallback;
									if (form_data_callback) {
										var veto = {};
										if (typeof(form_data_callback) == 'function')
											var form_data = form_data_callback.call(form, veto);
										else
											form_data = ams.executeFunctionByName(form_data_callback, form, veto);
										if (veto.veto) {
											button = form.data('ams-submit-button');
											if (button)
												button.button('reset');
											ams.form.finalizeSubmitFooter.call(form);
											return false;
										}
									} else {
										form_data = data.amsFormData || {};
									}

									button = $(form.data('ams-submit-button'));
									var buttonHandler,
										buttonTarget;
									if (button) {
										buttonHandler = button.data('ams-form-handler');
										buttonTarget = button.data('ams-form-submit-target');
									}

									var action = form.attr('action').replace(/#/, '');
									if (action.startsWith(window.location.protocol))
										var url = action;
									else
										url = ams.ajax.getAddr() + action;
									url += handler || buttonHandler || data.amsFormHandler || '';

									var target = null;
									if (data.amsFormInitSubmitTarget) {
										target = $(buttonTarget || data.amsFormSubmitTarget || '#content');
										ams.executeFunctionByName(data.amsFormInitSubmit || 'MyAMS.form.initSubmit', form, target);
									} else if (!data.amsFormHideSubmitFooter)
										ams.executeFunctionByName(data.amsFormInitSubmit || 'MyAMS.form.initSubmitFooter', form);

									var hasUpload = typeof(options.uuid) != 'undefined';
									if (hasUpload) {
										if (url.indexOf('X-Progress-ID') < 0)
											url += "?X-Progress-ID=" + options.uuid;
										delete options.uuid;
									}

									var defaults = {
										url: url,
										type: 'post',
										cache: false,
										data: form_data,
										dataType: data.amsFormDatatype,
										beforeSerialize: function(/*form, options*/) {
											if (typeof(tinyMCE) != 'undefined')
												tinyMCE.triggerSave();
										},
										beforeSubmit: function(data, form /*, options*/) {
											form.data('submitted', true);
										},
										error: function(request, status, error, form) {
											if (target)
												ams.executeFunctionByName(data.amsFormSubmitError || 'MyAMS.form.finalizeSubmitOnError', form, target);
											if (form.is(':visible')) {
												var button = form.data('ams-submit-button');
												if (button)
													button.button('reset');
												ams.form.finalizeSubmitFooter.call(form);
											}
											form.data('submitted', false);
											form.removeData('ams-submit-button');
										},
										success: function(result, status, request, form) {
											var callback;
											var button = form.data('ams-submit-button');
											if (button)
												callback = button.data('ams-form-submit-callback');
											if (!callback)
												callback = ams.getFunctionByName(data.amsFormSubmitCallback) || ams.form._submitCallback;
											callback.call(form, result, status, request, form);
											if (form.is(':visible') && button)
												button.button('reset');
											form.data('submitted', false);
											form.removeData('ams-submit-button');
											form.removeAttr('data-ams-form-changed');
										},
										iframe: hasUpload
									}
									var settings = $.extend({}, defaults, options, form_options, submit_options);
									$(form).ajaxSubmit(settings);
								}

								var hasUpload = $('INPUT[type="file"]', form).length > 0;
								if (hasUpload) {
									// JQuery-progressbar plug-in must be loaded synchronously!!
									// Otherwise, hidden input fields created by jquery-validate plug-in
									// and matching named buttons will be deleted (on first form submit)
									// before JQuery-form plug-in can get them when submitting the form...
									ams.ajax.check($.progressBar,
												   ams.baseURL + 'ext/jquery-progressbar' + (ams.devmode ? '.js' : '.min.js'));
									var settings = $.extend({}, {
										uuid: $.progressBar.submit(form)
									});
									_submitAjaxForm(form, settings);
								} else
									_submitAjaxForm(form, {});
						   });
			return false;
		},

		/**
		 * Initialize AJAX submit call
		 *
		 * @param this: the submitted form
		 * @param target: the form submit container target
		 * @param message: the optional message
		 */
		initSubmit: function(target, message) {
			var form = $(this);
			var spin = '<i class="fa fa-3x fa-gear fa-spin"></i>';
			if (!message)
				message = form.data('ams-form-submit-message');
			if (message)
				spin += '<strong>' + message + '</strong>';
			$(target).html('<div class="row margin-20"><div class="text-center">' + spin + '</div></div>');
			$(target).parents('.hidden').removeClass('hidden');
		},

		/**
		 * Finalize AJAX submit call
		 *
		 * @param target: the form submit container target
		 */
		finalizeSubmitOnError: function(target) {
			$('i', target).removeClass('fa-spin')
						  .removeClass('fa-gear')
						  .addClass('fa-ambulance');
		},

		/**
		 * Initialize AJAX submit call in form footer
		 *
		 * @param this: the submitted form
		 * @param message: the optional submit message
		 */
		initSubmitFooter: function(message) {
			var form = $(this);
			var spin = '<i class="fa fa-3x fa-gear fa-spin"></i>';
			if (!message)
				message = $(this).data('ams-form-submit-message');
			if (message)
				spin += '<strong class="submit-message align-top padding-left-10 margin-top-10">' + message + '</strong>';
			var footer = $('footer', form);
			$('button', footer).hide();
			footer.append('<div class="row"><div class="text-center">' + spin + '</div></div>');
		},

		/**
		 * Finalize AJAX submit call
		 *
		 * @param this: the submitted form
		 * @param target: the form submit container target
		 */
		finalizeSubmitFooter: function(/*target*/) {
			var form = $(this);
			var footer = $('footer', form);
			if (footer) {
				$('.row', footer).remove();
				$('button', footer).show();
			}
		},

		/**
		 * Handle AJAX submit results
		 *
		 * Submit results are auto-detected via response content type, except when this content type
		 * is specified into form's data attributes.
		 * Submit response can be of several content types:
		 * - html or text: the response is directly included into a "target" container (#content by default)
		 * - json: a "status" attribute indicates how the request was handled and how the response should be
		 *   treated:
		 *     - error: indicates that an error occured; other response attributes indicate error messages
		 *     - success: basic success, no other action is requested
		 *     - callback: only call given function to handle the result
		 *     - callbacks: only call given set of functions to handle the result
		 *     - reload: page's body should be reloaded from a given URL
		 *     - redirect: redirect browser to given URL
		 *   Each JSON response can also specify an HTML content, a message and a callback (
		 */
		_submitCallback: function(result, status, request, form) {

			if (form.is(':visible')) {
				ams.form.finalizeSubmitFooter.call(form);
				var button = form.data('ams-submit-button');
				if (button)
					button.button('reset');
			}
			var data = form.data();
			if (data.amsFormDatatype)
				var data_type = data.amsFormDatatype;
			else {
				var request_data = ams.ajax.getResponse(request);
				data_type = request_data.content_type;
				result = request_data.data;
			}

			if (button)
				var target = $(button.amsFormSubmitTarget || data.amsFormSubmitTarget || '#content');
			else
				target = $(data.amsFormSubmitTarget || '#content');

			switch (data_type) {
				case 'json':
					ams.ajax.handleJSON(result, form, target);
					break;
				case 'script':
					break;
				case 'xml':
					break;
				case 'html':
				case 'text':
				default:
					if (button && (button.data('ams-keep-modal') !== true))
						ams.dialog.close(form);
					if (!target.exists())
						target = $('body');
					target.parents('.hidden').removeClass('hidden');
					$('.alert', target.parents('.alerts-container')).remove();
					target.css({opacity: '0.0'})
						  .html(result)
						  .delay(50)
						  .animate({opacity: '1.0'}, 300);
					ams.initContent(target);
			}
			var callback = request.getResponseHeader('X-AMS-Callback');
			if (callback) {
				var options = request.getResponseHeader('X-AMS-Callback-Options');
				ams.executeFunctionByName(callback, form, options === undefined ? {} : JSON.parse(options), request);
			}
		},

		/**
		 * Get list of custom validators called before submit
		 */
		_getSubmitValidators: function(form) {
			var validators = new Array();
			var form_validator = form.data('ams-form-validator');
			if (form_validator)
				validators.push([form, form_validator]);
			$('[data-ams-form-validator]', form).each(function() {
				var source = $(this);
				validators.push([source, source.data('ams-form-validator')]);
			});
			return validators;
		},

		/**
		 * Call list of custom validators before submit
		 *
		 * Each validator can return:
		 *  - a boolean 'false' value to just specify that an error occured
		 *  - a string value containing an error message
		 *  - an array containing a list of string error messages
		 * Any other value (undefined, null, True...) will lead to a successful submit.
		 */
		_checkSubmitValidators: function(form) {
			var validators = ams.form._getSubmitValidators(form);
			if (!validators.length)
				return true;
			var output = new Array();
			var result = true;
			for (var index in validators) {
				if (!$.isNumeric(index))  // IE check !
					continue;
				var validator = validators[index];
				var source = validator[0];
				var handler = validator[1];
				var validator_result = ams.executeFunctionByName(handler, form, source);
				if (validator_result === false)
					result = false;
				else if (typeof(validator_result) == 'string')
					output.push(validator_result);
				else if (result.length && (result.length > 0))
					output = output.concat(result);
			}
			if (output.length > 0) {
				var header = output.length == 1 ? ams.i18n.ERROR_OCCURED : ams.i18n.ERRORS_OCCURED;
				ams.skin.alert(form, 'danger', header, output);
				return false;
			} else
				return result;
		},

		/**
		 * Display JSON errors
		 * JSON errors should be defined in an object as is:
		 * {status: 'error',
		 *  error_message: "Main error message",
		 *  messages: ["Message 1", "Message 2",...]
		 *  widgets: [{label: "First widget name",
		 *             name: "field-name-1",
		 *             message: "Error message"},
		 *            {label: "Second widget name",
		 *             name: "field-name-2",
		 *             message: "Second error message"},...]}
		 */
		showErrors: function(form, errors) {
			if (typeof(errors) == 'string') {
				ams.skin.alert(form, 'error', ams.i18n.ERROR_OCCURED, errors)
			} else if (errors instanceof Array) {
				var header = errors.length == 1 ? ams.i18n.ERROR_OCCURED : ams.i18n.ERRORS_OCCURED;
				ams.skin.alert(form, 'error', header, errors);
			} else {
				header = errors.widgets && (errors.widgets.length > 1) ? ams.i18n.ERRORS_OCCURED : ams.i18n.ERROR_OCCURED;
				var message = new Array();
				var index;
				for (index in errors.messages) {
					if (!$.isNumeric(index))
						continue;
					message.push(errors.messages[index].message || errors.messages[index]);
				}
				for (index in errors.widgets) {
					if (!$.isNumeric(index))
						continue;
					var widget = errors.widgets[index];
					$('[name="' + widget.name + '"]', form).parent('label')
														   .removeClassPrefix('state-')
														   .addClass('state-error')
														   .after('<span for="name" class="state-error">' + widget.message + '</span>');
					if (widget.label) {
						message.push(widget.label + ' : ' + widget.message);
					}
				}
				ams.skin.alert(form, 'error', header, message, errors.error_message);
			}
		}
	};


	/**
	 * Modal dialogs helper functions
	 */
	MyAMS.dialog = {

		/**
		 * Modal dialog opener
		 */
		open: function(source, options) {
			ams.ajax.check($.fn.modalmanager,
						   ams.baseURL + 'ext/bootstrap-modalmanager' + (ams.devmode ? '.js' : '.min.js'),
						   function() {
								ams.ajax.check($.fn.modal.defaults,
											   ams.baseURL + 'ext/bootstrap-modal' + (ams.devmode ? '.js' : '.min.js'),
								function(first_load) {
									if (first_load) {
										$(document).off('click.modal');
										$.fn.modal.defaults.spinner = $.fn.modalmanager.defaults.spinner =
											'<div class="loading-spinner" style="width: 200px; margin-left: -100px;">' +
												'<div class="progress progress-striped active">' +
													'<div class="progress-bar" style="width: 100%;"></div>' +
												'</div>' +
											'</div>';
									}
									if (typeof(source) == 'string') {
										var source_data = {};
										var url = source;
									} else {
										source_data = source.data();
										url = source.attr('href') || source_data.amsUrl;
										var url_getter = ams.getFunctionByName(url);
										if (typeof(url_getter) == 'function') {
											url = url_getter.call(source);
										}
									}
									if (!url)
										return;
									$('body').modalmanager('loading');
									if (url.indexOf('#') == 0) {
										// Inner hidden modal dialog
										$(url).modal('show');
									} else {
										// Remote URL modal dialog
										$.ajax({
											url: url,
											type: 'get',
											cache: source_data.amsAllowCache === undefined ? false : source_data.amsAllowCache,
											data: options,
											success: function(data, status, request) {
												$('body').modalmanager('removeLoading');
												var request_data = ams.ajax.getResponse(request);
												var data_type = request_data.content_type;
												var result = request_data.data;
												switch (data_type) {
													case 'json':
														ams.ajax.handleJSON(result, $($(source).data('ams-json-target') || '#content'));
														break;
													case 'script':
														break;
													case 'xml':
														break;
													case 'html':
													case 'text':
													default:
														var content = $(result);
														var dialog = $('.modal-dialog', content.wrap('<div></div>').parent());
														var dialog_data = dialog.data();
														var data_options = {
															overflow: dialog_data.amsModalOverflow || '.modal-viewport',
															maxHeight: dialog_data.amsModalMaxHeight === undefined
																	? function() {
																		return $(window).height() -
																					$('.modal-header', content).outerHeight(true) -
																					$('footer', content).outerHeight(true) - 85;
																	}
																	: ams.getFunctionByName(dialog_data.amsModalMaxHeight)
														};
														var settings = $.extend({}, data_options, dialog_data.amsModalOptions);
														settings = ams.executeFunctionByName(dialog_data.amsModalInitCallback, dialog, settings) || settings;
														$('<div>').addClass('modal fade')
																  .append(content)
																  .modal(settings);
														ams.initContent(content);
												}
											}
										});
									}
								});
						   });
		},

		/**
		 * Modals shown callback
		 * This callback is used to initialize modal's viewport size
		 */
		shown: function(e) {

			function resetViewport(ev) {
				var top = $('.scrollmarker.top', viewport);
				var top_position = viewport.scrollTop();
				if (top_position > 0)
					top.show();
				else
					top.hide();
				var bottom = $('.scrollmarker.bottom', viewport);
				if (maxHeight + top_position >= viewport.get(0).scrollHeight)
					bottom.hide();
				else
					bottom.show();
			}

			var modal = e.target;
			var viewport = $('.modal-viewport', modal);
			if (viewport.length == 0)
				return;
			var maxHeight = parseInt(viewport.css('max-height'));
			var barWidth = $.scrollbarWidth();
			if (viewport.height() == maxHeight) {
				$('<div></div>').addClass('scrollmarker')
								.addClass('top')
								.css('top', 0)
								.css('width', viewport.width() - barWidth)
								.hide()
								.appendTo(viewport);
				$('<div></div>').addClass('scrollmarker')
								.addClass('bottom')
								.css('top', maxHeight - 20)
								.css('width', viewport.width() - barWidth)
								.appendTo(viewport);
				viewport.scroll(resetViewport);
				viewport.off('resize')
						.on('resize', resetViewport);
			} else {
				$('.scrollmarker', viewport).remove();
			}
		},

		/**
		 * Close modal dialog associated with given context
		 */
		close: function(context) {
			var modal = context.parents('.modal').data('modal');
			if (modal) {
				var manager = $('body').data('modalmanager');
				if (manager && (manager.getOpenModals().indexOf(modal) >= 0))
					modal.hide();
			}
		}
	};


	/**
	 * Plug-ins helpers functions
	 *
	 * These helpers functions are used by several JQuery plug-in extensions.
	 * They have been extracted from these extensions management code to reuse them more easily into
	 * application specific callbacks.
	 */
	MyAMS.helpers = {

		/** Clear Select2 slection */
		select2ClearSelection: function() {
			var source = $(this);
			var label = source.parents('label');
			var target = source.data('ams-select2-target');
			$('INPUT[name="' + target + '"]', label).data('select2').val('');
		},

		/** Select2 selection formatter */
		select2FormatSelection: function(object, container) {
			if (object instanceof Array) {
				$(object).each(function() {
					if (typeof(this) == 'object')
						container.append(this.text);
					else
						container.append(this);
				});
			} else {
				if (typeof(object) == 'object')
					container.append(object.text);
				else
					container.append(object);
			}
		},

		/** Select2 query results callback */
		select2QueryUrlResultsCallback: function(data, page, context) {
			switch (data.status) {
				case 'error':
					ams.skin.messageBox('error', {
						title: ams.i18n.ERROR_OCCURED,
						content: '<h4>' + data.error_message + '</h4>',
						icon: "fa fa-warning animated shake",
						timeout: 10000
					});
					break;
				case 'modal':
					$(this).data('select2').dropdown.hide();
					ams.dialog.open(result.location);
					break;
				default:
					return {
						results: data.results || data,
						more: data.has_more || false,
						context: data.context
					};
			}
		},

		/** Select2 JSON-RPC success callback */
		select2QueryMethodSuccessCallback: function(data, status, options) {
			var result = data.result;
			if (typeof(result) == 'string') {
				try {
					result = JSON.parse(result);
				} catch (e) {}
			}
			switch (result.status) {
				case 'error':
					ams.skin.messageBox('error', {
						title: ams.i18n.ERROR_OCCURED,
						content: '<h4>' + result.error_message + '</h4>',
						icon: "fa fa-warning animated shake",
						timeout: 10000
					});
					break;
				case 'modal':
					$(this).data('select2').dropdown.hide();
					ams.dialog.open(result.location);
					break;
				default:
					options.callback({
						results: result.results || result,
						more: result.has_more || false,
						context: result.context
					});
			}
		}
	};


	/**
	 * Plug-ins management features
	 *
	 * Only basic JQuery, Bootstrap and MyAMS javascript extensions are typically loaded from main page.
	 * Other JQuery plug-ins may be loaded dynamically.
	 * Several JQuery extension plug-ins are already included and pre-configured by MyAMS. Other external
	 * plug-ins can be defined and loaded dynamically using simple "data" attributes.
	 *
	 * WARNING: any plug-in implicated into a form submit process (like JQuery-form or JQuery-progressbar)
	 * must be loaded in a synchronous way. Otherwise, if you use named buttons to submit your forms,
	 * dynamic hidden input fields created by JQuery-validate plug-in will be removed from the form
	 * before the form is submitted!
	 */
	MyAMS.plugins = {

		/**
		 * Initialize list of content plug-ins
		 */
		init: function(element) {

			// Initialize custom data attributes
			ams.plugins.initData(element);

			// Check for disabled plug-ins
			var disabled = new Array();
			$('[data-ams-plugins-disabled]', element).each(function() {
				var plugins = $(this).data('ams-plugins-disabled').split(/\s+/);
				for (var name in plugins) {
					disabled.push(plugins[name]);
				}
			});

			// Run already enabled plug-ins
			for (var index in ams.plugins.enabled) {
				if (disabled.indexOf(index) >= 0)
					continue;
				var plugin = ams.plugins.enabled[index];
				if (typeof(plugin) == 'function')
					plugin(element);
			}

			// Load, run and register new plug-ins
			var name;
			$('[data-ams-plugins]', element).each(function() {
				var source = $(this);
				var plugins = {}
				if (typeof(source.data('ams-plugins')) === 'string') {
					var names = source.data('ams-plugins').split(/\s+/);
					for (var index in names) {
						name = names[index];
						var plugin_options = {
							src: source.data('ams-plugin-' + name + '-src'),
							css: source.data('ams-plugin-' + name + '-css'),
							callback: source.data('ams-plugin-' + name + '-callback'),
							register: source.data('ams-plugin-' + name + '-register'),
							async: source.data('ams-plugin-' + name + '-async')
						}
						plugins[name] = plugin_options;
					}
				} else {
					plugins = source.data('ams-plugins');
				}
				for (name in plugins) {
					if (ams.plugins.enabled[name] === undefined) {
						var plugin = plugins[name];
						ams.getScript(plugin.src, function() {
							var callback = plugin.callback;
							if (callback) {
								var called = ams.getFunctionByName(callback);
								if (typeof(called) == 'function')
									called.apply(source);
								if (plugin.register !== false)
									ams.plugins.enabled[name] = called;
							} else {
								if (plugin.register !== false)
									ams.plugins.enabled[name] = null;
							}
							var css = plugin['css'];
							if (css) {
								ams.getCSS(css, name + '_css');
							}
						}, {
							async: plugin.async === undefined ? true : plugin.async
						});
					}
				}
			});
		},

		/**
		 * Data initializer
		 * This plug-in converts a single JSON "data-ams-data" attribute into a set of several equivalent "data-" attributes.
		 * This way of defining data attributes can be used with HTML templates engines which don't allow you
		 * to create dynamic attributes easily.
		 */
		initData: function(element) {
			$('[data-ams-data]', element).each(function() {
				var handler = $(this);
				var data = handler.data('ams-data');
				for (var index in data) {
					handler.attr('data-' + index, data[index]);
				}
			});
		},

		/**
		 * Map of enabled plug-ins
		 * This map can be extended by external plug-ins.
		 *
		 * Standard MyAMS plug-ins management method generally includes:
		 * - applying a class matching plug-in name on a set of HTML entities to apply the plug-in
		 * - defining a set of data-attributes on each of these entities to customize the plug-in
		 * For each standard plug-in, you can also provide an options object (to define plug-in options not handled
		 * by default MyAMS initialization engine) and an initialization callback (to define these options dynamically).
		 * Another callback can also be provided to be called after plug-in initialization.
		 */
		enabled: {

			/**
			 * Label hints
			 */
			hint: function(element) {
				var hints = $('.hint:not(:parents(.nohints))', element);
				if (hints.length > 0)
					ams.ajax.check($.fn.tipsy,
								   ams.baseURL + 'ext/jquery-tipsy' + (ams.devmode ? '.js' : '.min.js'),
								   function() {
										ams.getCSS(ams.baseURL + '../css/ext/jquery-tipsy' + (ams.devmode ? '.css' : '.min.css'),
												  'jquery-tipsy');
										hints.each(function() {
											var hint = $(this);
											var data = hint.data();
											var data_options = {
												html: data.amsHintHtml,
												title: ams.getFunctionByName(data.amsHintTitleGetter) || function() {
													var hint = $(this);
													return hint.attr('original-title') ||
														   hint.attr(data.amsHintTitleAttr || 'title') ||
														   (data.amsHintHtml ? hint.html() : hint.text());
												},
												opacity: data.amsHintOpacity,
												gravity: data.amsHintGravity || 'sw',
												offset: data.amsHintOffset || 0
											};
											var settings = $.extend({}, data_options, data.amsHintOptions);
											settings = ams.executeFunctionByName(data.amsHintInitCallback, hint, settings) || settings;
											var plugin = hint.tipsy(settings);
											ams.executeFunctionByName(data.amsHintAfterInitCallback, hint, plugin, settings);
										});
								   });
			},

			/**
			 * Fieldset legend switcher
			 */
			switcher: function(element) {
				$('LEGEND.switcher', element).each(function() {
					var legend = $(this);
					var fieldset = legend.parent('fieldset');
					var data = legend.data();
					if (!data.amsSwitcher) {
						$('<i class="fa fa-fw"></i>')
							.prependTo($(this))
							.addClass(data.amsSwitcherState == 'open' ?
									  (data.amsSwitcherMinusClass || 'fa-minus') :
									  (data.amsSwitcherPlusClass || 'fa-plus'));
						legend.on('click', function(e) {
							e.preventDefault();
							var veto = {};
							legend.trigger('ams.switcher.before-switch', [legend, veto]);
							if (veto.veto)
								return;
							if (fieldset.hasClass('switched')) {
								fieldset.removeClass('switched');
								$('.fa', legend).removeClass(data.amsSwitcherPlusClass || 'fa-plus')
												.addClass(data.amsSwitcherMinusClass || 'fa-minus');
								legend.trigger('ams.switcher.opened', [legend]);
								var id = legend.attr('id');
								if (id) {
									$('legend.switcher[data-ams-switcher-sync="'+id+'"]', fieldset).each(function() {
										var switcher = $(this);
										if (switcher.parents('fieldset').hasClass('switched'))
											switcher.click();
									});
								}
							} else {
								fieldset.addClass('switched');
								$('.fa', legend).removeClass(data.amsSwitcherMinusClass || 'fa-minus')
												.addClass(data.amsSwitcherPlusClass || 'fa-plus');
								legend.trigger('ams.switcher.closed', [legend]);
							}
						});
						if (data.amsSwitcherState != 'open')
							fieldset.addClass('switched');
						legend.data('ams-switcher', 'on');
					}
				});
			},

			/**
			 * Fieldset legend checker
			 */
			checker: function(element) {
				$('LEGEND.checker', element).each(function() {
					var legend = $(this);
					var fieldset = legend.parent('fieldset');
					var data = legend.data();
					if (!data.amsChecker) {
						var checker = $('<label class="checkbox"></label>');
						var fieldname = data.amsCheckerFieldname || ('checker_'+ams.generateId());
						var prefix = data.amsCheckerHiddenPrefix;
						var hidden = null;
						var checkedValue = data.amsCheckerHiddenValueOn || 'true';
						var uncheckedValue = data.amsCheckerHiddenValueOff || 'false';
						if (prefix) {
							hidden = $('<input type="hidden">').attr('name', prefix + fieldname)
															   .val(data.amsCheckerState == 'on' ? checkedValue : uncheckedValue)
															   .prependTo(legend);
						}
						var input = $('<input type="checkbox">').attr('name', fieldname)
																.attr('id', fieldname.replace(/\./, '_'))
																.data('ams-checker-hidden-input', hidden)
																.data('ams-checker-init', true)
																.val(true)
																.attr('checked', data.amsCheckerState == 'on' ? 'checked' : null);
						if (data.amsCheckerReadonly) {
							input.attr('disabled', 'disabled');
						} else {
							input.on('change', function(e) {
								e.preventDefault();
								var veto = {};
								legend.trigger('ams.checker.before-switch', [legend, veto]);
								if (veto.veto)
									return;
								var isChecked = $(this).is(':checked');
								ams.executeFunctionByName(data.amsCheckerChangeHandler, legend, isChecked);
								if (!data.amsCheckerCancelDefault) {
									var hidden = input.data('ams-checker-hidden-input');
									if (isChecked) {
										if (data.amsCheckerMode == 'disable')
											fieldset.removeAttr('disabled');
										else
											fieldset.removeClass('switched');
										if (hidden)
											hidden.val(checkedValue);
										$('[data-required]', fieldset).attr('required', 'required');
										legend.trigger('ams.checker.opened', [legend]);
									} else {
										if (data.amsCheckerMode == 'disable')
											fieldset.attr('disabled', 'disabled');
										else
											fieldset.addClass('switched');
										if (hidden)
											hidden.val(uncheckedValue);
										$('[data-required]', fieldset).removeAttr('required');
										legend.trigger('ams.checker.closed', [legend]);
									}
								}
							});
						}
						input.appendTo(checker);
						$('.legend', legend).attr('for', input.attr('id'));
						checker.append('<i></i>')
							   .prependTo(legend);
						var required = $('[required]', fieldset);
						required.attr('data-required', true);
						if (data.amsCheckerState == 'on') {
							input.attr('checked', true);
						} else {
							if (data.amsCheckerMode == 'disable')
								fieldset.attr('disabled', 'disabled');
							else
								fieldset.addClass('switched');
							required.removeAttr('required');
						}
						legend.data('ams-checker', 'on');
					}
				});
			},

			/**
			 * Sliders
			 */
			slider: function(element) {
				var sliders = $('.slider', element);
				if (sliders.length > 0) {
					ams.ajax.check($.fn.slider,
								   ams.baseURL + 'ext/bootstrap-slider.min.js',
								   function() {
										sliders.each(function() {
											var slider = $(this);
											var data = slider.data();
											var data_options = {};
											var settings = $.extend({}, data_options, slider.data.amsSliderOptions);
											settings = ams.executeFunctionByName(data.amsSliderInitCallback, slider, settings) || settings;
											var plugin = slider.slider(settings);
											ams.executeFunctionByName(data.amsSliderAfterInitCallback, slider, plugin, settings);
										});
								   });
				}
			},

			/**
			 * Select2 plug-in
			 */
			select2: function(element) {
				var selects = $('.select2', element);
				if (selects.length > 0) {
					ams.ajax.check($.fn.select2,
								   ams.baseURL + 'ext/jquery-select2-3.4.5' + (ams.devmode ? '.js' : '.min.js'),
								   function() {
										selects.each(function() {
											var select = $(this);
											var data = select.data();
											var data_options = {
												placeholder: data.amsSelect2Placeholder,
												multiple: data.amsSelect2Multiple,
												minimumInputLength: data.amsSelect2MinimumInputLength || 0,
												maximumSelectionSize: data.amsSelect2MaximumSelectionSize,
												openOnEnter: data.amsSelect2EnterOpen === undefined ? true : data.amsSelect2EnterOpen,
												allowClear: data.amsSelect2AllowClear === undefined ? true : data.amsSelect2AllowClear,
												width: data.amsSelect2Width || '100%',
												initSelection: ams.getFunctionByName(data.amsSelect2InitSelection),
												formatSelection: data.amsSelect2FormatSelection === undefined
																	? ams.helpers.select2FormatSelection
																	: ams.getFunctionByName(data.amsSelect2FormatSelection),
												formatResult: ams.getFunctionByName(data.amsSelect2FormatResult),
												formatNoMatches: data.amsSelect2FormatResult === undefined
																	? function(term) {
																		return ams.i18n.SELECT2_NOMATCHES;
																	}
																	: ams.getFunctionByName(data.amsSelect2FormatResult),
												formatInputTooShort: data.amsSelect2FormatInputTooShort === undefined
																	? function(input, min) {
																		var n = min - input.length;
																		return ams.i18n.SELECT2_INPUT_TOOSHORT
																						.replace(/\{0\}/, n)
																						.replace(/\{1\}/, n == 1 ? "" : ams.i18n.SELECT2_PLURAL);
																	}
																	: ams.getFunctionByName(data.amsSelect2FormatInputTooShort),
												formatInputTooLong: data.amsSelect2FormatInputTooLong === undefined
																	? function(input, max) {
																		var n = input.length - max;
																		return ams.i18n.SELECT2_INPUT_TOOLONG
																						.replace(/\{0\}/, n)
																						.replace(/\{1\}/, n == 1 ? "" : ams.i18n.SELECT2_PLURAL);
																	}
																	: ams.getFunctionByName(data.amsSelect2FormatInputTooLong),
												formatSelectionTooBig: data.amsSelect2FormatSelectionTooBig === undefined
																	? function(limit) {
																		return ams.i18n.SELECT2_SELECTION_TOOBIG
																						.replace(/\{0\}/, limit)
																						.replace(/\{1\}/, limit == 1 ? "" : ams.i18n.SELECT2_PLURAL);
																	}
																	: ams.getFunctionByName(data.amsSelect2FormatSelectionTooBig),
												formatLoadMore: data.amsSelect2FormatLoadMore === undefined
																	? function (pageNumber) {
																		return ams.i18n.SELECT2_LOADMORE;
																	}
																	: ams.getFunctionByName(data.amsSelect2FormatLoadMore),
												formatSearching: data.amsSelect2FormatSearching === undefined
																	? function() {
																		return ams.i18n.SELECT2_SEARCHING;
																	}
																	: ams.getFunctionByName(data.amsSelect2FormatSearching),
												separator: data.amsSelect2Separator || ',',
												tokenSeparators: data.amsSelect2TokensSeparators || [','],
												tokenizer: ams.getFunctionByName(data.amsSelect2Tokenizer)
											};

											switch (select.context.type) {
												case 'text':
												case 'hidden':
													if (!data_options.initSelection) {
														var values_data = select.data('ams-select2-values');
														if (values_data) {
															data_options.initSelection = function(element, callback) {
																var data = [];
																$(element.val().split(data_options.separator)).each(function() {
																	data.push({id: this,
																			   text: values_data[this] || this});
																});
																callback(data);
															}
														}
													}
													break;
												default:
													break;
											}

											if (data.amsSelect2Query) {
												// Custom query method
												data_options.query = ams.getFunctionByName(data.amsSelect2Query);
												data_options.minimumInputLength = data.amsSelect2MinimumInputLength || 1;
											} else if (data.amsSelect2QueryUrl) {
												// AJAX query
												data_options.ajax = {
													url: data.amsSelect2QueryUrl,
													quietMillis: data.amsSelect2QuietMillis || 200,
													type: data.amsSelect2QueryType || 'POST',
													dataType: data.amsSelect2QueryDatatype || 'json',
													data: function(term, page, context) {
														var options = {};
														options[data.amsSelect2QueryParamName || 'query'] = term;
														options[data.amsSelect2PageParamName || 'page'] = page;
														options[data.amsSelect2ContextParamName || 'context'] = context;
														return $.extend({}, options, data.amsSelect2QueryOptions);
													},
													results: ams.helpers.select2QueryUrlResultsCallback
												};
												data_options.minimumInputLength = data.amsSelect2MinimumInputLength || 1;
											} else if (data.amsSelect2QueryMethod) {
												// JSON-RPC query
												data_options.query = function(options) {
													var settings = {
														url: data.amsSelect2MethodTarget || ams.jsonrpc.getAddr(),
														type: data.amsSelect2MethodType || 'POST',
														cache: false,
														method: data.amsSelect2QueryMethod,
														params: data.amsSelect2QueryParams || {},
														success: function(data, status) {
															return ams.helpers.select2QueryMethodSuccessCallback.call(select, data, status, options);
														},
														error: ams.error.show
													};
													settings.params[data.amsSelect2QueryParamName || 'query'] = options.term;
													settings.params[data.amsSelect2PageParamName || 'page'] = options.page;
													settings.params[data.amsSelect2ContextParamName || 'context'] = options.context;
													settings = $.extend({}, settings, data.amsSelect2QueryOptions);
													settings = ams.executeFunctionByName(data.amsSelect2QueryInitCallback, select, settings) || settings;
													ams.ajax.check($.jsonRpc,
																   ams.baseURL + 'ext/jquery-jsonrpc' + (ams.devmode ? '.js' : '.min.js'),
																   function() {
																		$.jsonRpc(settings);
																   });
												};
												data_options.minimumInputLength = data.amsSelect2MinimumInputLength || 1;
											} else if (data.amsSelect2Tags) {
												// Tags mode
												data_options.tags = data.amsSelect2Tags;
											} else if (data.amsSelect2Data) {
												// Provided data mode
												data_options.data = data.amsSelect2Data;
											}

											if (data.amsSelect2EnableFreeTags) {
												data_options.createSearchChoice = function(term) {
													return {id: term,
															text: (data.amsSelect2FreeTagsPrefix || ams.i18n.SELECT2_FREETAG_PREFIX) + term};
												};
											}

											var settings = $.extend({}, data_options, data.amsSelect2Options);
											settings = ams.executeFunctionByName(data.amsSelect2InitCallback, select, settings) || settings;
											var plugin = select.select2(settings);
											ams.executeFunctionByName(data.amsSelect2AfterInitCallback, select, plugin, settings);

											select.on('change', function() {
												var validator = $(select.get(0).form).data('validator');
												if (validator !== undefined)
													$(select).valid();
											});
										});
								   });
				}
			},

			/**
			 * Edit mask plug-in
			 */
			maskedit: function(element) {
				var masks = $('[data-mask]', element);
				if (masks.length > 0) {
					ams.ajax.check($.fn.mask,
								   ams.baseURL + 'ext/jquery-maskedinput-1.3.1.min.js',
								   function() {
										masks.each(function() {
											var mask = $(this);
											var data = mask.data();
											var data_options = {
												placeholder: data.amsMaskeditPlaceholder || 'X'
											};
											var settings = $.extend({}, data_options, data.amsMaskeditOptions);
											settings = ams.executeFunctionByName(data.amsMaskeditInitCallback, mask, settings) || settings;
											var plugin = mask.mask(mask.attr('data-mask'), settings);
											ams.executeFunctionByName(data.amsMaskeditAfterInitCallback, mask, plugin, settings);
										});
								   });
				}
			},

			/**
			 * JQuery-UI date picker
			 */
			datepicker: function(element) {
				var datepickers = $('.datepicker', element);
				if (datepickers.length > 0) {
					datepickers.each(function() {
						var picker = $(this);
						var data = picker.data();
						var data_options = {
							dateFormat: data.amsDatepickerFormat || 'dd/mm/yy',
							prevText: '<i class="fa fa-chevron-left"></i>',
							nextText: '<i class="fa fa-chevron-right"></i>',
							changeMonth: data.amsDatepickerChangeMonth,
							changeYear: data.amsDatepickerChangeYear,
							showButtonPanel: !data.amsDatepickerHidePanel
						};
						var settings = $.extend({}, data_options, data.amsDatepickerOptions);
						settings = ams.executeFunctionByName(data.amsDatepickerInitCallback, picker, settings) || settings;
						var plugin = picker.datepicker(settings);
						ams.executeFunctionByName(data.amsDatepickerAfterInitCallback, picker, plugin, settings);
					});
				}
			},

			/**
			 * JQuery typeahead plug-in
			 */
			typeahead: function(element) {
				var typeaheads = $('.typeahead', element);
				if (typeaheads.length > 0) {
					ams.ajax.check($.fn.typeahead,
								   ams.baseURL + 'ext/jquery-typeahead' + (ams.devmode ? '.js' : '.min.js'),
								   function() {
										typeaheads.each(function() {
											var input = $(this);
											var data = input.data();
											var data_options = {};
											var settings = $.extend({}, data_options, data.amsTypeaheadOptions);
											settings = ams.executeFunctionByName(data.amsTypeaheadInitCallback, input, settings) || settings;
											var plugin = input.typeahead(settings);
											ams.executeFunctionByName(data.amsTypeaheadAfterInitCallback, input, plugin, settings);
										});
								   });
				}
			},

			/**
			 * JQuery validation plug-in
			 */
			validate: function(element) {
				var forms = $('FORM:not([novalidate])', element);
				if (forms.length > 0) {
					ams.ajax.check($.fn.validate,
								   ams.baseURL + 'ext/jquery-validate-1.11.1' + (ams.devmode ? '.js' : '.min.js'),
								   function(first_load) {
										if (first_load) {
											$.validator.setDefaults({
												highlight: function(element) {
													$(element).closest('.form-group, label:not(:parents(.form-group))').addClass('state-error');
												},
												unhighlight: function(element) {
													$(element).closest('.form-group, label:not(:parents(.form-group))').removeClass('state-error');
												},
												errorElement: 'span',
												errorClass: 'state-error',
												errorPlacement: function(error, element) {
													if (element.parent('label').length)
														error.insertAfter(element.parent());
													else
														error.insertAfter(element);
												}
											});
											if (ams.plugins.i18n) {
												for (var key in ams.plugins.i18n.validate) {
													var message = ams.plugins.i18n.validate[key];
													if ((typeof(message) == 'string') &&
														(message.indexOf('{0}') > -1))
														ams.plugins.i18n.validate[key] = $.validator.format(message);
												}
												$.extend($.validator.messages, ams.plugins.i18n.validate);
											}
										}
										forms.each(function() {
											var form = $(this);
											var data = form.data();
											var data_options = {
												ignore: null,
												submitHandler: form.attr('data-async') !== undefined
															   ? data.amsFormSubmitHandler === undefined
																	? function() {
																		// JQuery-form plug-in must be loaded synchronously!!
																		// Otherwise, hidden input fields created by jquery-validate plug-in
																		// and matching named buttons will be deleted (on first form submit)
																		// before JQuery-form plug-in can get them when submitting the form...
																		ams.ajax.check($.fn.ajaxSubmit,
																					   ams.baseURL + 'ext/jquery-form-3.49' + (ams.devmode ? '.js' : '.min.js'));
																		return ams.form.submit(form);
																	}
																	: ams.getFunctionByName(data.amsFormSubmitHandler)
															   : undefined
											};
											var settings = $.extend({}, data_options, data.amsValidateOptions);
											settings = ams.executeFunctionByName(data.amsValidateInitCallback, form, settings) || settings;
											var plugin = form.validate(settings);
											ams.executeFunctionByName(data.amsValidateAfterInitCallback, form, plugin, settings);
										});
								   });
				}
			},

			/**
			 * JQuery dataTables
			 */
			datatable: function(element) {
				var tables = $('.datatable', element);
				if (tables.length > 0) {
					ams.ajax.check($.fn.dataTable,
								   ams.baseURL + 'ext/jquery-dataTables-1.9.4' + (ams.devmode ? '.js' : '.min.js'),
								   function(first_load) {
										if (first_load) {
											$.fn.dataTableExt.oSort['numeric-comma-asc']  = function(a, b) {
												var x = a.replace(/,/, ".").replace(/ /g, '');
												var y = b.replace(/,/, ".").replace(/ /g, '');
												x = parseFloat(x);
												y = parseFloat(y);
												return ((x < y) ? -1 : ((x > y) ?  1 : 0));
											};
											$.fn.dataTableExt.oSort['numeric-comma-desc'] = function(a, b) {
												var x = a.replace(/,/, ".").replace(/ /g, '');
												var y = b.replace(/,/, ".").replace(/ /g, '');
												x = parseFloat(x);
												y = parseFloat(y);
												return ((x < y) ?  1 : ((x > y) ? -1 : 0));
											};
										}
										$(tables).each(function() {
											ams.ajax.check($.fn.dataTableExt.oPagination['bootstrap_full'],
														   ams.baseURL + 'myams-dataTables' + (ams.devmode ? '.js' : '.min.js'));
											var table = $(this);
											var data = table.data();
											var extensions = (data.amsDatatableExtensions || '').split(/\s+/);
											var sDom = data.amsDatatableSdom ||
												"W" +
												((extensions.indexOf('colreorder') >= 0 ||
												  extensions.indexOf('colreorderwithresize') >= 0) ? 'R' : '') +
												"<'dt-top-row'" +
												(extensions.indexOf('colvis') >= 0 ? 'C' : '') +
												((data.amsDatatablePagination === false ||
												  data.amsDatatablePaginationSize === false) ? '' : 'L') +
												(data.amsDatatableGlobalFilter === false ? '' : 'F') +
												">r<'dt-wrapper't" +
												(extensions.indexOf('scroller') >= 0 ? 'S' : '') +
												"><'dt-row dt-bottom-row'<'row'<'col-sm-6'" +
												(data.amsDatatableInformation === false ? '': 'i') +
												"><'col-sm-6 text-right'p>>";
											var data_options = {
												bJQueryUI: false,
												bFilter: data.amsDatatableGlobalFilter !== false,
												bPaginate: data.amsDatatablePagination !== false,
												bInfo: data.amsDatatableInfo !== false,
												bSort: data.amsDatatableSort !== false,
												bDeferRender: true,
												bAutoWidth: false,
												iDisplayLength: data.amsDatatableDisplayLength || 25,
												sPaginationType: data.amsDatatablePaginationType || 'bootstrap_full',
												sDom: sDom,
												oLanguage: ams.plugins.i18n.datatables,
												fnInitComplete: function(oSettings, json) {
													$('.ColVis_Button').addClass('btn btn-default btn-sm')
																	   .html((ams.plugins.i18n.datatables.sColumns || "Columns") + ' <i class="fa fa-fw fa-caret-down"></i>');
												}
											};
											var settings = $.extend({}, data_options, data.amsDatatableOptions);
											var index;
											if (extensions.length > 0) {
												for (index in extensions) {
													switch (extensions[index]) {
														case 'autofill':
															ams.ajax.check($.fn.dataTable.AutoFill,
																		   ams.baseURL + 'ext/jquery-dataTables-autoFill' + (ams.devmode ? '.js' : '.min.js'));
															break;
														case 'columnfilter':
															ams.ajax.check($.fn.columnFilter,
																		   ams.baseURL + 'ext/jquery-dataTables-columnFilter' + (ams.devmode ? '.js' : '.min.js'));
															break;
														case 'colreorder':
															ams.ajax.check($.fn.dataTable.ColReorder,
																		   ams.baseURL + 'ext/jquery-dataTables-colReorder' + (ams.devmode ? '.js' : '.min.js'));
															break;
														case 'colreorderwithresize':
															ams.ajax.check($.fn.dataTable.ColReorder,
																		   ams.baseURL + 'ext/jquery-dataTables-colReorderWithResize' + (ams.devmode ? '.js' : '.min.js'));
															break;
														case 'colvis':
															ams.ajax.check($.fn.dataTable.ColVis,
																		   ams.baseURL + 'ext/jquery-dataTables-colVis' + (ams.devmode ? '.js' : '.min.js'));
															var cv_default = {
																activate: 'click',
																sAlign: 'right'
															};
															settings.oColVis = $.extend({}, cv_default, data.amsDatatableColvisOptions);
															break;
														case 'editable':
															ams.ajax.check($.fn.editable,
																		   ams.baseURL + 'ext/jquery-jeditable' + (ams.devmode ? '.js' : '.min.js'));
															ams.ajax.check($.fn.makeEditable,
																		   ams.baseURL + 'ext/jquery-dataTables-editable' + (ams.devmode ? '.js' : '.min.js'));
															break;
														case 'fixedcolumns':
															ams.ajax.check($.fn.dataTable.FixedColumns,
																		   ams.baseURL + 'ext/jquery-dataTables-fixedColumns' + (ams.devmode ? '.js' : '.min.js'));
															break;
														case 'fixedheader':
															ams.ajax.check($.fn.dataTable.FixedHeader,
																		   ams.baseURL + 'ext/jquery-dataTables-fixedHeader' + (ams.devmode ? '.js' : '.min.js'));
															break;
														case 'keytable':
															ams.ajax.check(window.KeyTable,
																		   ams.baseURL + 'ext/jquery-dataTables-keyTable' + (ams.devmode ? '.js' : '.min.js'));
															break;
														case 'rowgrouping':
															ams.ajax.check($.fn.rowGrouping,
																		   ams.baseURL + 'ext/jquery-dataTables-rowGrouping' + (ams.devmode ? '.js' : '.min.js'));
															break;
														case 'rowreordering':
															ams.ajax.check($.fn.rowReordering,
																		   ams.baseURL + 'ext/jquery-dataTables-rowReordering' + (ams.devmode ? '.js' : '.min.js'));
															break;
														case 'scroller':
															ams.ajax.check($.fn.dataTable.Scroller,
																		   ams.baseURL + 'ext/jquery-dataTables-scroller' + (ams.devmode ? '.js' : '.min.js'));
															break;
														default:
															break;
													}
												}
											}
											settings = ams.executeFunctionByName(data.amsDatatableInitCallback, table, settings) || settings;
											var plugin = table.dataTable(settings);
											ams.executeFunctionByName(data.amsDatatableAfterInitCallback, table, plugin, settings);
											if (extensions.length > 0) {
												for (index in extensions) {
													switch(extensions[index]) {
														case 'autofill':
															var af_settings = $.extend({}, data.amsDatatableAutofillOptions, settings.autofill);
															af_settings = ams.executeFunctionByName(data.amsDatatableAutofillInitCallback, table, af_settings) || af_settings;
															table.data('ams-autofill', data.amsDatatableAutofillConstructor === undefined
																						? new $.fn.dataTable.AutoFill(table, af_settings)
																						: ams.executeFunctionByName(data.amsDatatableAutofillConstructor, table, plugin, af_settings));
															break;
														case 'columnfilter':
															var cf_default = {
																sPlaceHolder: 'head:after'
															};
															var cf_settings = $.extend({}, cf_default, data.amsDatatableColumnfilterOptions, settings.columnfilter);
															cf_settings = ams.executeFunctionByName(data.amsDatatableColumnfilterInitCallback, table, cf_settings) || cf_settings;
															table.data('ams-columnfilter', data.amsDatatableColumnfilterConstructor === undefined
																						? plugin.columnFilter(cf_settings)
																						: ams.executeFunctionByName(data.amsDatatableColumnfilterConstructor, table, plugin, cf_settings));
															break;
														case 'editable':
															var ed_settings = $.extend({}, data.amsDatatableEditableOptions, settings.editable);
															ed_settings = ams.executeFunctionByName(data.amsDatatableEditableInitCallback, table, ed_settings) || ed_settings;
															table.data('ams-editable', data.amsDatatableEditableConstructor === undefined
																						? table.makeEditable(ed_settings)
																						: ams.executeFunctionByName(data.amsDatatableEditableConstructor, table, plugin, ed_settings));
															break;
														case 'fixedcolumns':
															var fc_settings = $.extend({}, data.amsDatatableFixedcolumnsOptions, settings.fixedcolumns);
															fc_settings = ams.executeFunctionByName(data.amsDatatableFixedcolumnsInitCallback, table, fc_settings) || fc_settings;
															table.data('ams-fixedcolumns', data.amsDatatableFixedcolumnsConstructor === undefined
																						? new $.fn.dataTable.FixedColumns(table, fc_settings)
																						: ams.executeFunctionByName(data.amsDatatableFixedcolumnsConstructor, table, plugin, fc_settings));
															break;
														case 'fixedheader':
															var fh_settings = $.extend({}, data.amsDatatableFixedheaderOptions, settings.fixedheader);
															fh_settings = ams.executeFunctionByName(data.amsDatatableFixedheadeInitCallback, table, fh_settings) || fh_settings;
															table.data('ams-fixedheader', data.amsDatatableFixedheaderConstructor === undefined
																						? new $.fn.dataTable.FixedHeader(table, fh_settings)
																						: ams.executeFunctionByName(data.amsDatatableFixedheaderConstructor, table, plugin, fh_settings));
															break;
														case 'keytable':
															var kt_default = {
																table: table.get(0),
																datatable: plugin
															};
															var kt_settings = $.extend({}, kt_default, data.amsDatatableKeytableOptions, settings.keytable);
															kt_settings = ams.executeFunctionByName(data.amsDatatableKeytableInitCallback, table, kt_settings) || kt_settings;
															table.data('ams-keytable', data.amsDatatableKeytableConstructor === undefined
																						? new KeyTable(kt_settings)
																						: ams.executeFunctionByName(data.amsDatatableKeytableConstructor, table, plugin, kt_settings));
															break;
														case 'rowgrouping':
															var rg_settings = $.extend({}, data.amsDatatableRowgroupingOptions, settings.rowgrouping);
															rg_settings = ams.executeFunctionByName(data.amsDatatableRowgroupingInitCallback, table, rg_settings) || rg_settings;
															table.data('ams-rowgrouping', data.amsDatatableRowgroupingConstructor === undefined
																						? table.rowGrouping(rg_settings)
																						: ams.executeFunctionByName(data.amsDatatableRowgroupingConstructor, table, plugin, rg_settings));
															break;
														case 'rowreordering':
															var rr_settings = $.extend({}, data.amsDatatableRowreorderingOptions, settings.rowreordering);
															rr_settings = ams.executeFunctionByName(data.amsDatatableRowreorderingInitCallback, table, rr_settings) || rr_settings;
															table.data('ams-rowreordering', data.amsDatatableRowreorderingConstructor === undefined
																						? table.rowReordering(rr_settings)
																						: ams.executeFunctionByName(data.amsDatatableRowreorderingConstructor, table, plugin, rr_settings));
															break;
														default:
															break;
													}
												}
											}
											var finalizers = (data.amsDatatableFinalizeCallback || '').split(/\s+/);
											if (finalizers.length > 0) {
												for (index in finalizers) {
													ams.executeFunctionByName(finalizers[index], table, plugin, settings);
												}
											}
										});
								   });
				}
			},

			/**
			 * Sparkline graphs
			 */
			graphs: function(element) {
				var graphs = $('.sparkline', element);
				if (graphs.length > 0) {
					ams.ajax.check(ams.graphs,
								   ams.baseURL + 'myams-graphs' + (ams.devmode ? '.js' : '.min.js'),
								   function() {
										ams.graphs.init(graphs);
								   });
				}
			},

			/**
			 * Custom scrollbars
			 */
			scrollbars: function(element) {
				var scrollbars = $('.scrollbar', element);
				if (scrollbars.length > 0) {
					ams.ajax.check($.event.special.mousewheel,
								   ams.baseURL + 'ext/jquery-mousewheel.min.js',
								   function() {
										ams.ajax.check($.fn.mCustomScrollbar,
													   ams.baseURL + 'ext/jquery-mCustomScrollbar' + (ams.devmode ? '.js' : '.min.js'),
													   function(first_load) {
															if (first_load)
																ams.getCSS(ams.baseURL + '../css/ext/jquery-mCustomScrollbar.css',
																		  'jquery-mCustomScrollbar');
															scrollbars.each(function() {
																var scrollbar = $(this);
																var data = scrollbar.data();
																var data_options = {
																	theme: data.amsScrollbarTheme || 'light'
																};
																var settings = $.extend({}, data_options, data.amsScrollbarOptions);
																settings = ams.executeFunctionByName(data.amsScrollbarInitCallback, scrollbar, settings) || settings;
																var plugin = scrollbar.mCustomScrollbar(settings);
																ams.executeFunctionByName(data.amsScrollbarAfterInitCallback, scrollbar, plugin, settings);
															});
													   });
									});
				}
			}
		}
	};


	/**
	 * Callbacks management features
	 */
	MyAMS.callbacks = {

		/**
		 * Initialize list of callbacks
		 *
		 * Callbacks are initialized each time a page content is loaded and integrated into page's DOM.
		 * Unlike plug-ins, callbacks are called once in current's content context but are not kept into
		 * browser's memory for future use.
		 * Callbacks are defined via several data attributes:
		 * - data-ams-callback: name of function callback
		 * - data-ams-callback-source: source URL of file containing callback's function; can contain variables names
		 *   if enclosed between braces
		 * - data-ams-callback-options: JSON object containing callback options
		 */
		init: function(element) {
			$('[data-ams-callback]', element).each(function() {
				var self = this;
				var data = $(self).data();
				var callback = ams.getFunctionByName(data.amsCallback);
				if (callback === undefined) {
					if (data.amsCallbackSource) {
						ams.getScript(data.amsCallbackSource,
									  function() {
										ams.executeFunctionByName(data.amsCallback, self, data.amsCallbackOptions);
									  });
					} else if (window.console) {
						console.warn("Undefined callback: " + data.amsCallback);
					}
				} else {
					callback.call(self, data.amsCallbackOptions);
				}
			})
		},

		/**
		 * Standard alert message callback
		 *
		 * An alert is an HTML div included on top of a "parent's" body
		 * Alert options include:
		 * - a status: 'info', 'warning', 'error' or 'success'
		 * - a parent: jQuery selector of parent's element
		 * - a header: alert's title
		 * - a subtitle
		 * - a message body
		 * - a boolean margin marker; if true, a 10 pixels margin will be added to alert's body
		 */
		alert: function(options) {
			var data = $(this).data();
			var settings = $.extend({}, options, data.amsAlertOptions);
			var parent = $(data.amsAlertParent || settings.parent || this);
			var status = data.amsAlertStatus || settings.status || 'info';
			var header = data.amsAlertHeader || settings.header;
			var message = data.amsAlertMessage || settings.message;
			var subtitle = data.amsAlertSubtitle || settings.subtitle;
			var margin = data.amsAlertMargin === undefined ? (settings.margin === undefined ? false : settings.margin) : data.amsAlertMargin;
			ams.skin.alert(parent, status, header, message, subtitle, margin);
		},

		/**
		 * Standard message box callback
		 *
		 * Message boxes are small informations messages displayed on bottom right page's corner
		 * Message box options include:
		 * - data-ams-messagebox-status: determines message box color; given as 'info', 'warning', 'error' or 'success'
		 * - data-ams-messagebox-title: message's title
		 * - data-ams-messagebox-content: message's HTML content
		 * - data-ams-messagebox-icon: if given, CSS class of message's icon
		 * - data-ams-messagebox-number: if given, a small error/message number displayed below message
		 * - data-ams-messagebox-timeout: if given, the message box will be automatically hidden passed this number
		 *   of milliseconds
		 * - data-ams-messagebox-callback: a callback's name, which will be called when message box is closed
		 */
		messageBox: function(options) {
			var data = $(this).data();
			var data_options = $.extend({}, options, data.amsMessageboxOptions);
			var settings = $.extend({}, data_options, {
				title: data.amsMessageboxTitle || data_options.title || '',
				content: data.amsMessageboxContent || data_options.content || '',
				icon: data.amsMessageboxIcon || data_options.icon,
				number: data.amsMessageboxNumber || data_options.number,
				timeout: data.amsMessageboxTimeout || data_options.icon
			});
			var status = data.amsMessageboxStatus || data_options.status || 'info';
			var callback = ams.getFunctionByName(data.amsMessageboxCallback || data_options.callback);
			ams.skin.messageBox(status, settings, callback);
		},

		/**
		 * Standard small box callback
		 *
		 * Small boxes are notification messages displayed on top right page's corner.
		 * Small box options include:
		 * - data-ams-smallbox-status: determines message box color; given as 'info', 'warning', 'error' or 'success'
		 * - data-ams-smallbox-title: message's title
		 * - data-ams-smallbox-content: message's HTML content
		 * - data-ams-smallbox-icon: if given, CSS class of message's icon
		 * - data-ams-smallbox-icon-small: if given, CSS class of small message's icon
		 * - data-ams-smallbox-timeout: if given, the message box will be automatically hidden passed this number
		 *   of milliseconds
		 * - data-ams-smallbox-callback: a callback's name, which will be called when message box is closed
		 */
		smallBox: function(options) {
			var data = $(this).data();
			var data_options = $.extend({}, options, data.amsSmallboxOptions);
			var settings = $.extend({}, data_options, {
				title: data.amsSmallboxTitle || data_options.title || '',
				content: data.amsSmallboxContent || data_options.content || '',
				icon: data.amsSmallboxIcon || data_options.icon,
				iconSmall: data.amsSmallboxIconSmall || data_options.iconSmall,
				timeout: data.amsSmallboxTimeout || data_options.icon
			});
			var status = data.amsSmallboxStatus || data_options.status || 'info';
			var callback = ams.getFunctionByName(data.amsSmallboxCallback || data_options.callback);
			ams.skin.smallBox(status, settings, callback);
		}
	};


	/**
	 * Events management
	 */
	MyAMS.events = {

		/**
		 * Initialize events listeners
		 *
		 * "data-ams-events-handlers" is a data attribute containing a JSON object where:
		 *  - each key is an event name
		 *  - value is a callback name.
		 * For example: data-ams-events-handlers='{"change": "MyAPP.events.changeListener"}'
		 */
		init: function(element) {
			$('[data-ams-events-handlers]', element).each(function() {
				var element = $(this);
				var handlers = element.data('ams-events-handlers');
				for (var event in handlers) {
					element.on(event, ams.getFunctionByName(handlers[event]));
				}
			});
		}
	};


	/**
	 * Generic skin features
	 */
	MyAMS.skin = {

		/**
		 * Compute navigation page height
		 */
		_setPageHeight: function() {
			var main_height = $('#main').height();
			var menu_height = ams.left_panel.height();
			var window_height = $(window).height() - ams.navbar_height;
			if (main_height > window_height) {
				ams.left_panel.css('min-height', main_height);
				ams.root.css('min-height', main_height + ams.navbar_height);
			} else {
				ams.left_panel.css('min-height', window_height);
				ams.root.css('min-height', window_height);
			}
		},

		/**
		 * Check width for mobile devices
		 */
		_checkMobileWidth: function() {
			if ($(window).width() < 979)
				ams.root.addClass('mobile-view-activated')
			else if (ams.root.hasClass('mobile-view-activated'))
				ams.root.removeClass('mobile-view-activated');
		},

		/**
		 * Show/hide shortcut buttons
		 */
		_showShortcutButtons: function() {
			ams.shortcuts.animate({
				height: 'show'
			}, 200, 'easeOutCirc');
			ams.root.addClass('shortcut-on');
		},
		
		_hideShortcutButtons: function() {
			ams.shortcuts.animate({
				height: 'hide'
			}, 300, 'easeOutCirc');
			ams.root.removeClass('shortcut-on');
		},

		/**
		 * Check notification badge
		 */
		checkNotification: function() {
			$this = $('#activity > .badge');
			if (parseInt($this.text()) > 0)
				$this.removeClass("hidden")
					 .addClass("bg-color-red bounceIn animated");
			else
				$this.addClass("hidden")
					 .removeClass("bg-color-red bounceIn animated");
		},

		/**
		 * Initialize desktop and mobile widgets
		 */
		_initDesktopWidgets: function(element) {
			if (ams.enable_widgets) {
				var widgets = $('.ams-widget', element);
				if (widgets.length > 0)
					ams.ajax.check($.fn.MyAMSWidget,
								   ams.baseURL + 'myams-widgets' + (ams.devmode ? '.js' : '.min.js'),
								   function() {
										widgets.each(function() {
											var widget = $(this);
											var data = widget.data();
											var data_options = {
												deleteSettingsKey: '#deletesettingskey-options',
												deletePositionKey: '#deletepositionkey-options'
											};
											var settings = $.extend({}, data_options, data.amsWidgetOptions);
											settings = ams.executeFunctionByName(data.amsWidgetInitcallback, widget, settings) || settings;
											widget.MyAMSWidget(settings);
										});
										MyAMSWidget.initWidgetsGrid($('.ams-widget-grid', element));
									});
			}
		},

		_initMobileWidgets: function(element) {
			if (ams.enable_mobile && ams.enable_widgets)
				ams.skin._initDesktopWidgets(element);
		},

		/**
		 * Add an alert on top of a container
		 *
		 * @parent: parent container where the alert will be displayed
		 * @status: info, success, warning or danger
		 * @header: alert header
		 * @message: main alert message
		 * @subtitle: optional subtitle
		 * @margin: if true, a margin will be displayed around alert
		 */
		alert: function(parent, status, header, message, subtitle, margin) {
			$('.alert', parent).remove();
			if (status == 'error')
				status = 'danger';
			var content = '<div class="' + (margin ? 'margin-10' : '') + ' alert alert-block alert-' + status + ' fade in">' +
							'<a class="close" data-dismiss="alert"><i class="fa fa-check"></i></a>' +
							'<h4 class="alert-heading">' +
								'<i class="fa fa-fw fa-warning"></i> ' + header +
							'</h4>' +
							(subtitle ? ('<p>' + subtitle + '</p>') : '') +
							'<ul>';
			if (typeof(message) == 'string')
				content += '<li>' + message + '</li>';
			else {
				for (var index in message) {
					if (!$.isNumeric(index))  // IE check
						continue;
					content += '<li>' + message[index] + '</li>';
				};
			}
			content += '</ul></div>';
			var alert = $(content).prependTo(parent);
			if (parent.exists) {
				ams.ajax.check($.scrollTo,
							   ams.baseURL + 'ext/jquery-scrollTo.min.js',
							   function() {
									$.scrollTo(parent, {offset: {top: -50}});
							   });
			}
		},

		/**
		 * Big message box
		 */
		bigBox: function(options, callback) {
			ams.ajax.check(ams.notify,
						   ams.baseURL + 'myams-notify' + (ams.devmode ? '.js' : '.min.js'),
						   function() {
								ams.notify.messageBox(options, callback);
						   });
		},

		/**
		 * Medium notification message box, displayed on page's bottom right
		 */
		messageBox: function(status, options, callback) {
			if (typeof(status) == 'object') {
				callback = options;
				options = status || {};
				status = 'info';
			}
			ams.ajax.check(ams.notify,
						   ams.baseURL + 'myams-notify' + (ams.devmode ? '.js' : '.min.js'),
						   function() {
								switch (status) {
									case 'error':
									case 'danger':
										options.color = '#C46A69';
										break;
									case 'warning':
										options.color = '#C79121';
										break;
									case 'success':
										options.color = '#739E73';
										break;
									default:
										options.color = options.color || '#3276B1';
								}
								options.sound = false;
								ams.notify.bigBox(options, callback);
						   });
		},

		/**
		 * Small notification message box, displayed on page's top right
		 */
		smallBox: function(status, options, callback) {
			if (typeof(status) == 'object') {
				callback = options;
				options = status || {};
				status = 'info';
			}
			ams.ajax.check(ams.notify,
						   ams.baseURL + 'myams-notify' + (ams.devmode ? '.js' : '.min.js'),
						   function() {
								switch (status) {
									case 'error':
									case 'danger':
										options.color = '#C46A69';
										break;
									case 'warning':
										options.color = '#C79121';
										break;
									case 'success':
										options.color = '#739E73';
										break;
									default:
										options.color = options.color || '#3276B1';
								}
								options.sound = false;
								ams.notify.smallBox(options, callback);
						   });
		},

		/**
		 * Initialize breadcrumbs based on active menu position
		 */
		_drawBreadCrumb: function() {
			var crumb = $('#ribbon OL.breadcrumb');
			crumb.empty()
				 .append($('<li></li>').append($('<a></a>').text(ams.i18n.HOME)
				 										   .attr('href', $('nav a[href!="#"]:first').attr('href'))));
			$('nav LI.active >A').each(function() {
				var menu = $(this);
				var body = $.trim(menu.clone()
									  .children(".badge")
									  .remove()
									  .end()
									  .text());
				var item = $("<li></li>").append(menu.attr('href').replace(/^#/, '')
													? $("<a></a>").html(body)
																  .attr('href', menu.attr('href'))
													: body);
				crumb.append(item);
			});
		},

		/**
		 * Check URL matching current location hash
		 */
		checkURL: function() {

			function updateActiveMenus(menu) {
				$('nav .active').removeClass('active');
				menu.addClass('open')
					.addClass('active');
				menu.parents('li').addClass('open active')
								  .children('ul').addClass('active')
												 .show();
				menu.parents('li:first').removeClass('open');
				menu.parents('ul').addClass(menu.attr('href').replace(/^#/, '') ? 'active' : '')
								  .show();
			}

			var hash = location.hash;
			var url = hash.replace(/^#/, '');
			if (url) {
				var container = $('#content');
				if (!container.exists())
					container = $('body');
				var menu = $('nav A[href="' + hash + '"]');
				if (menu.exists())
					updateActiveMenus(menu);
				ams.skin.loadURL(url, container);
				document.title = $('[data-ams-page-title]:first', container).data('ams-page-title') ||
								 menu.attr('title') ||
								 document.title;
			} else {
				var active_url = $('[data-ams-active-menu]').data('ams-active-menu');
				if (active_url) {
					menu = $('nav A[href="' + active_url + '"]');
				} else {
					menu = $('nav >UL >LI >A[href!="#"]').first();
				}
				if (menu.exists()) {
					updateActiveMenus(menu);
					if (active_url)
						ams.skin._drawBreadCrumb();
					else
						window.location.hash = menu.attr('href');
				}
			}
		},

		/**
		 * Load given URL into container
		 */
		loadURL: function(url, container, options, callback) {
			if (url.startsWith('#')) {
				url = url.substr(1);
			}
			if (typeof(options) == 'function') {
				callback = options;
				options = {};
			}
			container = $(container);
			var defaults = {
				type: 'GET',
				url: url,
				dataType: 'html',
				cache: false,
				beforeSend: function() {
					container.html('<h1><i class="fa fa-cog fa-spin"></i> Loading... </h1>');
					if (container[0] == $('#content')[0]) {
						ams.skin._drawBreadCrumb();
						document.title = $('.breadcrumb LI:last-child').text();
						$('html, body').animate({scrollTop: 0}, 'fast');
					} else {
						container.animate({scrollTop: 0}, 'fast');
					}
				},
				success: function(data, status, request) {
					if (callback)
						ams.executeFunctionByName(callback, this, data, status, request, options);
					else {
						var request_data = ams.ajax.getResponse(request);
						var data_type = request_data.content_type;
						var result = request_data.data;
						switch (data_type) {
							case 'json':
								ams.ajax.handleJSON(result, container);
								break;
							case 'script':
								break;
							case 'xml':
								break;
							case 'html':
							case 'text':
							default:
								container.parents('.hidden').removeClass('hidden');
								$('.alert', container.parents('.alerts-container')).remove();
								container.css({opacity: '0.0'})
										 .html(data)
										 .delay(50)
										 .animate({opacity: '1.0'}, 300);
								ams.initContent(container);
						}
					}
				},
				error: function(request, options, error) {
					container.html('<h3 class="error"><i class="fa fa-warning txt-color-orangeDark"></i> ' +
								   ams.i18n.ERROR + error + '</h3>' +
								   request.responseText);
				},
				async: false
			};
			var settings = $.extend({}, defaults, options);
			$.ajax(settings);
		},

		/**
		 * Change user language
		 */
		setLanguage: function(options) {
			var lang = options.lang;
			var handler_type = options.handler_type || 'json';
			switch (handler_type) {
				case 'json':
					var method = options.method || 'setUserLanguage';
					ams.jsonrpc.post(method, {lang: lang}, function() {
						window.location.reload(true);
					});
					break;
				case 'ajax':
					var href = options.href || 'setUserLanguage';
					ams.ajax.post(href, {lang: lang}, function() {
						window.location.reload(true);
					});
					break;
			}
		},

		/**
		 * Go to logout page
		 */
		logout: function() {
			window.location = ams.loginURL;
		}
	};


	/**
	 * Main page initialization
	 * This code is called only once to register global events and callbacks
	 */
	MyAMS.initPage = function() {

		/* Init main components */
		ams.root = $('BODY');
		ams.left_panel = $('#left-panel');
		ams.shortcuts = $('#shortcut');

		// Init main AJAX events
		var jquery_xhr = $.ajaxSettings.xhr;
		$.ajaxSetup({
			progress: ams.ajax.progress,
			progressUpload: ams.ajax.progress,
			xhr: function() {
				var request = jquery_xhr();
				if (request && (typeof(request.addEventListener) == "function")) {
					var that = this;
					request.addEventListener("progress", function(evt) {
						that.progress(evt);
					}, false);
				}
				return request;
			}
		});
		$(document).ajaxError(ams.error.ajax);

		// Check mobile/desktop
		if (!ams.isMobile) {
			ams.root.addClass('desktop-detected');
			ams.device = 'desktop';
		} else {
			ams.root.addClass('mobile-detected');
			ams.device = 'mobile';
			if (ams.enable_fastclick) {
				ams.ajax.check($.fn.noClickDelay,
							   ams.baseURL + '/ext/jquery-smartclick' + (ams.devmode ? '.js' : '.min.js'),
							   function() {
								   $('NAV UL A').noClickDelay();
								   $('#hide-menu A').noClickDelay();
							   });
			}
		}

		// Hide menu button
		$('#hide-menu >:first-child > A').click(function(e) {
			$('BODY').toggleClass("hidden-menu");
			e.preventDefault();
		});

		// Switch shortcuts
		$('#show-shortcut').click(function(e) {
			if (ams.shortcuts.is(":visible")) {
				ams.skin._hideShortcutButtons();
			} else {
				ams.skin._showShortcutButtons();
			}
			e.preventDefault();
		});

		$(document).mouseup(function(e) {
			if (!ams.shortcuts.is(e.target)
				&& ams.shortcuts.has(e.target).length === 0) {
				ams.skin._hideShortcutButtons();
			}
		});

		// Show & hide mobile search field
		$('#search-mobile').click(function() {
			ams.root.addClass('search-mobile');
		});

		$('#cancel-search-js').click(function() {
			ams.root.removeClass('search-mobile');
		});

		// Activity badge
		$('#activity').click(function(e) {
			var activity = $(this);
			var dropdown = activity.next('.ajax-dropdown');
			if (!dropdown.is(':visible')) {
				dropdown.css('left', activity.position().left - dropdown.innerWidth() / 2 + activity.innerWidth() / 2)
						.fadeIn(150);
				activity.addClass('active');
			} else {
				dropdown.fadeOut(150);
				activity.removeClass('active')
			}
			e.preventDefault();
		});
		ams.skin.checkNotification();

		$(document).mouseup(function(e) {
			var dropdown = $('.ajax-dropdown');
			if (!dropdown.is(e.target) &&
				dropdown.has(e.target).length === 0) {
				dropdown.fadeOut(150)
						.prev().removeClass("active");
			}
		});

		$('input[name="activity"]').change(function() {
			var url = $(this).data('ams-url');
			container = $('.ajax-notifications');
			ams.skin.loadURL(url, container);
		});

		// Logout button
		$('#logout a').click(function(e) {
			e.preventDefault();
			e.stopPropagation();
			//get the link
			ams.loginURL = $(this).attr('href');
			// ask verification
			ams.skin.bigBox({
				title : "<i class='fa fa-sign-out txt-color-orangeDark'></i> " + ams.i18n.LOGOUT +
						" <span class='txt-color-orangeDark'><strong>" + $('#show-shortcut').text() + "</strong></span> ?",
				content : ams.i18n.LOGOUT_COMMENT,
				buttons : '['+ams.i18n.BTN_NO+']['+ams.i18n.BTN_YES+']'
			}, function(ButtonPressed) {
				if (ButtonPressed == ams.i18n.BTN_YES) {
					ams.root.addClass('animated fadeOutUp');
					setTimeout(ams.skin.logout, 1000)
				}
			});
		});

		// Initialize left nav
		$('NAV UL').myams_menu({
			accordion : true,
			speed : ams.menu_speed
		});

		// Left navigation collapser
		$('.minifyme').click(function(e) {
			$('BODY').toggleClass("minified");
			$(this).effect("highlight", {}, 500);
			e.preventDefault();
		});

		// Reset widgets
		$('#refresh').click(function(e) {
			ams.skin.bigBox({
				title: "<i class='fa fa-refresh' style='color: green'></i> " + ams.i18n.CLEAR_STORAGE_TITLE,
				content: ams.i18n.CLEAR_STORAGE_CONTENT,
				buttons: '['+ams.i18n.BTN_CANCEL+']['+ams.i18n.BTN_OK+']'
			}, function(buttonPressed) {
				if (buttonPressed == ams.i18n.BTN_OK && localStorage) {
					localStorage.clear();
					location.reload();
				}
			});
			e.preventDefault();
		});

		// Check active pop-overs
		$('BODY').on('click', function(e) {
			var element = $(this);
			if (!element.is(e.target) &&
				element.has(e.target).length === 0 &&
				$('.popover').has(e.target).length === 0)
				element.popover('hide');
		});

		// Resize events
		ams.ajax.check($.resize,
					   ams.baseURL + 'ext/jquery-resize' + (ams.devmode ? '.js' : '.min.js'),
					   function() {
						   $('#main').resize(function() {
							   ams.skin._setPageHeight();
							   ams.skin._checkMobileWidth();
						   });
						   $('nav').resize(function() {
							   ams.skin._setPageHeight();
						   });
					   });

		// Init AJAX navigation
		if (ams.ajax_nav) {
			if ($('nav').length > 0)
				ams.skin.checkURL();
			$(document).on('click', 'a[href="#"]', function(e) {
				e.preventDefault();
			});
			$(document).on('click', 'a[href!="#"]:not([data-toggle]), [data-ams-url]:not([data-toggle])', function(e) {
				var link = $(e.currentTarget);
				var href = link.attr('href') || link.data('ams-url');
				if (!href || href.startsWith('javascript:') || link.attr('target'))
					return;
				e.preventDefault();
				var href_getter = ams.getFunctionByName(href);
				if (typeof(href_getter) == 'function') {
					href = href_getter.call(link);
				}
				var target = link.data('ams-target');
				if (target) {
					ams.form.confirmChangedForm(target, function() {
						ams.skin.loadURL(href, target, link.data('ams-link-options'), link.data('ams-link-callback'));
					});
				} else {
					ams.form.confirmChangedForm(function() {
						if (href.startsWith('#')) {
							if (href != location.hash) {
								if (ams.root.hasClass('mobile-view-activated')) {
									ams.root.removeClass('hidden-menu');
									window.setTimeout(function () {
										window.location.hash = href;
									}, 150);
								} else
									window.location.hash = href;
							}
						} else
							window.location = href;
					});
				}
			});
			$(document).on('click', 'a[target="_blank"]', function(e) {
				e.preventDefault();
				window.open($(e.currentTarget).attr('href'));
			});
			$(document).on('click', 'a[target="_top"]', function(e) {
				e.preventDefault();
				ams.form.confirmChangedForm(function() {
					window.location = $(e.currentTarget).attr('href');
				});
			});

			// Check URL when hash changed
			$(window).on('hashchange', ams.skin.checkURL);
		}

		// Initialize modal dialogs links
		$(document).off('click.modal')
				   .on('click', '[data-toggle="modal"]', function(e) {
			e.preventDefault();
			var source = $(this);
			ams.dialog.open(source);
			if (source.parents('#shortcut').exists())
				setTimeout(ams.skin._hideShortcutButtons, 300);
		});
		$(document).on('shown.bs.modal', ams.dialog.shown);

		// Initialize form buttons
		$(document).on('click', 'button[type="submit"], button.submit', function() {
			var button = $(this);
			$(button.get(0).form).data('ams-submit-button', button);
		});

		// Initialize custom click handlers
		$(document).on('click', '[data-ams-click-handler]', function(e) {
			var source = $(this);
			var data = source.data();
			if (data.amsClickHandler) {
				if (data.amsClickStopPropagation === true)
					e.stopPropagation();
				if (data.amsClickKeepDefault !== true)
					e.preventDefault();
				var callback = ams.getFunctionByName(data.amsClickHandler);
				if (callback !== undefined)
					callback.call(source, data.amsClickHandlerOptions);
			}
		});

		// Initialize custom change handlers
		$(document).on('change', '[data-ams-change-handler]', function(e) {
			var source = $(this);
			var data = source.data();
			if (data.amsChangeHandler) {
				if (data.amsChangeKeepDefault !== true)
					e.preventDefault();
				var callback = ams.getFunctionByName(data.amsChangeHandler);
				if (callback !== undefined)
					callback.call(source, data.amsChangeHandlerOptions);
			}
		});

		// Initialize custom reset handlers
		$(document).on('reset', '[data-ams-reset-handler]', function(e) {
			var form = $(this);
			var data = form.data();
			if (data.amsResetHandler) {
				if (data.amsResetKeepDefault !== true)
					e.preventDefault();
				var callback = ams.getFunctionByName(data.amsResetHandler);
				if (callback !== undefined)
					callback.call(form, data.amsResetHandlerOptions);
			}
		});

		// Handle update on file upload placeholder
		$(document).on('change', 'input[type="file"]', function(e) {
			e.preventDefault();
			var input = $(this);
			var button = input.parent('.button');
			if (button.exists() && button.parent().hasClass('input-file')) {
				button.next('input[type="text"]').val(input.val());
			}
		});

		// Disable clicks on disabled tabs
		$("a[data-toggle=tab]", ".nav-tabs").on("click", function(e) {
			if ($(this).parent('li').hasClass("disabled")) {
				e.preventDefault();
				return false;
			}
		});

		// Enable tabs dynamic loading
		$(document).on('show.bs.tab', function(e) {
			var link = $(e.target);
			var data = link.data();
			if (data.amsUrl) {
				if (data.amsTabLoaded)
					return;
				ams.skin.loadURL(data.amsUrl, link.attr('href'));
				if (data.amsTabLoadOnce)
					link.data('ams-tab-loaded', true);
			}
		});

		// Init plug-ins required by main layout
		ams.plugins.enabled.hint(document);

		// Init content when not loaded by AJAX request
		// or when redirecting to authentication page...
		if ((window.location.hash == '') || (ams.getQueryVar(window.location.href, 'came_from') != false))
			ams.initContent(document);

		// Add unload event listener to check for modified forms
		$(window).on('beforeunload', ams.form.checkBeforeUnload);

	};


	/**
	 * Main content plug-ins initializer
	 * This code is called to initialize plugins, callbacks and events listeners each time an HTML content
	 * is loaded dynamically from remote server.
	 */
	MyAMS.initContent = function(element) {

		// Remove left tips
		$('.tipsy').remove();

		// Activate tooltips and popovers
		$("[rel=tooltip]", element).tooltip();
		$("[rel=popover]", element).popover();

		// Activate popovers with hover states
		$("[rel=popover-hover]", element).popover({
			trigger : "hover"
		});

		// Init registered plug-ins and callbacks
		ams.plugins.init(element);
		ams.callbacks.init(element);
		ams.events.init(element);
		ams.form.init(element);

		// Initialize widgets
		if (ams.device === 'desktop')
			ams.skin._initDesktopWidgets(element);
		else
			ams.skin._initMobileWidgets(element);
		ams.skin._setPageHeight();

	};


	/**
	 * MyAMS locale strings
	 */
	MyAMS.i18n = {

		INFO: "Information",
		WARNING: "!! WARNING !!",
		ERROR: "ERROR: ",

		WAIT: "Please wait!",
		FORM_SUBMITTED: "This form was already submitted...",
		NO_SERVER_RESPONSE: "No response from server!",
		ERROR_OCCURED: "An error occured!",
		ERRORS_OCCURED: "Some errors occured!",

		BAD_LOGIN_TITLE: "Bad login!",
		BAD_LOGIN_MESSAGE: "Your anthentication credentials didn't allow you to open a session; " +
						   "please check your credentials or contact administrator.",

		CONFIRM: "Confirm",
		CONFIRM_REMOVE: "Removing this content can't be undone. Do you confirm?",

		CLEAR_STORAGE_TITLE: "Clear Local Storage",
		CLEAR_STORAGE_CONTENT: "Would you like to RESET all your saved widgets and clear LocalStorage?",

		BTN_OK: "OK",
		BTN_CANCEL: "Cancel",
		BTN_YES: "Yes",
		BTN_NO: "No",
		BTN_OK_CANCEL: "[OK][Cancel]",

		FORM_CHANGED_WARNING: "Some changes were not saved. These updates will be lost if you leave this page.",
		NO_UPDATE: "No changes were applied.",
		DATA_UPDATED: "Data successfully updated.",

		HOME: "Home",
		LOGOUT: "Logout?",
		LOGOUT_COMMENT: "You can improve your security further after logging out by closing this opened browser",

		SELECT2_PLURAL: 's',
		SELECT2_NOMATCHES: "No matches found",
		SELECT2_SEARCHING: "Searching...",
		SELECT2_LOADMORE: "Loading more results...",
		SELECT2_INPUT_TOOSHORT: "Please enter {0} more character{1}",
		SELECT2_INPUT_TOOLONG: "Please delete {0} character{1}",
		SELECT2_SELECTION_TOOBIG: "You can only select {0} item{1}",
		SELECT2_FREETAG_PREFIX: "Free text: ",

		DT_COLUMNS: "Columns"

	};


	$(document).ready(function() {
		$ = jQuery.noConflict();
		var lang = $('HTML').attr('lang') || $('HTML').attr('xml:lang');
		if (lang && !lang.startsWith('en'))
			MyAMS.getScript(MyAMS.baseURL + 'i18n/myams_' + lang.substr(0,2) + '.js', function() {
				MyAMS.initPage();
			});
		else {
			MyAMS.initPage();
		}
	});

})(jQuery);
