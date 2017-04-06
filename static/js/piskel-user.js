function getUserId() {
  return window.__pageInfo.userid;
}

function getCategory() {
  return window.__pageInfo.category;
}

function get(url, onload, onerror) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", url, true);
  xhr.onload = onload;
  xhr.onerror = onerror;
  xhr.send();
}

var dummyEl;
var getDummyEl = function () {
  if (!dummyEl) {
    dummyEl = document.createElement("div");
  }
  return dummyEl;
};

/**
 * Random templating util extracted from the piskel codebase.
 */
var replace = function (template, dict) {
  for (var key in dict) {
    if (dict.hasOwnProperty(key)) {
      var value = sanitize(dict[key]);
      template = template.replace(new RegExp('\\{\\{' + key + '\\}\\}', 'g'), value);
    }
  }
  return template;
};

/**
 * String sanitizer for the template values.
 */
var sanitize = function (string) {
  var dummyEl = getDummyEl();

  // Apply the unsafe string as text content and
  dummyEl.textContent = string;
  var sanitizedString = dummyEl.innerHTML;
  dummyEl.innerHTML = '';

  return sanitizedString;
};

/**
 * Sub template for generating the piskel "actions" part of the piskelcard.
 * @param  {Object} piskel
 *         Piskel returned by the server
 * @return {String} the markup for the piskelcard actions section
 */
var getPiskelActions = function (piskel) {
  var info = window.__pageInfo;
  var template = '';

  if (info.isOwnProfile) {
    if (piskel.deleted) {
      template =
        '<a class="card-preview-action right" href="#" onclick="if(window.confirm(\'This will permanently delete your piskel. Continue ?\')){window.location=\'/p/{{key}}/perm_delete?callback_url=/user/{{user_id}}/{{category}}\'}">Destroy</a>\
         <a class="card-preview-action right" href="/p/{{key}}/restore?callback_url=/user/{{user_id}}/{{category}}">Restore</a>';
    } else {
      template =
        '<a class="card-preview-action right" href="/p/{{key}}/delete?callback_url=/user/{{user_id}}/{{category}}">Delete</a>\
         <a class="card-preview-action right" href="/p/{{key}}/clone/gallery">Clone</a>\
         <a class="card-preview-action right" href="/p/{{key}}/view">View</a>\
         <a class="card-preview-action right bold important" href="/p/{{key}}/edit">Edit</a>';
    }
  } else {
    if (info.isLoggedIn) {
      template = '<a class="card-preview-action right" href="/p/{{key}}/clone/gallery">Clone</a>';
    }
    template += '<a class="card-preview-action right bold important" href="/p/{{key}}/view">View</a>';
  }

  return template;
};

/**
 * Sub template for generating the piskel "frames" part of the piskelcard.
 * @param  {Object} piskel
 *         Piskel returned by the server
 * @return {String} the markup for the piskelcard frames section
 */
var getPiskelFrames = function (piskel) {
  if (piskel.frames > 1) {
    return '<span class="counter">{{frames}}</span> frames - <span class="counter">{{fps}}</span> fps';
  } else {
    return 'Single frame';
  }
};

/**
 * Main template for generating a piskel card element
 * @param  {Object} piskel
 *         Piskel returned by the server
 * @return {String} the markup for the piskelcard
 */
var getPiskelCard = function (piskel) {
  var template = '<div class="card-container {{className}}">\
    <div class="card-preview-container">\
      <a class="card-preview-link" href="/p/{{key}}/view">\
        <img\
          id="image{{framesheet_key}}"\
          style="display:block; width:192px; height:192px;"\
          width="192"\
          src="/img/{{framesheet_key}}/preview"\
          onload="window.pskl.website.createAnimatedPreview(\'{{framesheet_key}}\', {{fps}}, event, false)"/>\
      </a>\
      <div class="card-preview-actions">' + getPiskelActions(piskel) + '</div>\
    </div>\
    <div class="card-info-container">\
      <h4 class="card-info-name" title="Edit this sprite"><a href="/p/{{key}}/edit">{{name}}</a></h4>\
      <p class="card-info-meta">' + getPiskelFrames(piskel) + '</p>\
    </div>\
  </div>';

  return replace(template, {
    className: piskel.private ? 'card-container-private': '',
    key: piskel.key,
    framesheet_key: piskel.framesheet_key,
    fps: piskel.fps,
    name: piskel.name,
    frames: piskel.frames,
    user_id: getUserId(),
    category: getCategory()
  });
};

/**
 * Create DOM elements for each provided piskel and insert it in the user piskels container
 * @param {Array} piskels array of piskel objects
 */
function insertPiskelCards(piskels) {
  if (!piskels || piskels.length === 0) {
    return;
  }

  var container = document.querySelector('.user-piskels-grid');
  var dummyEl = getDummyEl();
  dummyEl.innerHTML = piskels.reduce(function (markup, piskel) {
    return markup + getPiskelCard(piskel);
  }, '');
  while (dummyEl.firstChild) {
    container.appendChild(dummyEl.firstChild);
  }
}

/**
 * Load a bucket of user piskels. After retrieving them from the server
 * they will be inserted in the DOM of the page.
 *
 * @param  {Number} offset
 *         The bucket offset
 * @param  {Number} limit
 *         The bucket size
 */
function loadUserPiskels(offset, limit) {
  get(
    "/user/" + getUserId() + "/" + getCategory() + "/piskels/" + offset + "/" + limit,
    function (e) {
      if (this.status != 200) {
        console.error("Failed to retrieve user piskels");
        return;
      }

      var response = JSON.parse(this.responseText);
      var container = document.querySelector('.user-piskels-grid');
      if (response.piskelsCount > 0) {
        if (offset === 0) {
          // If this is the first bucket received, clear out the loading message.
          container.innerHTML = '';
        }
        // If the response contained some piskels, add them in the page and call the next bucket.
        insertPiskelCards(response.piskels);
        loadUserPiskels(offset + limit, limit);
      } else if (offset === 0) {
        container.innerHTML =
          '<div class="user-piskels-empty-message font-pixel">' +
            'No piskel available in \'' + getCategory() +'\' category.' +
          '</div>';
      }
    },
    function (e) {
      console.error("Failed to retrieve user piskels");
    }
  );
}

/**
 * Load the stats for the current user and display them in the page.
 */
function loadUserStats() {
  get(
    "/user/" + getUserId() + "/stats",
    function () {
      if (this.status != 200) {
        console.error("Failed to retrieve user/user_id/stats");
        return;
      }

      try {
        var stats = JSON.parse(this.responseText);
        document.getElementById("animation-duration").innerText = stats.animationDuration;
        document.getElementById("piskels-count").innerText = stats.piskelsCount;
        document.getElementById("frames-count").innerText = stats.framesCount;
      } catch (e) {
        // nothing to do ...
        console.error("Could not parse JSON response from user/user_id/stats");
      }
    },
    function () {
      console.error("Failed to retrieve user/user_id/stats");
    }
  );
}


window.addEventListener("load", function () {
  // If the BUCKET_SIZE needs to be updated, it should also be changed on the server side in
  // models/__init__.py, otherwise the calls to get the piskels will no longer be memcached.
  var BUCKET_SIZE = 100;
  // Get user piskels by buckets of 100.
  loadUserPiskels(0, BUCKET_SIZE);
  // Get user stats.
  loadUserStats();
});
