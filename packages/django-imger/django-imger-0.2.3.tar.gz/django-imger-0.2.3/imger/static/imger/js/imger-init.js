$(document).ready(function (e) {
	var target = null;

	var $browseBtn = $('.ImgerBrowseBTN');
	var static_url = $browseBtn.attr('data-static_url');

	var completeHandler = function(data) {
		if(data.form === null) data.form = {}

		data.form.meta = data.meta;

		var new_name = ''
		
		if(typeof data.form.imagename !== 'undefined')
			new_name = ' as <b>' + data.form.imagename + '</b>'

		target
			.find('.ImgerBrowseLabel')
				.html(data.meta.name + new_name);

		var v = 'imgerDjango:'+JSON.stringify(data.form)+':imgerDjango:'+data.dataURL;

		target
			.find('.ImgerDataURL')
				.val(v);
	}

	imger = new Imger({
		templateUrl: static_url + "imger/templates/theme-standard.html"
	});

	$('.ImgerBrowseBTN').click(function(e) {
		target = $(this).parent();

		var user_settings = $(this).attr('data-imger');
		user_settings = JSON.parse(user_settings);

		var settings = {
			width: 300,
			height: 200,
			mime: 'image/jpeg',
			quality: 100,
			autobrowse: true,
			note: "",
			form: 'imger.imagename',
		}

		settings = $.extend(settings, user_settings);

		settings.dataurl = {complete: completeHandler};

		imger.open(settings);
	});
});
