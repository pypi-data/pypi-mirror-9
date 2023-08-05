/*
 * jQuery Progress Bar plugin
 * Version 2.0 (06/22/2009)
 * @requires jQuery v1.2.1 or later
 *
 * Copyright (c) 2008 Gary Teo
 * http://t.wits.sg

 USAGE:
 $(".someclass").progressBar();
 $("#progressbar").progressBar();
 $("#progressbar").progressBar(45);							// percentage
 $("#progressbar").progressBar({showText: false });			// percentage with config
 $("#progressbar").progressBar(45, {showText: false });		// percentage with config
 */
(function ($) {

	$.extend({

				 progressBar: new function () {

					 this.defaults = {
						 steps: 20,											// steps taken to reach target
						 step_duration: 20,
						 max: 100,											// Upon 100% i'd assume, but configurable
						 showText: true,											// show text with percentage in next to the progressbar? - default : true
						 textFormat: 'percentage',									// Or otherwise, set to 'fraction'
						 width: 120,											// Width of the progressbar - don't forget to adjust your image too!!!												// Image to use in the progressbar. Can be a single image too: 'images/progressbg_green.gif'
						 height: 12,											// Height of the progressbar - don't forget to adjust your image too!!!
						 callback: null,											// Calls back with the config object that has the current percentage, target percentage, current image, etc
						 boxImage: '/--static--/ztfy.jqueryui/img/progressbar.gif',						// boxImage : image around the progress bar
						 barImage: {
							 0: '/--static--/ztfy.jqueryui/img/progressbg_red.gif',
							 30: '/--static--/ztfy.jqueryui/img/progressbg_orange.gif',
							 70: '/--static--/ztfy.jqueryui/img/progressbg_green.gif'
						 },
						 // Internal use
						 running_value: 0,
						 value: 0,
						 image: null
					 };

					 /* public methods */
					 this.construct = function (arg1, arg2) {
						 var argvalue = null;
						 var argconfig = null;

						 if (arg1 != null) {
							 if (!isNaN(arg1)) {
								 argvalue = arg1;
								 if (arg2 != null) {
									 argconfig = arg2;
								 }
							 } else {
								 argconfig = arg1;
							 }
						 }

						 return this.each(function (child) {
							 var pb = this;
							 var config = this.config;

							 if (argvalue != null && this.bar != null && this.config != null) {
								 this.config.value = argvalue
								 if (argconfig != null)
									 pb.config = $.extend(this.config, argconfig);
								 config = pb.config;
							 } else {
								 var $this = $(this);
								 var config = $.extend({}, $.progressBar.defaults, argconfig);
								 config.id = $this.attr('id') ? $this.attr('id') : Math.ceil(Math.random() * 100000);	// random id, if none provided

								 if (argvalue == null)
									 argvalue = $this.html().replace("%", "")	// parse percentage

								 config.value = argvalue;
								 config.running_value = 0;
								 config.image = getBarImage(config);

								 $this.html("");
								 var bar = document.createElement('img');
								 var text = document.createElement('span');
								 var $bar = $(bar);
								 var $text = $(text);
								 pb.bar = $bar;

								 $bar.attr('id', config.id + "_pbImage");
								 $text.attr('id', config.id + "_pbText");
								 $text.html(getText(config));
								 $bar.attr('title', getText(config));
								 $bar.attr('alt', getText(config));
								 $bar.attr('src', config.boxImage);
								 $bar.attr('width', config.width);
								 $bar.css("width", config.width + "px");
								 $bar.css("height", config.height + "px");
								 $bar.css("background-image", "url(" + config.image + ")");
								 $bar.css("background-position", ((config.width * -1)) + 'px 50%');
								 $bar.css("padding", "0");
								 $bar.css("margin", "0");
								 $this.append($bar);
								 $this.append($text);
							 }

							 function getPercentage(config) {
								 return config.running_value * 100 / config.max;
							 }

							 function getBarImage(config) {
								 var image = config.barImage;
								 if (typeof(config.barImage) == 'object') {
									 for (var i in config.barImage) {
										 if (getPercentage(config) >= parseInt(i)) {
											 image = config.barImage[i];
										 } else {
											 break;
										 }
									 }
								 }
								 return image;
							 }

							 function getText(config) {
								 if (config.showText) {
									 if (config.textFormat == 'percentage') {
										 return " " + Math.round(config.running_value) + "%";
									 } else if (config.textFormat == 'fraction') {
										 return " " + config.running_value + '/' + config.max;
									 }
								 }
							 }

							 config.increment = Math.round((config.value - config.running_value) / config.steps);
							 if (config.increment < 0)
								 config.increment *= -1;
							 if (config.increment < 1)
								 config.increment = 1;

							 var t = setInterval(function () {
								 var pixels = config.width / 100;			// Define how many pixels go into 1%
								 var stop = false;

								 if (config.running_value > config.value) {
									 if (config.running_value - config.increment < config.value) {
										 config.running_value = config.value;
									 } else {
										 config.running_value -= config.increment;
									 }
								 }
								 else if (config.running_value < config.value) {
									 if (config.running_value + config.increment > config.value) {
										 config.running_value = config.value;
									 } else {
										 config.running_value += config.increment;
									 }
								 }

								 if (config.running_value == config.value)
									 clearInterval(t);

								 var $bar = $("#" + config.id + "_pbImage");
								 var $text = $("#" + config.id + "_pbText");
								 var image = getBarImage(config);
								 if (image != config.image) {
									 $bar.css("background-image", "url(" + image + ")");
									 config.image = image;
								 }
								 $bar.css("background-position", (((config.width * -1)) + (getPercentage(config) * pixels)) + 'px 50%');
								 $bar.attr('title', getText(config));
								 $text.html(getText(config));

								 if (config.callback != null && typeof(config.callback) == 'function')
									 config.callback(config);

								 pb.config = config;
							 }, config.step_duration);
						 });
					 };

					 this.submit = function (form) {
						 var files = $('input:file', form);
						 if (files.length > 0) {
							 var frame = $('iframe[name=progress]', form);
							 if (frame.length > 0) {
								 var uuid = "";
								 for (var i = 0; i < 32; i++) {
									 uuid += Math.floor(Math.random() * 16).toString(16);
								 }
								 var action = $(form).attr("action");
								 if (old_id = /X-Progress-ID=([^&]+)/.exec(action)) {
									 action = action.replace(old_id[1], uuid);
								 } else {
									 action = action + "?X-Progress-ID=" + uuid;
								 }
								 $(form).attr("action", action);
								 var progress = $(frame).get(0).contentWindow.updateUploadProgress;
								 if (progress) {
									 progress(uuid);
									 return uuid;
								 }
							 }
						 }
					 }
				 }
			 });

	$.fn.extend({
					progressBar: $.progressBar.construct
				});

})(jQuery);
