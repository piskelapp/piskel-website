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
      stats = models.get_stats_for_user(user_id)
      is_own_profile = self.is_logged_in and long(user_id) == self.session_user['user_id']      
      piskels = Piskel.prepare_piskels_for_view(self._get_piskels_for_category(user_id, cat, is_own_profile))
      categories = PRIVATE_CATEGORIES if is_own_profile else PUBLIC_CATEGORIES
      values = {
        # mandatory
        'user': self.current_user if self.is_logged_in else False,
        'session': self.session_user if self.is_logged_in else False,
        'is_logged_in': self.is_logged_in,
        # page-specific
        'profile_user': user,
        'category' : cat,
        'categories' : categories,
        'profile_stats' : stats,
        'profile_piskels': piskels,
        'is_own_profile': is_own_profile
        }
      self.render("user/user.html", values)
    else:
      self.abort(404)

  def _get_piskels_for_category(self, user_id, cat, is_own_profile):
    if is_own_profile:
      if cat == 'all':
        return models.get_piskels_for_user(user_id)
      if cat == 'public':
        return models.get_public_piskels_for_user(user_id)
      if cat == 'private':
        return models.get_private_piskels_for_user(user_id)
      if cat == 'deleted':
        return models.get_deleted_piskels_for_user(user_id)
    elif cat == 'public':
      return models.get_public_piskels_for_user(user_id)
    else:
      raise RuntimeError("Invalid category %s in User handler", cat)