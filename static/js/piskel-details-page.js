(function () {
  window.pskl = window.pskl || {};
  window.pskl.website = window.pskl.website || {};

	var form = null;
	var __memForm = function () {
		if (!form) form = document.getElementById("piskel-edit");
		return form;
	};

	window.addEventListener("keyup", function (evt) {
		if (evt.keyCode == 27 /* ESCAPE */) {
			pskl.website.hideEditForm();
		}
	});

	pskl.website.showEditForm = function () {
		if (__memForm()) form.classList.add("show");
	};
	pskl.website.hideEditForm = function () {
		if (__memForm()) form.classList.remove("show");
	};
	pskl.website.confirmDestroy = function (piskelKey, userId) {
		if (window.confirm('This will permanently delete this piskel. Continue ?')) {
			window.location = "/p/"+piskelKey+"/perm_delete?callback_url=/user/" + userId;
		}
	};

})();