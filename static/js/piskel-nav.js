(function () {

  var addPopupEventListeners = function (menuSelector, userLinkSelector) {
    window.addEventListener("click", function (e) {
      var target = e.target;
      var menu = document.querySelector(menuSelector);
      var userlink = document.querySelector(userLinkSelector);
      if (!menu) {
        return;
      }

      var isVisible = menu.classList.contains("visible");
      if (isVisible && !menu.contains(target)) {
        menu.classList.remove("visible");
        e.preventDefault();
      } else if (!isVisible && userlink.contains(target)) {
        menu.classList.add("visible");
        e.preventDefault();
      }
    });
  };

  addPopupEventListeners("#user-menu-popup", ".user-link");
  addPopupEventListeners("#nav-about-popup", ".nav-about-container");
  addPopupEventListeners("#tiny-menu-popup", ".tiny-button");
})();