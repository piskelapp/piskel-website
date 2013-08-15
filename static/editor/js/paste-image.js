var loadBlob = function (blob, callback) {
	var reader = new FileReader();
	reader.onload = function(event){
		callback(event.target.result);
	}; 
	reader.readAsDataURL(blob);
};

var componentToHex = function (c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

var rgbToHex = function (r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}
var importFramesheetFromDataUrl = function (dataUrl) {
	var image = new Image(),
		canvas = document.createElement("canvas"),
		context = canvas.getContext("2d");
	image.onload = function () {
		var w = image.width, h = image.height;
		canvas.width = w;
  		canvas.height = h;
		context.drawImage(image, 0,0,w,h,0,0,w,h);
		var imgData = context.getImageData(0,0,w,h).data;
		// Draw the zoomed-up pixels to a different canvas context
		var framesheet = [];
		for (var x=0;x<image.width;++x){
			framesheet[x] = [];
		  for (var y=0;y<image.height;++y){
		    // Find the starting index in the one-dimensional image data
		    var i = (y*image.width + x)*4;
		    var r = imgData[i  ];
		    var g = imgData[i+1];
		    var b = imgData[i+2];
		    var a = imgData[i+3];
		    if (a < 125) {
		    	framesheet[x][y] = "TRANSPARENT";
		    } else {
		    	framesheet[x][y] = rgbToHex(r,g,b);
		    }
		  }
		}
		pskl.app.loadFramesheet([framesheet]);
	}
	image.src = dataUrl;	
};


var getBlobFromClipboard = function (clipboardData) {
	var items = clipboardData.items;
	for (var i = 0 ; i < items.length ;i++) {
		if (/^image/i.test(items[i].type)) {
			return items[i].getAsFile();
		}
	}
	return false;
}

var onPasteEvent = function (event) {
	var blob = getBlobFromClipboard(event.clipboardData);
	if (blob) {
		loadBlob(blob, function (result) {
			importFramesheetFromDataUrl(result);
		})
	} else {
		console.log("Your clipboard doesn't contain an image :(");
	}				
};

window.addEventListener("paste", onPasteEvent);