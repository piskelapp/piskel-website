import os, logging

# Copy this file into secrets.py and set keys, secrets and scopes.

# This is a session secret key used by webapp2 framework.
# Get 'a random and long string' from here:
# http://clsc.net/tools/random-string-generator.php
# or execute this from a python shell: import os; os.urandom(64)
SESSION_KEY = "T-x71L_86ZW-79g9S-83_NW-X_-l5k4_0-_j162pPK27-qmx_-"

GOOGLE = {
  # This id is only whitelisted for localhost:8081, please use this port for local development.
  'localhost' : {
    'id' : '452414156077-ad5kcjklv5gkn4etm6mtjouunhemc0fp.apps.googleusercontent.com',
    'secret' : 'oTj8rKTtjpyFxNMBnAz3D5lB'
  },
  'legacy' : {
    'id' : '5997570023-o9ujviltf0f8b692kea2pim6vbg2hmub.apps.googleusercontent.com',
    'secret' : '-lpooHZRA4MpzgTO9aE87ZOr'
  },
}

if "Dev" in os.environ['SERVER_SOFTWARE']:
  _google_key = "localhost"
else:
  # CURRENT_VERSION_ID is returned following the pattern : alpha.073856742296829858
  # The second part of the ID represents the upload time (see more at https://code.google.com/p/googleappengine/issues/detail?id=5788)
  current_version = os.environ['CURRENT_VERSION_ID'].split('.')[0]
  _google_key = current_version


# config that summarizes the above
AUTH_CONFIG = {
  'google'      : (GOOGLE[_google_key]['id'], GOOGLE[_google_key]['secret'], 'https://www.googleapis.com/auth/userinfo.profile')
}
