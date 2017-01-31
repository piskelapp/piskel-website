import webapp2, logging
from google.appengine.ext import db
from base import BaseHandler
from models import Piskel
import models

PUBLIC_CATEGORIES = ['public']
PRIVATE_CATEGORIES = ['all', 'public', 'private', 'deleted']

class UserHandler(BaseHandler):
  def get_default(self, user_id):
    user = self.auth.store.user_model.get_by_id(long(user_id))
    if user:
      is_own_profile = self.is_logged_in and long(user_id) == self.session_user['user_id']
      if is_own_profile:
        self.get(user_id, 'all')
      else:
        self.get(user_id, 'public')

    else:
      self.abort(404)

  def get(self, user_id, cat):
    user = self.auth.store.user_model.get_by_id(long(user_id))
    if user:
      is_own_profile = self.is_logged_in and long(user_id) == self.session_user['user_id']

      if self._is_valid_category(user_id, cat):
        piskels = self._get_piskels_for_category(user_id, cat)
        view_piskels = Piskel.prepare_piskels_for_view(piskels)
        categories = PRIVATE_CATEGORIES if is_own_profile else PUBLIC_CATEGORIES
        values = {
          'user_id' : user_id,
          'profile_user' : user,
          'category' : cat,
          'categories' : categories,
          'profile_piskels': view_piskels,
          'is_own_profile': is_own_profile
          }
        self.render('user/user.html', values)
      else:
        self.redirect('/user/' + user_id + '/public')
    else:
      self.abort(404)

  def _get_piskels_for_category(self, user_id, cat):
    if cat == 'all':
      return models.get_piskels_for_user(user_id)
    if cat == 'public':
      return models.get_public_piskels_for_user(user_id)
    if cat == 'private':
      return models.get_private_piskels_for_user(user_id)
    if cat == 'deleted':
      return models.get_deleted_piskels_for_user(user_id)

  def _is_valid_category(self, user_id, cat):
    is_own_profile = self.is_logged_in and long(user_id) == self.session_user['user_id']
    if is_own_profile and cat in ['all', 'public', 'private', 'deleted']:
      return True
    else:
      return cat == 'public'
