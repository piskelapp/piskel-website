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
          var width = imageInfo.width;
          var height = imageInfo.height;
          var zoom = imageInfo.zoom;

          var framesheet = [];
          var frames = Math.floor(img.width / width);
          for (var i = 0; i < frames; i++) {
            var canvas = pskl.website.createCanvas(width, height);
            canvas.getContext('2d').drawImage(img, i * width, 0, width, height, 0, 0, width, height);
            framesheet.push(pskl.website.scale(canvas, zoom));
          }
          imageInfo.framesheet = framesheet;
          if (imageInfo.hover) {
            startAnimationTimer(id);
          }
        };
      })(id);
      img.src = imageInfo.url;
    } else {
      startAnimationTimer(id);
    }
  };

  var startAnimationTimer = function(id) {
    var imageInfo = images[id];

    if (imageInfo.timer) {
      window.clearTimeout(imageInfo.timer);
    }

    // Default to 1 fps
    if (imageInfo.fps === 0) {
      imageInfo.fps = 1;
    }

    imageInfo.timer = window.setTimeout(function() {
      var w = imageInfo.width * imageInfo.zoom,
        h = imageInfo.height * imageInfo.zoom;
      var context = imageInfo.canvas.getContext('2d');
      context.clearRect(0, 0, imageInfo.canvas.width, imageInfo.canvas.height);
      context.drawImage(imageInfo.framesheet[imageInfo.animationIndex], imageInfo.xOffset, imageInfo.yOffset, w, h);
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
    context.drawImage(imageInfo.preview_canvas, imageInfo.xOffset, imageInfo.yOffset);
  };

  var __id = -1;
  window.pskl.website.createAnimatedPreview = function(piskelId, fps, event, animate) {
    var spritesheet_url = "/img/" + piskelId + "/framesheet";
    window.pskl.website.createSpritesheetPreview(piskelId, spritesheet_url, fps, event, animate);
  };

  window.pskl.website.createSpritesheetPreview = function(id, spritesheet_url, fps, event, animate) {
    var image = event.target || document.getElementById("image" + id);

    var targetSize = image.width;

    var zoom = targetSize / Math.max(image.naturalWidth, image.naturalHeight);
    var preview_canvas = pskl.website.scale(image, zoom);

    var canvas = pskl.website.createCanvas(targetSize, targetSize);
    let xOffset = Math.floor((targetSize - preview_canvas.width) / 2);
    let yOffset = Math.floor((targetSize - preview_canvas.height) / 2);
    canvas.getContext('2d').drawImage(preview_canvas, xOffset, yOffset);
    canvas.className = "animated-preview-widget";

    __id++;
    images["key" + __id] = {
      url: spritesheet_url,
      fps: fps,
      width: image.naturalWidth,
      height: image.naturalHeight,
      preview_canvas: preview_canvas,
      canvas: canvas,
      zoom: zoom,
      animationIndex: 0,
      hover: false,
      xOffset: xOffset,
      yOffset: yOffset
    };

    image.parentNode.replaceChild(canvas, image);

    if (animate) {
        onCanvasOver("key" + __id, targetSize);
    } else {
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
    }
  };
})();
