(function() {
  // @require piskel-utils
  // @require piskel-image-scale

  // Progress bar height in pixels
  var PROGRESS_BAR_HEIGHT = 3;
  var PROGRESS_BAR_HEIGHT_HOVER = 8;

  // Minimum animation time for animating the progress bar
  var PROGRESS_BAR_TIME_THRESHOLD = 1000;

  window.pskl = window.pskl || {};
  window.pskl.website = window.pskl.website || {};

  var drawLoading = function(canvas) {
    var ctx = canvas.getContext('2d');
    // Overlay
    ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    // Loading text
    ctx.textBaseline = 'middle';
    ctx.textAlign = 'center';
    ctx.fillStyle = 'white';
    ctx.font = '30px Helvetica';
    ctx.fillText("Loading...", canvas.width / 2, canvas.height / 2);
  };

  var resetPreview = function(imageInfo) {
    imageInfo.animationIndex = 0;
    imageInfo.lastAnimationIndex = -1;
    var context = imageInfo.canvas.getContext('2d');
    context.clearRect(0, 0, imageInfo.canvas.width, imageInfo.canvas.height);
    context.drawImage(imageInfo.preview_canvas, 0, 0);
  };

  var images = {};

  var onCanvasOver = function(id, targetSize) {
    var imageInfo = images[id];
    imageInfo.hover = true;
    if (!imageInfo.framesheet) {
      drawLoading(imageInfo.canvas);
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
          resetPreview(imageInfo);
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
      window.cancelAnimationFrame(imageInfo.timer);
    }

    // Default to 1 fps
    if (imageInfo.fps === 0) {
      imageInfo.fps = 1;
    }

    if (imageInfo.animationIndex == 0 && imageInfo.lastAnimationIndex != imageInfo.animationIndex) {
      imageInfo.startTime = Date.now();
    }

    imageInfo.lastAnimationIndex = imageInfo.animationIndex;

    imageInfo.timer = window.requestAnimationFrame(function() {
      var timePerFrame = 1000 / imageInfo.fps;
      var fullAnimationTime = imageInfo.frames * timePerFrame;
      if (imageInfo.progressBarHover) {
        imageInfo.startTime = Date.now() - (timePerFrame * (imageInfo.progressBarHoverFrame));
      }
      var timeElapsedSinceStart = Date.now() - imageInfo.startTime;

      var w = imageInfo.width * imageInfo.zoom,
        h = imageInfo.height * imageInfo.zoom;
      var context = imageInfo.canvas.getContext('2d');
      context.clearRect(0, 0, imageInfo.canvas.width, imageInfo.canvas.height);
      context.drawImage(imageInfo.framesheet[imageInfo.animationIndex], 0, 0, w, h);
      imageInfo.animationIndex = Math.floor(timeElapsedSinceStart / timePerFrame) % imageInfo.frames;

      // Crisp lines
      context.save();
      context.translate(0.5, 0.5);
      context.lineWidth = 1;

      // Background
      var rectWidth = Math.round(imageInfo.canvas.width / imageInfo.frames);
      var rectHeight = (imageInfo.progressBarHover) ? PROGRESS_BAR_HEIGHT_HOVER : PROGRESS_BAR_HEIGHT;

      context.globalAlpha = 0.2;
      context.fillStyle = '#039BE5';
      context.fillRect(0, 0, imageInfo.canvas.width, rectHeight);

      // Progress
      context.globalAlpha = 0.9;
      context.save();
      context.shadowColor = '#01579B';
      context.shadowBlur = 20;
      context.shadowOffsetX = context.shadowOffsetY = 0;
      var progressWidth = Math.ceil(imageInfo.canvas.width * (timeElapsedSinceStart / fullAnimationTime));
      if (imageInfo.progressBarHover) {
        progressWidth += rectWidth / 2;
      } else if (fullAnimationTime < PROGRESS_BAR_TIME_THRESHOLD) {
        progressWidth = imageInfo.canvas.width;
      }
      context.fillRect(0, 0, progressWidth, rectHeight);
      context.restore();

      // Bars
      context.globalAlpha = 0.8;
      context.strokeStyle = '#026ca0';
      //context.strokeRect(0, 0, imageInfo.canvas.width - 1, rectHeight);
      for (var i = 1; i < imageInfo.frames; i++) {
        context.beginPath();
        context.moveTo(i * rectWidth, 0)
        context.lineTo(i * rectWidth, rectHeight);
        context.stroke();
      }

      context.restore();

      startAnimationTimer(id);
    });
  };

  var onCanvasOut = function(id) {
    var imageInfo = images[id];
    imageInfo.hover = imageInfo.progressBarHover = false;
    window.cancelAnimationFrame(imageInfo.timer);
    if (imageInfo.framesheet) {
      resetPreview(imageInfo);
    }
  };

  var onCanvasMove = function(event, id) {
    var imageInfo = images[id];
    var rect = imageInfo.canvas.getBoundingClientRect();
    var x = event.clientX - rect.left;
    var y = event.clientY - rect.top;

    // On progress bar
    if (imageInfo.framesheet) {
      if (y <= PROGRESS_BAR_HEIGHT_HOVER) {
        imageInfo.progressBarHover = true;
        var frame = Math.floor(x / (imageInfo.canvas.width / imageInfo.frames));
        imageInfo.progressBarHoverFrame = frame;
      } else if (imageInfo.progressBarHover) {
        imageInfo.progressBarHover = false;
      }
    }
  };

  var onCanvasOutAnimate = function(id) {
    var imageInfo = images[id];
    imageInfo.progressBarHover = false;
  };

  var __id = -1;
  window.pskl.website.createAnimatedPreview = function(piskelId, frames, fps, event, animate) {
    var image = event.target || document.getElementById("image" + piskelId);

    var targetSize = image.width;

    var zoom = targetSize / Math.max(image.naturalWidth, image.naturalHeight);
    var preview_canvas = pskl.website.scale(image, zoom);

    var canvas = pskl.website.createCanvas(targetSize, targetSize);
    canvas.getContext('2d').drawImage(preview_canvas, 0, 0);
    canvas.className = "animated-preview-widget";

    var imageInfo;
    __id++;
    images["key" + __id] = imageInfo = {
      piskelId: piskelId,
      frames: frames,
      fps: fps,
      width: image.naturalWidth,
      height: image.naturalHeight,
      preview_canvas: preview_canvas,
      canvas: canvas,
      zoom: zoom,
      animationIndex: 0,
      lastAnimationIndex: -1,
      hover: false,
      progressBarHover: false,
      progressBarHoverFrame: 0
    };

    image.parentNode.replaceChild(canvas, image);

    if (imageInfo.frames > 1) {
      if (animate) {
          onCanvasOver("key" + __id, targetSize);
          canvas.parentNode.addEventListener('mouseout', (function(id, targetSize) {
          return function(event) {
            onCanvasOutAnimate(id, targetSize);
          };
        })("key" + __id, targetSize));
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

      canvas.parentNode.addEventListener('mousemove', (function(id, targetSize) {
        return function(event) {
          onCanvasMove(event, id, targetSize);
        };
      })("key" + __id, targetSize));
    }
  };
})();
