from base import BaseHandler
from handlers import image as image_handler
import logging
import uuid

PUBLIC_CATEGORIES = ['public']
PRIVATE_CATEGORIES = ['all', 'public', 'private', 'deleted']
DEFAULT_AVATAR_URL = '/static/resources/default-avatar.gif'

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
                    'DEFAULT_AVATAR_URL' : DEFAULT_AVATAR_URL,
                }
                self.render('user/user_settings.html', values)
            else:
                self.abort(401)  # Unauthorized
        else:
            self.abort(404)

    def update(self, user_id):
        user = self.auth.store.user_model.get_by_id(long(user_id))
        post_data = self.request.POST
        user.name = str(post_data.get('name'))
        user.location = str(post_data.get('location'))
        user.bio = str(post_data.get('bio'))

        avatar_url = str(post_data.get('avatar'))
        if avatar_url.startswith('data:image/'):
            path = image_handler.create_link(avatar_url, user_id)
            suffix = str(uuid.uuid1())
            user.avatar_url = '/img/' + path + '?' + suffix
        elif avatar_url == 'DEFAULT':
            user.avatar_url = DEFAULT_AVATAR_URL
        # elif avatar_url == 'CURRENT':
            # Nothing to do
        # else:
            # Not accepted

        user.put()
        self.redirect('/user/' + user_id + '/settings')
