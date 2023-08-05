/*
 * MyAMS extensions to jquery-sparkline graphs plug-in
 * Version 0.1.0
 * ©2014 Thierry Florac <tflorac@ulthar.net>
 */
(function($) {

	MyAMS.graphs = {

		init: function(graphs) {
			MyAMS.ajax.check($.fn.sparkline,
							   MyAMS.baseURL + 'ext/jquery-sparkline-2.1.1.min.js',
							   function(first_load) {
									graphs.each(function() {
										var graph = $(this);
										var graph_data  =graph.data();
										var sparklineType = graph_data.sparklineType || 'bar';
										switch (sparklineType) {
											case 'bar':
												graph.sparkline('html', {
													type: 'bar',
													barColor: graph_data.sparklineBarColor || graph.css('color') || '#0000f0',
													height: graph_data.sparklineHeight || '26px',
													barWidth: graph_data.sparklineBarwidth || 5,
													barSpacing: graph_data.sparklineBarspacing || 2,
													stackedBarColor: graph.data.sparklineBarstackedColor || ["#A90329", "#0099c6", "#98AA56", "#da532c", "#4490B1", "#6E9461", "#990099", "#B4CAD3"],
													negBarColor: graph.data.sparklineNegbarColor || '#A90329',
													zeroAxis: 'false'
												});
												break;

											case 'line':
												graph.sparkline('html', {
													type: 'line',
													width: graph_data.sparklineWidth || '90px',
													height: graph_data.sparklineHeight || '20px',
													lineWidth: graph_data.sparklineLineWidth || 1,
													lineColor: graph_data.sparklineLineColor || graph.css('color') || '#0000f0',
													fillColor: graph_data.fillColor || '#c0d0f0',
													spotColor: graph_data.sparklineSpotColor || '#f08000',
													minSpotColor: graph_data.sparklineMinspotColor || '#ed1c24',
													maxSpotColor: graph_data.sparklineMaxspotColor || '#f08000',
													highlightSpotColor: graph_data.sparklineHighlightspotColor || '#50f050',
													highlightLineColor: graph_data.sparklineHighlightlineColor || 'f02020',
													spotRadius: graph_data.sparklineSpotradius || 1.5,
													chartRangeMin: graph_data.sparklineMinY || 'undefined',
													chartRangeMax: graph_data.sparklineMaxY || 'undefined',
													chartRangeMinX: graph_data.sparklineMinX || 'undefined',
													chartRangeMaxX: graph_data.sparklineMaxX || 'undefined',
													normalRangeMin: graph_data.minVal || 'undefined',
													normalRangeMax: graph_data.maxVal || 'undefined',
													normalRangeColor: graph_data.normColor || '#c0c0c0',
													drawNormalOnTop: graph_data.drawNormal || false
												});
												break;

											case 'pie':
												graph.sparkline('html', {
													type: 'pie',
													width : graph_data.sparklinePiesize || 90,
													height : graph_data.sparklinePiesize || 90,
													tooltipFormat : '<span style="color: {{color}}">&#9679;</span> ({{percent.1}}%)',
													sliceColors : graph_data.sparklinePiecolor || ["#B4CAD3", "#4490B1", "#98AA56", "#da532c", "#6E9461", "#0099c6", "#990099", "#717D8A"],
													offset : 0,
													borderWidth : 1,
													offset : graph_data.sparklineOffset || 0,
													borderColor : graph_data.borderColor || '#45494C'
												});
												break;

											case 'box':
												graph.sparkline('html', {
													type : 'box',
													width : graph_data.sparklineWidth || 'auto',
													height : graph_data.sparklineHeight || 'auto',
													raw : graph_data.sparklineBoxraw || false,
													target : graph_data.sparklineTargetval || 'undefined',
													minValue : graph_data.sparklineMin || 'undefined',
													maxValue : graph_data.sparklineMax || 'undefined',
													showOutliers : graph_data.sparklineShowoutlier || true,
													outlierIQR : graph_data.sparklineOutlierIqr || 1.5,
													spotRadius : graph_data.sparklineSpotradius || 1.5,
													boxLineColor : graph.css('color') || '#000000',
													boxFillColor : graph_data.fillColor || '#c0d0f0',
													whiskerColor : graph_data.sparklineWhisColor || '#000000',
													outlierLineColor : graph_data.sparklineOutlineColor || '#303030',
													outlierFillColor : graph_data.sparklineOutlinefillColor || '#f0f0f0',
													medianColor : graph_data.sparklineOutlinemedianColor || '#f00000',
													targetColor : graph_data.sparklineOutlinetargetColor || '#40a020'
												});
												break;

											case 'bullet':
												graph.sparkline('html', {
													type : 'bullet',
													height : graph_data.sparklineHeight || 'auto',
													targetWidth : graph_data.sparklineWidth || 2,
													targetColor : graph_data.sparklineBullet-color || '#ed1c24',
													performanceColor : graph_data.sparklinePerformanceColor || '#3030f0',
													rangeColors : graph_data.sparklineBulletrangeColor || ["#d3dafe", "#a8b6ff", "#7f94ff"]
												});
												break;

											case 'discrete':
												graph.sparkline('html', {
													type : 'discrete',
													width : graph_data.sparklineWidth || 50,
													height : graph_data.sparklineHeight || 26,
													lineColor : graph.css('color'),
													lineHeight : graph_data.sparklineLineHeight || 5,
													thresholdValue : graph_data.sparklineThreshold || 'undefined',
													thresholdColor : graph_data.sparklineThresholdColor || '#ed1c24'
												});
												break;

											case 'tristate':
												graph.sparkline('html', {
													type : 'tristate',
													height : graph_data.sparklineHeight || 26,
													posBarColor : graph_data.sparklinePosbarColor || '#60f060',
													negBarColor : graph_data.sparklineNegbarColor || '#f04040',
													zeroBarColor : graph_data.sparklineZerobarColor || '#909090',
													barWidth : graph_data.sparklineBarwidth || 5,
													barSpacing : graph_data.sparklineBarspacing || 2,
													zeroAxis : graph_data.sparklineZeroaxis || false
												});
												break;

											case 'compositebar':
												$this.sparkline(graph_data.sparklineBarVal, {
													type : 'bar',
													width : graph_data.sparklineWidth || '100%',
													height : graph_data.sparklineHeight || '20px',
													barColor : graph_data.sparklineColorBottom || '#333333',
													barWidth : graph_data.sparklineBarwidth || 3
												});
												$this.sparkline(graph_data.sparklineLineVal, {
													width : graph_data.sparklineWidth || '100%',
													height : graph_data.sparklineHeight || '20px',
													lineColor : graph_data.sparklineColorTop || '#ed1c24',
													lineWidth : graph_data.sparklineLineWidth || 1,
													composite : true,
													fillColor : false
												});
												break;

											case 'compositeline':
												$this.sparkline(graph_data.sparklineBarVal, {
													type : 'line',
													spotRadius : graph_data.sparklineSpotradiusTop || 1.5,
													spotColor : graph_data.sparklineSpotColor || '#f08000',
													minSpotColor : graph_data.sparklineMinspotColorTop || '#ed1c24',
													maxSpotColor : graph_data.sparkline-maxspotColorTop || '#f08000',
													highlightSpotColor : graph_data.sparklineHighlightspotColorTop || '#50f050',
													highlightLineColor : graph_data.sparklineHighlightlineColorTop || '#f02020',
													valueSpots : graph_data.sparklineBarValSpotsTop || null,
													lineWidth : graph_data.sparklineLineWidthTop || 1,
													width : graph_data.sparklineWidth || '90px',
													height : graph_data.sparklineHeight || '20px',
													lineColor : graph_data.sparklineColorTop || '#333333',
													fillColor : graph_data.sparklineFillcolorTop || 'transparent'
												});
												$this.sparkline(graph_data.sparklineLineVal, {
													type : 'line',
													spotRadius : graph_data.sparklineSpotradiusBottom || graph_data.sparklineSpotradiusTop || 1.5,
													spotColor : graph_data.sparklineSpotColor || '#f08000',
													minSpotColor : graph_data.sparklineMinspotColorBottom || graph_data.sparklineMinspotColorTop || '#ed1c24',
													maxSpotColor : graph_data.sparklineMaxspotColorBottom || graph_data.sparklineMaxspotColorTop || '#f08000',
													highlightSpotColor : graph_data.sparklineHighlightspotColorBottom || graph_data.sparklineHighlightspotColorTop || '#50f050',
													highlightLineColor : graph_data.sparklineHighlightlineColorBottom || graph_data.sparklineHighlightlineColorTop || '#f02020',
													valueSpots : graph_data.sparklineBarValSpotsBottom || null,
													lineWidth : graph_data.sparklineLineWidthBottom || 1,
													width : graph_data.sparklineWidth || '90px',
													height : graph_data.sparklineHeight || '20px',
													lineColor : graph_data.sparklineColorBottom || '#ed1c24',
													composite : true,
													fillColor : graph_data.sparklineFillcolorBottom || 'transparent'
												});
												break;
										}
									});
							   });
		}
	}

})(jQuery);
