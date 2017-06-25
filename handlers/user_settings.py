from base import BaseHandler
from models import user_details as user_details_model
import models
import logging

PUBLIC_CATEGORIES = ['public']
PRIVATE_CATEGORIES = ['all', 'public', 'private', 'deleted']


class UserSettingsHandler(BaseHandler):
    def get(self, user_id):
        user = self.auth.store.user_model.get_by_id(long(user_id))
        if user:
            is_own_profile = self.is_logged_in and long(user_id) == self.session_user['user_id']
            logging.info("current_user: session")
            logging.info(self.current_user)
            logging.info("current_user: is_admin")
            logging.info(self.current_user.is_admin)
            logging.info("current_user: is_searchable")
            logging.info(self.current_user.is_searchable)
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

    def update(self, user_id):
        user = self.auth.store.user_model.get_by_id(long(user_id))
        post_data = self.request.POST
        user.is_searchable = bool(post_data.get('is_searchable'))
        user.put()
        self.redirect('/user/' + user_id + '/settings')
