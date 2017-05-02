from base import BaseHandler
from models import Piskel
from models import user_details as user_details_model
import models
import json

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
                categories = PRIVATE_CATEGORIES if is_own_profile else PUBLIC_CATEGORIES
                values = {
                    'user_id': user_id,
                    'profile_user': user,
                    'category': cat,
                    'categories': categories,
                    'is_own_profile': is_own_profile
                }
                self.render('user/user.html', values)
            else:
                self.redirect('/user/' + user_id + '/public')
        else:
            self.abort(404)

    def get_piskels(self, user_id, cat, offset, limit):
        user = self.auth.store.user_model.get_by_id(long(user_id))
        if user:
            if self._is_valid_category(user_id, cat):
                piskels = models.get_piskels(user_id, cat, long(offset), long(limit))
                if piskels:
                    view_piskels = Piskel.prepare_piskels_for_view(piskels)
                    obj = {
                        'piskelsCount': len(piskels),
                        'piskels': view_piskels
                    }
                else:
                    obj = {
                        'piskelsCount': 0
                    }
                self.response.headers['Content-Type'] = 'application/json'
                self.response.out.write(json.dumps(obj))
            else:
                self.abort(401)  # Unauthorized
        else:
            self.abort(404)  # User not found

    def _is_valid_category(self, user_id, cat):
        is_own_profile = self.is_logged_in and long(user_id) == self.session_user['user_id']
        if is_own_profile and cat in ['all', 'public', 'private', 'deleted']:
            return True
        else:
            return cat == 'public'
