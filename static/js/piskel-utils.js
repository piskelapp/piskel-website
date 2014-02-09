(function () {
	window.pskl = window.pskl || {};
	window.pskl.website = window.pskl.website || {};
	
	window.pskl.website.createCanvas = function(width, height) {
    var canvas = document.createElement('canvas');
    canvas.setAttribute("width", width);
    canvas.setAttribute("height", height);
    return canvas;
  };
})();