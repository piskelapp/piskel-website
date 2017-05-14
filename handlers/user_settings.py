from base import BaseHandler
from models import user_details as user_details_model
import models

PUBLIC_CATEGORIES = ['public']
PRIVATE_CATEGORIES = ['all', 'public', 'private', 'deleted']


class UserSettingsHandler(BaseHandler):
    def get(self, user_id):
        user = self.auth.store.user_model.get_by_id(long(user_id))
        if user:
            is_own_profile = self.is_logged_in and long(user_id) == self.session_user['user_id']
            if is_own_profile:
                values = {
                    'user_id': user_id,
                    'profile_user': user,
                    'has_footer' : True,
                }
                self.render('user/user_settings.html', values)
            else:
                self.abort(401)  # Unauthorized
        else:
            self.abort(404)
