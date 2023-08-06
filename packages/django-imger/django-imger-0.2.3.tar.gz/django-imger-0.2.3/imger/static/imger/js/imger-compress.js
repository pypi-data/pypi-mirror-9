(function ( window, document ) {

function ImgerCompress ( ) {
	// Because of img.onload, we need canvas and context to be global
	var imger_canvas, imger_context, imger_status, imger_timer;

	var imgerImg = new Image();
	imgerImg.crossOrigin = "Anonymous"; //cors support
	imgerImg.onload = function() {
		console.log('[Imger] Buffer image loaded.');
	    var W = imgerImg.width;
	    var H = imgerImg.height;
	    imger_canvas.width = W;
	    imger_canvas.height = H;
	    console.log( imger_context );
	    imger_context.drawImage(imgerImg, 0, 0); //draw image
		imger_status = 'loaded';
	}



	// To preload an image on the canvas uncomment this:
	// imgerImg.src = '/path/to/image.jpg';


	/* Demo input for console:
	imgerLoad('input-images/test-01.jpg', 'demo_canvas');
	imgerResample('demo_canvas', imgerImg, 300);
	*/

	this.test = function () {
		console.log( 'test' );
	}

	// Manual control for loading images onto the target canvas
	this.load = function(img, targetCanvasId) {
		imger_status = 'loading';
		console.log('Changing imger_status to loading.');

		// Create deferred object
		var r = $.Deferred();
		
		// Get a handle on the canvas
		imger_canvas = document.getElementById(targetCanvasId);
		imger_context = imger_canvas.getContext("2d");
		
		// Load the image
		imgerImg.src = img;

		// Wait for browser to finish loading
		imger_timer = setTimeout( function() { delay(); }, 1000);
		function delay() {
		  if( imger_status === 'loaded' ) {
		  	console.log('[Imger] Buffering completed.');
		  	clearTimeout(imger_timer);
		  	r.resolve();
		  } else {
		  	console.log('[Imger] Buffering image...');
		  	imger_timer = setTimeout(function() { delay(); }, 1000);
		  }
		}

		return r;
	}


	// A controller to handle re-sampling.\
	// Uses a scale value to determine dimensions
	this.imgerResample = function(targetCanvasId, imgRef, scale) {
		console.log( document );
		console.log('[Imger] Resampling image...');

		imger_canvas = document.getElementById(targetCanvasId);
		context = imger_canvas.getContext("2d");

		var imgerImg = imgRef;

	    var W = imgerImg.width;
	    var H = imgerImg.height;
	    imger_canvas.width = W;
	    imger_canvas.height = H;
	    context.drawImage(imgerImg, 0, 0); //draw image
	    
	    //resize by ratio (with new width)
	    var newH = H * scale,
	    	newW = W * scale;
	    
	    resample_hermite(imger_canvas, W, H, newW, newH);
	    
	    return true;
	};


	// Re-sampling function using Hermite algorithm
	function resample_hermite(imger_canvas, W, H, W2, H2) {
		var time1 = Date.now();
		W2 = Math.round(W2);
		H2 = Math.round(H2);
		var imgerImg = imger_canvas.getContext("2d").getImageData(0, 0, W, H);
		var imgerImg2 = imger_canvas.getContext("2d").getImageData(0, 0, W2, H2);
		var data = imgerImg.data;
		var data2 = imgerImg2.data;
		var ratio_w = W / W2;
		var ratio_h = H / H2;
		var ratio_w_half = Math.ceil(ratio_w/2);
		var ratio_h_half = Math.ceil(ratio_h/2);
		
		for(var j = 0; j < H2; j++){
			for(var i = 0; i < W2; i++){
				var x2 = (i + j*W2) * 4;
				var weight = 0;
				var weights = 0;
				var weights_alpha = 0;
				var gx_r = gx_g = gx_b = gx_a = 0;
				var center_y = (j + 0.5) * ratio_h;
				for(var yy = Math.floor(j * ratio_h); yy < (j + 1) * ratio_h; yy++){
					var dy = Math.abs(center_y - (yy + 0.5)) / ratio_h_half;
					var center_x = (i + 0.5) * ratio_w;
					var w0 = dy*dy //pre-calc part of w
					for(var xx = Math.floor(i * ratio_w); xx < (i + 1) * ratio_w; xx++){
						var dx = Math.abs(center_x - (xx + 0.5)) / ratio_w_half;
						var w = Math.sqrt(w0 + dx*dx);
						if(w >= -1 && w <= 1){
							//hermite filter
							weight = 2 * w*w*w - 3*w*w + 1;
							if(weight > 0){
								dx = 4*(xx + yy*W);
								//alpha
								gx_a += weight * data[dx + 3];
								weights_alpha += weight;
								//colors
								if(data[dx + 3] < 255)
									weight = weight * data[dx + 3] / 250;
								gx_r += weight * data[dx];
								gx_g += weight * data[dx + 1];
								gx_b += weight * data[dx + 2];
								weights += weight;
								}
							}
						}		
					}
				data2[x2]     = gx_r / weights;
				data2[x2 + 1] = gx_g / weights;
				data2[x2 + 2] = gx_b / weights;
				data2[x2 + 3] = gx_a / weights_alpha;
				}
			}
		console.log("[Imger] Algorithm completed in: "+(Math.round(Date.now() - time1)/1000)+" s");
		imger_canvas.getContext("2d").clearRect(0, 0, Math.max(W, W2), Math.max(H, H2));
		imger_canvas.width = W2;
		imger_canvas.height = H2;
		imger_canvas.getContext("2d").putImageData(imgerImg2, 0, 0);
	}

}

window.ImgerCompress = ImgerCompress;

})( window, document );
