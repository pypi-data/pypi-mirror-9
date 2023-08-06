$(document).ready(function (e){
	var $browseBtn = $('#ImgerBrowseBTN');
	var w = $browseBtn.attr('data-width');
	var h = $browseBtn.attr('data-height');
	var t = $browseBtn.attr('data-mime');
	var q = $browseBtn.attr('data-quality');

	imger = new Imger({
		templateUrl: "/static/imger/templates/theme-standard.html"
	});

	$('#ImgerBrowseBTN').click(function(e){
		imger.open(
			{
				width: w,
				height: h,
				mime: t,
				quality: q,
				autoborwse: false,
				note: "Django-Imger",
				form: 'imger.imagename',
				autobrowse: true,
				dataurl: {
					complete: function (data) {
						data.form.meta = data.meta;
						$('#ImgerBrowseLabel').html(data.meta.name + ' as <b>' + data.form.imagename + '</b>');	
						var v = 'imgerDjango:'+JSON.stringify(data.form)+':imgerDjango:'+data.dataURL;
						$('#ImgerDataURL').val(v);
					}
				}
			}
		);
	});
});
