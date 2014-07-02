#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -*- coding: utf-8 -*-
from fix_path import fix_sys_path
fix_sys_path()

from config import secrets

from webapp2 import WSGIApplication, Route
from webapp2_extras import routes
from handlers import home, user, redirect



# webapp2 config
config = {
    'webapp2_extras.sessions': {
        'cookie_name': '_piskel_session',
        'secret_key': secrets.SESSION_KEY
    },
    'webapp2_extras.auth': {
        'user_attributes': []
    }
}

routes = [
  routes.DomainRoute('alpha.piskel-app.appspot.com', [Route('<:.*>',handler=redirect.RedirectHandler, name='redirect')]),
  Route('/', handler='handlers.gallery.PickedHandler', name='picked'),
  # ################ #
  #  GALLERY ROUTES  #
  # ################ #
  Route('/picked', handler='handlers.gallery.PickedHandler', name='picked'),
  Route('/picked/<index>', handler='handlers.gallery.PickedHandler:getPage', name='picked-page'),
  # ############# #
  #  USER ROUTES  #
  # ############# #
  Route('/user/<user_id>', handler='handlers.user.UserHandler:get_default', name='user-page'),
  Route('/user/<user_id>/<cat>', handler=user.UserHandler, name='user-page-cat'),
  # ############# #
  #  AUTH ROUTES  #
  # ############# #
  Route('/auth/<provider>', handler='handlers.oauth.AuthHandler:_simple_auth', name='auth_login'),
  Route('/auth/<provider>/callback', handler='handlers.oauth.AuthHandler:_auth_callback', name='auth_callback'),
  Route('/logout', handler='handlers.oauth.AuthHandler:logout', name='logout'),
  Route('/login', handler='handlers.login.LoginHandler', name='login'),
  # ############# #
  # EDITOR ROUTES #
  # ############# #
  Route('/p/create', handler='handlers.piskel.PiskelHandler:create', name='piskel-create'),
  # ############# #
  # PISKEL ROUTES #
  # ############# #
  Route('/p/<piskel_id>/history', handler='handlers.piskel.PiskelHandler:get_history', name='piskel-view-history'),
  Route('/p/<piskel_id>/view', handler='handlers.piskel.PiskelHandler:view', name='piskel-view'),
  Route('/p/<piskel_id>/delete', handler='handlers.piskel.PiskelHandler:delete', name='piskel-delete'),
  Route('/p/<piskel_id>/perm_delete', handler='handlers.piskel.PiskelHandler:permanently_delete', name='piskel-permanent-delete'),
  Route('/p/<piskel_id>/clone', handler='handlers.piskel.PiskelHandler:clone', name='piskel-clone'),
  Route('/p/<piskel_id>/clone/<action>', handler='handlers.piskel.PiskelHandler:clone', name='piskel-clone-action'),
  Route('/p/<piskel_id>/rollback/<framesheet_id>', handler='handlers.piskel.PiskelHandler:rollback_piskel_to_framesheet', name='piskel-rollback'),
  Route('/p/<piskel_id>/restore', handler='handlers.piskel.PiskelHandler:restore', name='piskel-restore'),
  Route('/p/<piskel_id>/edit', handler='handlers.piskel.PiskelHandler:edit', name='piskel-edit'),
  Route('/p/<piskel_id>/save', handler='handlers.piskel.PiskelHandler:save', name='piskel-save', methods=['POST']),
  Route('/p/<piskel_id>/updateinfo', handler='handlers.piskel.PiskelHandler:updateinfo', name='piskel-update', methods=['POST']),
  # ############# #
  # IMAGE  ROUTES #
  # ############# #
  Route('/img/<image_name>', handler='handlers.image.GetImageHandler', name='image-get'),
  Route('/img/<framesheet_id>/preview', handler='handlers.image.GetImageHandler:get_framesheet_preview', name='image-get-preview'),
  Route('/img/<framesheet_id>/framesheet', handler='handlers.image.GetImageHandler:get_framesheet', name='image-get-framesheet')
]

app = WSGIApplication(routes, config=config, debug=True)