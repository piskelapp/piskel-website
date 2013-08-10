(function() {
  // @require piskel-utils
  // @require piskel-image-scale

  window.pskl = window.pskl || {};
  window.pskl.website = window.pskl.website || {};

  var images = {};

  var onCanvasOver = function(id, targetSize) {
    var imageInfo = images[id];
    imageInfo.hover = true;
    if (!imageInfo.framesheet_canvas) {
      var img = new Image();
      img.onload = (function(id) {
        return function() {
          var imageInfo = images[id];
          var framesheet = [];
          var frames = Math.floor(img.width / imageInfo.width);
          for (var i = 0; i < frames; i++) {
            var canvas = pskl.website.createCanvas(imageInfo.width, imageInfo.height);
            var leftOffset = i * imageInfo.width;
            canvas.getContext('2d').drawImage(img, leftOffset, 0, imageInfo.width, imageInfo.height, 0, 0, imageInfo.width, imageInfo.height);
            framesheet.push(pskl.website.scale(canvas, imageInfo.zoom));
          }
          imageInfo.framesheet = framesheet;
          if (imageInfo.hover) {
            startAnimationTimer(id);
          }
        };
      })(id);
      img.src = "/img/" + imageInfo.piskelId + "/framesheet";
    } else {
      startAnimationTimer(id);
    }
  };

  var startAnimationTimer = function(id) {
    var imageInfo = images[id];

    if (imageInfo.timer) {
      window.clearTimeout(imageInfo.timer);
    }

    imageInfo.timer = window.setTimeout(function() {
      var w = imageInfo.width * imageInfo.zoom,
        h = imageInfo.height * imageInfo.zoom;
      var context = imageInfo.canvas.getContext('2d');
      context.clearRect(0, 0, imageInfo.canvas.width, imageInfo.canvas.height);
      context.drawImage(imageInfo.framesheet[imageInfo.animationIndex], 0, 0, w, h);
      startAnimationTimer(id);
      imageInfo.animationIndex = (imageInfo.animationIndex + 1) % imageInfo.framesheet.length;
    }, 1000 / imageInfo.fps);
  };

  var onCanvasOut = function(id) {
    var imageInfo = images[id];
    imageInfo.hover = false;
    window.clearTimeout(imageInfo.timer);
    imageInfo.animationIndex = 0;
    var context = imageInfo.canvas.getContext('2d');
    context.clearRect(0, 0, imageInfo.canvas.width, imageInfo.canvas.height);
    context.drawImage(imageInfo.preview_canvas, 0, 0);
  };

  var __id = -1;
  window.pskl.website.createAnimatedPreview = function(piskelId, fps, event) {
    var image = event.target || document.getElementById("image" + piskelId);

    var targetSize = image.width;

    var zoom = targetSize / Math.max(image.naturalWidth, image.naturalHeight);
    var preview_canvas = pskl.website.scale(image, zoom);

    var canvas = pskl.website.createCanvas(targetSize, targetSize);
    canvas.getContext('2d').drawImage(preview_canvas, 0, 0);
    canvas.className = "animated-preview-widget";

    __id++;
    images["key" + __id] = {
      piskelId: piskelId,
      fps: fps,
      width: image.naturalWidth,
      height: image.naturalHeight,
      preview_canvas: preview_canvas,
      canvas: canvas,
      zoom: zoom,
      animationIndex: 0,
      hover: false
    };

    image.parentNode.replaceChild(canvas, image);

    // Targetting parentNode because the canvas is below an inset border 
    canvas.parentNode.addEventListener('mouseover', (function(id, targetSize) {
      return function(event) {
        onCanvasOver(id, targetSize);
      };
    })("key" + __id, targetSize));

    canvas.parentNode.addEventListener('mouseout', (function(id, targetSize) {
      return function(event) {
        onCanvasOut(id, targetSize);
      };
    })("key" + __id, targetSize));
  };
})();
