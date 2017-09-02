(function () {

  // Special values accepted for the avatar. Only base64 data uris allowed otherwise.
  var AVATAR = {
    CURRENT: "CURRENT",
    DEFAULT: "DEFAULT"
  };

  var onSaveButtonClick = function (e) {
    document.forms[0].submit();
    e.preventDefault();
  };

  var onResetButtonClick = function (e) {
    document.querySelector(".user-settings-input[name='name']").value = __pageInfo.name;
    document.querySelector(".user-settings-input[name='location']").value = __pageInfo.location;
    updateAvatar(AVATAR.CURRENT);

    e.preventDefault();
  };

  var getHiddenFileInput = function () {
    return document.querySelector(".user-settings-input[name='file']");
  };

  var onUploadAvatarClick = function (e) {
    getHiddenFileInput().click();
    e.preventDefault();
  };

  var onHiddenFileInputChange = function (evt) {
    var files = getHiddenFileInput().files;
    if (files.length == 1) {
      // Check mime type and size and prompt for error if needed.
      var reader = new FileReader();
      reader.addEventListener('loadend', function() {
        resizeAvatar(reader.result);
      });
      reader.readAsDataURL(files[0]);
    }
  };

  var resizeAvatar = function (dataURI) {
    var img = new Image();
    img.onload = function () {
      var height, width;
      if (img.width == img.height && img.width < 512) {
        updateAvatar(dataURI);
        return;
      }

      var imgMax = Math.max(img.width, img.height);
      var imgMin = Math.min(img.width, img.height);
      var canvas = document.createElement("canvas");
      canvas.setAttribute("height", Math.min(512, imgMin));
      canvas.setAttribute("width", Math.min(512, imgMin));
      var scale = Math.min(512, imgMin) / imgMin;
      var context = canvas.getContext("2d");
      context.scale(scale, scale);
      context.drawImage(img, (imgMin - img.width) / 2, (imgMin - img.height) / 2);
      updateAvatar(canvas.toDataURL("image/png"));
    };

    img.src = dataURI;
  }

  var onDefaultAvatarClick = function (e) {
    updateAvatar(AVATAR.DEFAULT);
    e.preventDefault();
  };

  var updateAvatar = function (value) {
    document.querySelector(".user-settings-input[name='avatar']").value = value;

    var url = value;
    if (url === AVATAR.DEFAULT) {
      url = __pageInfo.DEFAULT_AVATAR_URL;
    } else if (url === AVATAR.CURRENT) {
      url = __pageInfo.avatar;
    }

    document.querySelector(".user-settings-avatar-preview").setAttribute(
      "style",
      "background-image: url('" + url + "')");
  };

  window.addEventListener("load", function () {
    // Button click listeners
    document.getElementById("save-button").addEventListener('click', onSaveButtonClick);
    document.getElementById("reset-button").addEventListener('click', onResetButtonClick);
    document.getElementById("upload-avatar-button").addEventListener('click', onUploadAvatarClick);
    document.getElementById("no-avatar-button").addEventListener('click', onDefaultAvatarClick);

    // Change listeners
    getHiddenFileInput().addEventListener('change', onHiddenFileInputChange);
  });
})();
