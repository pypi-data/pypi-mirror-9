// JavaScript Document
(function (window, document) {

function Imger(options) {
	var settings = {
		templateUrl: "templates/theme-standard.html"
	}

	$.extend(settings, options);

	var $document = $(document),
		$body = $('body'),
		$imgerWR = $('<div />').addClass('imger-wr'),
		$fileSelector = $('<input type="file" />'),

		extentionTypes = [], // build dynamically from mimeTypes on initSetup
		mimeTypes = ['image/jpeg', 'image/png'],
		mimeDefault = 'image/jpeg',
		mime = 'image/jpeg',
		extention = 'jpg',

		$imgerBrowselBTN =
		$imgerCancelBTN =
		$imgerDoneBTN =
		$imgerCanvas =
		$imgerImageInfo =
		$imgerDisplay =
		$imgerForm =
		$imgerFromWR =
		$getURL =
		$imgerFormSbmtBTN =
		$imgerFormCancelBTN =
		$imgerFormNote =
		$imgerToolbarToolsWR =
		file =
		imagedata =
		image =
		freader =
		placements =
		staticAnchor =
		cornerRect = 
		translatePos =
		imgerContext =
		upload =
		dataurl =
		resampler =
		form =
		imageDataToUpload =
		doneTarget = null,

		// moved into the resamplers{} object
		//imgerCompress = new ImgerCompress(),

		_ready =
		is_setup =
		blob = false,

		defaultWidth = 300,
		defaultHeight = 200,
		typeDefaults = {
			"upload": {
				doneLabel: "Upload"
			},
			"dataurl": {
				doneLabel: "Done"
			}
		},
		forms = {},
		validators = {},
		resamplers = {},
		history = [],
		historyredo = [],
		startDragOffset = {},

		w =
		h =
		quality =
		imgW =
		imgH =
		scale =
		minScale =
		centerX =
	    centerY = 
	    limitX = 
	    limitY = 0;

	$imgerWR.load(settings.templateUrl, function( response, status, xhr ) {
		if(status == "error") {
			console.log( msg + xhr.status + " " + xhr.statusText );
			return;
		}

		_ready = true;

	});

	var initSetup = function(t) {
		if(is_setup) return;

		$imgerBrowselBTN = $('.imger-btn-browse');
		$imgerCancelBTN = $('.imger-btn-cancel');
		$imgerDoneBTN = $('.imger-btn-done');
		$imgerScaler = $('.imger-scaler');
		$imgerCanvas = $('.imger-canvas');
		$imgerDisplay = $('.imger-display');
		$imgerImageInfo = $('.imger-image-info');
		$imgerForm = $('.imger-form');
		$imgerFromWR = $('.imger-form-wr');
		$imgerFormSbmtBTN = $('.imger-form-sbmt-btn');
		$imgerFormCancelBTN = $('.imger-form-cancel-btn');
		$imgerFormNote = $('.imger-form-note');
		$getURL = $('.get-URL');
		$imgerToolbarToolsWR = $('.imger-toolbar-tools-wr');

		imgerContext = $imgerCanvas[0].getContext('2d');

		image = new Image();
		//image.crossOrigin = "Anonymous"; // CORS support

		freader = new FileReader();

		validators = {
			anyregex: function(v, r) {
				return v.match(r);
			},
			imger: {
				filename: function(v) {
					var _v = v.replace(/[^a-z0-9\-]/gi, '');
					return (_v.length > 0);
				},
				email: function(v) {

				},
				hasvalue: function(v) {
					return (v.length > 0);
				}
			}
		}

		mimeLength = mimeTypes.length;

		for(var i = 0; i < mimeLength; i++) {
			extentionTypes.push( mimeTypes[i].split('/').pop() );	
		}

		forms = {
			imger: {
				imagename: {
					compiled: false,
					note: "Please provide a name for your image.",
					fields: [
						{
							type: "text",
							validate: 'imger.filename',
							placeholder: "Image name",
							name: "imagename",
							required: true,
							addon: function() { //Can be string or function that returns a string
								return '.' + extention;
							},
							process: function(v) {
								var _v = $.trim(v);
								_v = _v.replace(/\ /g, '-');
								_v = _v.replace(/[^a-z0-9\-]/gi, '');
								_v = _v.toLowerCase();
								return _v + '.' + extention;
							}
						}
					]
				}
			}
		}

		resamplers = {
			imger: {
				default: new ImgerCompress()
			}
		}

		$imgerScaler.noUiSlider({
			start: 0,
			connect: "lower",
			orientation: "horizontal",
			range: {
				'min': 0,
				'max': 100
			}
		});

		is_setup = true;
	}

	var imageLoaded = function(e) {
		imgW = image.width;
		imgH = image.height;

		setPlacements(true);

		//reset the slacer :: this initiates onScalerSet
		$imgerScaler.val(0);

		setHistory('scale');
	}

	var selectFile = function(e) {
		file = $fileSelector[0].files[0];

		if(file.type.indexOf('image') == -1) {
			alert("Image file not recognised");
			return;
		}

		freader.onload = function(e) {
			//keeping imagedata variable incase its more useful with the resampeling algo
			// if not then we can just: image.src = e.target.result;
			imagedata = e.target.result;
			image.src = imagedata;

			image.onload = imageLoaded;

			// I think this needs to move to the onScalerSet method
			// Thats where all the funky image quality stuff happens
			//@martin imgerCompress.load( image, $imgerCanvas.attr('id') );
		}

        freader.readAsDataURL(file);

		$imgerImageInfo.text(file.name);
	}

	var initBrowse = function(e) {
		$fileSelector.click();
	}

	var initURLGet = function(e) {
		var url = $('#getURLInput').val();
		image.src = url;

		image.onload = imageLoaded;
	}

	var uploadHandler = function(data) {

		var uploadData = {
			"image": imageDataToUpload,
			"name": file.name,
			"form": data
		}

		var headers = {
			"Access-Control-Request-Headers": "x-requested-with"
		}

		if(key_or_xyz('headers', upload, false)) {
			$.extend(headers, upload.headers);
		}

		$.ajax({
			url: upload.url,
			type: 'POST',
			data: uploadData,
		    headers: headers,
		    crossDomain: true,
	    	dataType: 'json',
		    success: function (data, status, xhr) {
				console.info(data);
				if(key_or_xyz('complete', upload, false)) {
					upload.complete(data);
				}
		    },
			error: function(err) {
				console.info(err);
			}
		});
	}

	var initForm = function() {
		if(!form.compiled) {
			var $compiledform = $('<form />');

			var fields  = form.fields;
			var length = fields.length;

			for(var i = 0; i < length; i++) {
				var field = fields[i];

				var addon = key_or_xyz('addon', field, null);
				var addonValue = '';

				if(addon != null) {
					if(typeof addon === 'function') addon = addon();
					addonValue = '<span class="input-group-addon">'+addon.toString()+'</span>';
				}

				var s = '';

				if(['text', 'email', 'number'].indexOf(field.type) != -1){
					s += '<div class="input-group"><input class="form-control" type="'+field.type+'" ';
					s += 'name="'+field.name+'" ';
					s += 'placeholder="'+field.placeholder+'" ';
					s += key_or_xyz('required', field, '');
					s += '/>'+addonValue+'</div>';
				}

				if(['radiogroup', 'checkgroup'].indexOf(field.type) != -1) {
					var list = field.list;
					var listlength = list.length;

					var type = 'radio';

					if(field.type === 'checkgroup') type = "checkbox";

					s += '<div class="input-box"><div class="input-group"><div>'+key_or_xyz('note', field, '')+'</div>';

					for(var j = 0; j < listlength; j++) {
						var item = list[j];

						s += '<div class="radio"><label><input type="'+type+'" value="'+item.value+'" name="'+field.name+'">'+item.label+'</label></div>';
					}

					s += '</div></div>';
				}

				if(field.type === 'textarea') {
					s += '<div class="input-group"><textarea class="form-control" name="'+field.name+'" placeholder="'+field.placeholder+'"></textarea></div>';
				}

				if(field.type === 'select') {
					s += '<select name="'+field.name+'"><option value="" disabled selected>'+field.placeholder+'</option>';

					var options = field.options;
					var optionslength = options.length;

					for(var j = 0; j < optionslength; j++) {
						var item = options[j];

						s += '<option value="'+item.value+'">'+item.label+'</option>';
					}

					s += '</select>';
				}

				$compiledform.append($(s));
			}

			form.compiled = $compiledform;
		}

		//display form

		$imgerFormNote.text(key_or_xyz('note', form, ''));

		$imgerFromWR
			.empty()
			.append(form.compiled);

		$imgerToolbarToolsWR.css('display', 'none');
		$imgerForm.css('display', 'block');
	}

	var submitForm = function(e) {
		var formData = form2js($imgerForm[0]);

		var errors = formErrors(formData);
		if(errors.length) {
			formErrorHandler(errors);
			return;
		}

		processForm(formData);

		completeHandler(formData);
		
	}

	var processForm = function(formData) {
		var fields = form.fields;
		var length = fields.length;

		for(var i = 0; i < length; i++) {
			var field = fields[i];
			var process = key_or_xyz('process', field, false);

			if(process) {
				var valueObj = object_dot_path(formData, field.name, true);
				value = valueObj.obj[valueObj.key];
				value = process(value);
				valueObj.obj[valueObj.key] = value;
			}
		}
	}

	var formErrors = function(formData) {
		var errors = [];

		var fields = form.fields;
		var length = fields.length;

		for(var i = 0; i < length; i++) {
			var field = fields[i];
			var required = key_or_xyz('required', field, false);
			var value = object_dot_path(formData, field.name);

			if(typeof value === 'undefined') {
				value = '';
			}

			if(value == '' && required){
				errors.push({
					field: field.name,
					err: "Required but empty",
					placeholder: field.placeholder
				});
				continue;
			}

			//var validate = field.validate;

			if( (validate = key_or_xyz('validate', field, false)) ) {
				if(typeof validate == 'string') {
					validate = object_dot_path(validators, validate);
				}

				var validateResponse = validate(value);

				if(validateResponse === false || validateResponse === null) {
					errors.push({
						field: field.name,
						err: "Validation error.",
						placeholder: field.placeholder
					});
					continue;
				}
				else if(typeof validateResponse === 'object') {
					if( !key_or_xyz('valid', validateResponse, false) ) {
						errors.push({
							field: field.name,
							err: key_or_xyz('err', validateResponse, "Validation error."),
							placeholder: field.placeholder
						});
						continue;
					}
				}
			}
		}

		return errors;
	}

	var formErrorHandler = function(errors) {
		var s = "";
		var length = errors.length;

		for(var i = 0; i < length; i++) {
			s += errors[i].placeholder + ": " + errors[i].err + "\n\r";
		}

		alert(s);
	}

	var cancelForm = function(e, reset) {
		$imgerToolbarToolsWR.css('display', 'block');
		$imgerForm.css('display', 'none');

		if(reset) {
			$imgerForm
					.find('form')
					.each(function(i, e) {
						e.reset();
					});
		}
	}

	var doneHandler = function(e) {
		
		imageDataToUpload = $imgerCanvas[0].toDataURL(mime, quality);

		if(form != null) {
			initForm();
			return;
		}

		completeHandler(null);	
	}

	var completeHandler = function(formData) {
		if(doneTarget == 'upload') {
			uploadHandler(formData);
		}
		else {
			if(blob) {
				$imgerCanvas[0].toBlob(dataUrlCompleteHandler);
			}
			else {
				dataUrlCompleteHandler(null);
			}
		}

		function dataUrlCompleteHandler(blob) {
			dataurl.complete(
				{
					dataURL: imageDataToUpload,
					blob: blob,
					meta: getMeta(),
					form: formData
				}
			);
			$imgerCancelBTN.click();
		}
	}

	var getMeta = function() {
		return {
			name: file.name,
			ext: '.' + file.name.split('.').pop(),
			save_ext: '.' + extention
		}
	}

	var setPlacements = function(initial) {
		// initial setup (place new image placements at TL and smallest scale)
		if(initial) {
			//minScale and initial scale are the same
			minScale = scale = Math.max((w/imgW), (h/imgH));

			staticAnchor = {
				x: 0, y: 0,
				width: centerX, height: centerY,
				imgW: (imgW * scale), imgH: (imgH * scale),
				scale: scale
			}

			cornerRect = {
				width: centerX,
				height: centerY
			}

			translatePos = {
				x: 0,
				y: 0
			}
		}
		else {
			// onSlide
			scale = minScale + ( (1 - minScale) * ($imgerScaler.val() / 100) );

			cornerRect.width = staticAnchor.width * ((imgW * scale) / staticAnchor.imgW);
			cornerRect.height = staticAnchor.height * ((imgH * scale) / staticAnchor.imgH);
			
			translatePos.x = -(cornerRect.width - centerX);
			translatePos.y = -(cornerRect.height - centerY);
		}

		//prevent dragging past image borders
		limitX = w - (imgW * scale);
		limitY = h - (imgH * scale);
	}

	var draw = function() {
		if(translatePos.x > 0) translatePos.x = 0;
		else if(translatePos.x < limitX) translatePos.x = limitX;

		if(translatePos.y > 0) translatePos.y = 0;
		else if(translatePos.y < limitY) translatePos.y = limitY;

    	imgerContext.save();
    	imgerContext.clearRect(0, 0, w, h);
        imgerContext.setTransform(scale, 0, 0, scale, translatePos.x, translatePos.y);
        imgerContext.drawImage(image, 0, 0);
        imgerContext.restore();
	}

	var onScalerSlide = function(e) {
		setPlacements(false);
		draw();
	}

	var onScalerSet = function(e) {
		//@martin imgerCompress.load( image, $imgerCanvas.attr('id') );

		//TODO*** using draw() for now
		//var resampled = resampler.resample(image, imgW, imgH);
		draw();

		setHistory('scale');
	}

	/* HISTORY MANAGER BEATING ME 4NOW :) */

	var setHistory = function(s) {
		switch(s) {
			case "scale":
			case "drag":
				history.push(
					{
						key: s,
						scaler: $imgerScaler.val(),
						translatePos: $.extend({}, translatePos),
						cornerRect: $.extend({}, cornerRect),
						limitY: (limitY+0),
						limitX: (limitX+0)
					}
				);
				//console.log(history[history.length-1]);
			break;
		}
	}

	var handleHistory = function(undo) {
		var target, other;
		if(undo) {
			if(!history.length) return;
			target = history;
			other = historyredo;
		}
		else {
			if(!historyredo.length) return;
			target = historyredo;
			other = history;
		}

		var toOther = target.pop();
		var t = target.pop();
		var key = t.key;

		switch(key) {
			case "scale":
			case "drag":
				translatePos = $.extend({}, t.translatePos);
				cornerRect = $.extend({}, t.cornerRect);
				limitY = (t.limitY+0);
				limitX = (t.limitX+0);
				$imgerScaler.val(t.scaler);
				draw();
				other.push(toOther);
			break;
		}
	}

	/* END HISTORY MANAGER */

	// Drag events

	var onMouseDwn = function(e) {
		if(translatePos === null) return;

        startDragOffset.x = e.clientX - translatePos.x;
        startDragOffset.y = e.clientY - translatePos.y;

		$imgerWR.on('mousemove', onMouseMve);
		$imgerWR.on("mouseup", onDragEnd);
		$imgerDisplay.on("mouseleave", onDragEnd);
	}

	var onMouseMve = function(e) {
		translatePos.x = e.clientX - startDragOffset.x;
		translatePos.y = e.clientY - startDragOffset.y;
		draw();
    }

    var onDragEnd = function(e) {
		staticAnchor.x = translatePos.x;
		staticAnchor.y = translatePos.y;
		staticAnchor.width = -translatePos.x + centerX;
		staticAnchor.height = -translatePos.y + centerY;
		staticAnchor.imgW = imgW * scale;
		staticAnchor.imgH = imgH * scale;
		staticAnchor.scale = scale;
		mouseDown = false;

		$imgerWR.off('mousemove', onMouseMve);
		$imgerWR.off("mouseup", onDragEnd);
		$imgerDisplay.off("mouseleave", onDragEnd);

		setHistory('drag');
	}

	var keyDownHandler = function(e) {
		if(e.which === 90 && e.ctrlKey) {
			handleHistory(true);
		}
		else if(e.which === 89 && e.ctrlKey) {
			handleHistory(false);
		}
	}

	var addBindings = function(b, t) {
		b ? $c = 'on' : $c = 'off';

		// no inline functions as the bibdings wont be removed

		$imgerCancelBTN[$c]('click', t.exit);

		$imgerBrowselBTN[$c]('click', initBrowse);

		$imgerCanvas[$c]('dblclick', initBrowse); // TODO*** click events are still registered so throws errors when blank

		$fileSelector[$c]('change', selectFile);

		$imgerDoneBTN[$c]('click', doneHandler);

		$getURL[$c]('click', initURLGet);

		$imgerScaler[$c]('slide', onScalerSlide);
		$imgerScaler[$c]('set', onScalerSet);

		$imgerCanvas[$c]('mousedown', onMouseDwn);

		$imgerFormSbmtBTN[$c]('click', submitForm);

		$imgerFormCancelBTN[$c]('click', cancelForm);

		//$document[$c]('keydown', keyDownHandler); // TODO*** not functional yet
	}

	var key_or_xyz = function(x, y, z) {
		var result = y[x];
		if(typeof result == 'undefined'){
			if(typeof z == 'function') {
				return z();
			}
			return z;
		}
		return y[x];
	}

	var object_dot_path = function(obj, path, objectAndKey) {
		var arr = path.split('.');
		var length = arr.length;

		var t_obj = null;

		for(var i = 0; i < length; i++) {
			if(i == 0) {
				t_obj = obj[arr[0]]
				if(objectAndKey && length == 1) return{obj: obj, key: arr[0]}
				continue;
			}

			if(typeof t_obj === 'function') {
				t_obj = t_obj()
			}

			t_obj = t_obj[arr[i]];
		}

		if(objectAndKey && i == (length-1)) return{obj: t_obj, key: arr[i]}

		return t_obj;
	}


	this.open = function(options) {
		$body.append($imgerWR);
		initSetup(this);

		//add eventlisteners
		addBindings(true, this);

		//key_or_xyz is a function that checks if a key exists and returns a specified default (the last argument)

		w = key_or_xyz('width', options, defaultWidth);
		h = key_or_xyz('height', options, defaultHeight);

		bolb = key_or_xyz('blob', options, false);

		form = key_or_xyz('form', options, null);

		quality = key_or_xyz('quality', options, 100);

		if(typeof form == 'string') {
			form = object_dot_path(forms, form);
		}

		mime = key_or_xyz('mime', options, mimeDefault);

		if(mimeTypes.indexOf(mime) == -1) {
			if(extentionTypes.indexOf(mime) == -1) {
				console.log("Imger mime error! Unsuported mime format. please use: (" + mimeTypes.toString() + "). Reverting to default: '" + mimeDefault);
			}
			else {
				mime = 'image/' + mime;
			}
		}

		extention = mime.split('/').pop();
		if(extention == 'jpeg') extention = 'jpg';

		resampler_path = key_or_xyz('resampler', options, 'imger.default');
		resampler = object_dot_path(resamplers, resampler_path);

		centerX = w * 0.5;
		centerY = h * 0.5;
		
		//reset to null (assists with error checking further down)
		dataurl = null;

		//doneTarget assists with dynamic reference to "typeDefaults"
		doneTarget = "upload";

		//get settings for upload
		upload = key_or_xyz('upload', options, null);

		if(upload == null) {
			//doneTarget assists with dynamic reference to "typeDefaults"
			doneTarget = "dataurl";

			//get settings for dataurl
			dataurl = key_or_xyz('dataurl', options, null);
		}

		if(upload == null && dataurl == null){
			console.log('Imger Error! Need at least a "upload" or "dataurl" to be specified');
			return;
		}

		s = key_or_xyz('note', options, '');
		s += '<br />Min size: ' + w + ' X ' + h;
		$('.imger-user-info').html(s);

		$imgerCanvas.css({
			width: w,
			height: h
		});

		var canvas = $imgerCanvas[0];
		canvas.width = w;
		canvas.height = h;

		$imgerDoneBTN.text(key_or_xyz('doneLabel', options, function(){
			return typeDefaults[doneTarget].doneLabel;
		}));

		if(key_or_xyz('autobrowse', options, false)) {
			$imgerBrowselBTN.click();
		}

		//@martin $imgerDoneBTN.click( function() {
			// TODO: Upload handling.
		//});
	}

	this.exit = function(options) {
		//remove eventlisteners
		addBindings(false, this);

		cancelForm(null, true);

		$imgerImageInfo.text('');

		$imgerWR.detach();
	}

	this.ready = function() {
		return _ready;
	}

	this.registerForm = function(options) {
		// basic form that can upload info with the image
	}

	this.registerResampler = function(resampler) {
		// resamples image ate the end of a scale
	}

	this.getFormData = function() {
		//return formData;
	}
}

window.Imger = Imger;

}(window, document));