function getUserId() {
  var href = window.location.href;
  return href.match(/\/user\/(\d+)/)[1];
}

function onStatsReceived(responseText) {
  try {
    var stats = JSON.parse(responseText);
    document.getElementById("animation-duration").innerText = stats.animationDuration;
    document.getElementById("piskels-count").innerText = stats.piskelsCount;
    document.getElementById("frames-count").innerText = stats.framesCount;
  } catch (e) {
    // nothing to do ...
    console.error("Could not parse JSON response from user/user_id/stats");
  }
}

window.addEventListener("load", function () {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/user/" + getUserId() + "/stats", true);

  xhr.onload = function (e) {
    if (this.status == 200) {
      onStatsReceived(this.responseText);
    } else {
      console.error("Failed to retrieve user/user_id/stats");
    }
  };

  xhr.onerror = function (e) {
    console.error("Failed to retrieve user/user_id/stats");
  };

  xhr.send();
});
