from base import BaseHandler
from handlers import image as image_handler
import logging
import uuid

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

    def update(self, user_id):
        user = self.auth.store.user_model.get_by_id(long(user_id))
        post_data = self.request.POST
        user.is_searchable = bool(post_data.get('is_searchable'))
        user.name = str(post_data.get('name'))
        user.location = str(post_data.get('location'))

        avatar_url = str(post_data.get('avatar'))
        if avatar_url.startswith('data:image/'):
            avatar_url = '/img/' + image_handler.create_link(avatar_url, user_id) + '?' + str(uuid.uuid1())
        user.avatar_url = avatar_url

        user.put()
        self.redirect('/user/' + user_id + '/settings')
