(function () {

  function post(url, formData, onload, onerror) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.onload = onload;
    xhr.onerror = onerror;
    xhr.send(formData);
  }
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
    document.querySelector("[name='name']").value = __pageInfo.name;
    document.querySelector("[name='location']").value = __pageInfo.location;
    document.querySelector(".user-settings-bio").value = __pageInfo.bio;
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

  var onDeleteButtonClick = function (e) {
    e.preventDefault();
    showModal("delete");
  };

  var onTransferButtonClick = function (e) {
    e.preventDefault();
    showModal("transfer");
  };

  var showModal = function (id) {
    closeModal();
    var modal = document.getElementById(id + "-modal");
    modal.classList.remove("hidden");
    document.body.classList.add("has-modal");
  };

  var closeModal = function () {
    var openedModal = document.querySelector(".user-settings-modal:not(.hidden)");
    if (openedModal) {
      openedModal.classList.add("hidden")
    }
    document.body.classList.remove("has-modal");
  };

  var onDelegatedBodyClick = function (e) {
    var target = e.target;
    if (target.dataset && target.dataset.action === "close-modal") {
      e.preventDefault();
      closeModal();
    } else if (target.dataset.action == "prepare-transfer") {
      e.preventDefault();
      prepareTransfer();
    } else if (target.dataset.action == "confirm-transfer") {
      e.preventDefault();
      confirmTransfer();
    } else if (target.dataset.action == "delete") {
      e.preventDefault();
      deleteUser();
    }
  };

  var getTransferFormData = function () {
    var formData = new FormData();
    var userid = document.querySelector("[name='transfer-userid']").value;
    formData.append("target_userid", userid.trim());
    var apikey = document.querySelector("[name='transfer-apikey']").value;
    formData.append("target_apikey", apikey.trim());
    return formData;
  };

  var goldify = function (str) {
    return "<span style='color: gold;'>" + str + "</span>";
  };

  var pluralize = function (str, count) {
    return count == 1 ? (count + " " + str) : (count + " " + str + "s");
  }

  var prepareTransfer = function () {
    post("/user/transfer/prepare", getTransferFormData(), function onPrepareSuccess (e) {
      if (e.target.status != 200) {
        alert('Failed to prepare transfer, check your user id and secret key.');
        return;
      }

      var response = JSON.parse(e.target.response);
      if (response.status === 'ok') {
        var confirmDescription = document.getElementById("transfer-confirm-description");
        confirmDescription.innerHTML = confirmDescription.innerHTML
                                        .replace("${sprites}", goldify(pluralize("sprite", response.count)))
                                        .replace("${target_name}", goldify(response.target_name));
        showModal("transfer-confirm");
      } else {
        alert(response.error);
      }
    }, function onPrepareError() {
      alert('Failed to prepare transfer, check your user id and secret key.');
    });
  };

  var confirmTransfer = function () {
    post("/user/transfer/confirm", getTransferFormData(), function onConfirmSuccess (e) {
      if (e.target.status != 200) {
        alert('Transfer failed');
        return;
      }

      var response = JSON.parse(e.target.response);
      if (response.status === 'ok') {
        var completedDescription = document.getElementById("transfer-completed-description");
        completedDescription.innerHTML = completedDescription.innerHTML
                                          .replace("${sprites}", goldify(pluralize("sprite", response.count)))
                                          .replace("${target_name}", goldify(response.target_name));
        showModal("transfer-completed");
      } else {
        alert(response.error);
      }
    }, function onConfirmError() {
      alert('Transfer failed');
    });
  };

  var deleteUser = function () {
    post("/user/settings/delete", {}, function onConfirmSuccess (e) {
      if (e.target.status != 200) {
        alert('Could not delete your user');
        return;
      }

      var response = JSON.parse(e.target.response);
      if (response.status === 'ok') {
        showModal("delete-completed");
        // User was logged out and we should navigate to the home page
        window.setTimeout(function () {
          window.location = "/";
        }, 6000);
      } else {
        alert(response.error);
      }
    }, function onConfirmError() {
      alert('Could not delete your user');
    });
  };

  window.addEventListener("load", function () {
    // Button click listeners
    document.getElementById("save-button").addEventListener('click', onSaveButtonClick);
    document.getElementById("reset-button").addEventListener('click', onResetButtonClick);
    document.getElementById("upload-avatar-button").addEventListener('click', onUploadAvatarClick);
    document.getElementById("no-avatar-button").addEventListener('click', onDefaultAvatarClick);

    // Modal openers
    document.getElementById("delete-button").addEventListener('click', onDeleteButtonClick);
    document.getElementById("transfer-button").addEventListener('click', onTransferButtonClick);

    document.body.addEventListener('click', onDelegatedBodyClick);

    // Change listeners
    getHiddenFileInput().addEventListener('change', onHiddenFileInputChange);
  });
})();
