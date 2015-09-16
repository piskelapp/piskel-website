(function() {
	// @ require piskel-utils

  window.pskl = window.pskl || {};
  window.pskl.website = window.pskl.website || {};

  var __getImageData = function(image) {
    var w = getDim(image, "width");
    var h = getDim(image, "height");
    var canvas = pskl.website.createCanvas(w, h);

    var sourceContext = canvas.getContext('2d');
    sourceContext.drawImage(image, 0, 0);
    return sourceContext.getImageData(0, 0, w, h).data;
  };

  var _scaleNearestNeighbour = function(image, scaleInfo) {
    var canvas = pskl.website.createCanvas(scaleInfo.width, scaleInfo.height);

    var context = canvas.getContext('2d');

    var imgData = __getImageData(image);

    var yRanges = {}, xOffset = 0,
      yOffset = 0;
    // Draw the zoomed-up pixels to a different canvas context
    for (var x = 0; x < scaleInfo.srcWidth; x++) {
      // Calculate X Range
      xRange = (((x + 1) * scaleInfo.zoom) | 0) - xOffset;

      for (var y = 0; y < scaleInfo.srcHeight; y++) {
        // Calculate Y Range
        if (!yRanges[y + ""]) {
          // Cache Y Range
          yRanges[y + ""] = (((y + 1) * scaleInfo.zoom) | 0) - yOffset;
        }
        yRange = yRanges[y + ""];

        var i = (y * scaleInfo.srcWidth + x) * 4;
        var r = imgData[i];
        var g = imgData[i + 1];
        var b = imgData[i + 2];
        var a = imgData[i + 3];

        context.fillStyle = "rgba(" + r + "," + g + "," + b + "," + (a / 255) + ")";
        context.fillRect(xOffset, yOffset, xRange, yRange);
        yOffset += yRange;
      }
      yOffset = 0;
      xOffset += xRange;
    }
    return canvas;
  };

  var _scaleAntiAlias = function(image, scaleInfo) {
    var canvas = pskl.website.createCanvas(scaleInfo.width, scaleInfo.height);
    var context = canvas.getContext('2d');

    context.save();
    context.translate(canvas.width / 2, canvas.height / 2);
    context.scale(scaleInfo.zoom, scaleInfo.zoom);
    context.drawImage(image, -scaleInfo.srcWidth / 2, -scaleInfo.srcHeight / 2);
    context.restore();

    return canvas;
  };

  var _getScaleInfo = function(image, zoom) {
    var w = getDim(image, "width"), h = getDim(image, "height");
    return {
      zoom: zoom,
      srcWidth: w,
      srcHeight: h,
      width: Math.round(zoom * w),
      height: Math.round(zoom * h)
    };
  };

  /**
   * pskl.website.scale can accept images or canvas elements
   * Resolving dimensions differs depending on which tag is used.
   */
  var getDim = function (el, dim) {
    if (el.tagName == "CANVAS") {
      return el[dim];
    } else if (el.tagName == "IMG") {
      return el["natural" + dim.substring(0,1).toUpperCase() + dim.substr(1)];
    }
  };

  pskl.website.scale = function(image, zoom) {
    var canvas = null;
    if (zoom > 1) {
      canvas = _scaleNearestNeighbour(image, _getScaleInfo(image, zoom));
    } else {
      canvas = _scaleAntiAlias(image, _getScaleInfo(image, zoom));
    }
    canvas.setAttribute("data-src", image.src);
    return canvas;
  };
})();
