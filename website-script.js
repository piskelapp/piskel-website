(function () {
	var piskels = [];
	var baseUrl = "http://juliandescottes.github.com/piskel/?frameId=";
	var serviceUrl = "http://3.piskel-app.appspot.com/";
	var piskelsLoaded = -1;
	
	var retrievePiskels = function () {
		var xhr = new XMLHttpRequest();
		xhr.open('GET',  serviceUrl + "all", true);
		xhr.responseType = 'text';

		xhr.onload = function(e) {
			eval("var responseObject = " + this.responseText);
			var keys = responseObject.keys;
			piskels = responseObject.keys;
			loadPiskels(0, 20);
		};
		xhr.send();
	};

	var loadPiskels = function (offsetBegin, offsetEnd) {
		var list = document.getElementById("main-piskel-list");
		for (var i = offsetBegin ; i < Math.min(offsetEnd, piskels.length) ; i++) {
			var key = piskels[i];
			var li = document.createElement("LI");
			li.className = "piskel-preview";
			li.innerHTML = "<a target='_blank' id='"+key+"'' href='"+baseUrl+key+"' title='"+key+"'></a>"
			list.appendChild(li);
			loadPreview(key);
		}
		piskelsLoaded = Math.min(offsetEnd, piskels.length);
		if (piskelsLoaded == piskels.length) {
			document.getElementById("load-more").innerHTML = "No more piskels !";
		}
	};

	var loadPreview = function (key) {
		var xhr = new XMLHttpRequest();
		xhr.open('GET',  serviceUrl + "get?l="+key, true);
		xhr.responseType = 'text';

		xhr.onload = function(e) {
			try {
				var res = JSON.parse(this.responseText);
				var frame = res.framesheet[0];
				var canvas = document.createElement("canvas");
				canvas.setAttribute("width", 100);
				canvas.setAttribute("height", 100);
				var width = frame.length, height = frame[0].length;
				var dpi = calculateDPI(100, 100, width, height);

				var context = canvas.getContext('2d');

				for(var col = 0 ; col < width; col++) {
					for(var row = 0 ; row < height; row++) {
						var color = frame[col][row];
						if(color != 'TRANSPARENT') {
							context.fillStyle = color;
							context.fillRect(col * dpi , row * dpi, dpi, dpi);
						}
					}
				}
				document.getElementById(key).appendChild(canvas);
			} catch (e) {
				throw "Couldn't load preview for piskel ["+key+"]. Piskel is probably corrupted and should be removed."
			}
			

			
		};
		xhr.send();
	};

	var calculateDPI = function (height, width, pictureHeight, pictureWidth) {
      var heightBoundDpi = Math.floor(height / pictureHeight),
          widthBoundDpi = Math.floor(width / pictureWidth);

      return Math.min(heightBoundDpi, widthBoundDpi);
    }

	retrievePiskels();

	window.loadMore = function () {
		loadPiskels(piskelsLoaded + 1, piskelsLoaded + 21);
	};
})();