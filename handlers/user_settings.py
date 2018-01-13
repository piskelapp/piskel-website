from base import BaseHandler
from google.appengine.ext import db
from webapp2_extras.appengine.auth.models import Unique
from handlers import image as image_handler
import logging
import models
import json
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
                if not user.apikey:
                    user.apikey = str(uuid.uuid1())
                    user.put()
                values = {
                    'user_id': user_id,
                    'profile_user': user,
                    'has_footer' : True,
                    'DEFAULT_AVATAR_URL' : DEFAULT_AVATAR_URL,
                }
                self.render('user/user-settings.html', values)
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

        user.put()
        self.redirect('/user/' + user_id + '/settings')


    def get_target_transfer_user(self):
        if not self.is_logged_in:
            raise Exception('Not logged in')

        post_data = self.request.POST

        target_userid = str(post_data.get('target_userid'))

        if not target_userid:
            raise Exception('Missing target user id')

        if str(self.session_user['user_id']) == target_userid:
            raise Exception('Please use a different user id')

        try:
            target_user = self.auth.store.user_model.get_by_id(long(target_userid))
        except Exception as e:
            # unable to find user.
            target_user = False

        if not target_user:
           raise Exception('Unable to find user')

        target_apikey = str(post_data.get('target_apikey'))

        if not target_apikey:
            raise Exception('Missing target api key')

        if target_apikey != target_user.apikey:
           raise Exception('Wrong key')

        return target_user


    def prepare_transfer(self):
        try:
            target_user = self.get_target_transfer_user()
            current_user_id = self.session_user['user_id']
            stats = models.get_stats_for_user(current_user_id)
            count = int(stats['piskels_count'])

            return self.send_json_response({
                'status': 'ok',
                'count': count,
                'target_name': target_user.name
            })
        except Exception as error:
            return self.send_json_error(str(error))


    def do_transfer(self):
        try:
            target_user = self.get_target_transfer_user()
            current_user_id = self.session_user['user_id']
            piskels = models.get_piskels_for_user(current_user_id)
            for piskel in piskels:
                piskel.owner = target_user.key.id()
                piskel.put()
                # force consistency
                db.get(piskel.key())

            models.invalidate_user_cache(target_user.key.id())
            models.invalidate_user_cache(current_user_id)

            return self.send_json_response({
                'status': 'ok',
                'count': len(piskels),
                'target_name': target_user.name
            })
        except Exception as error:
            return self.send_json_error(str(error))

    def do_delete(self):
        if not self.is_logged_in:
            self.send_json_error('Not logged in')

        try:
            userid = self.session_user['user_id']
            user = self.auth.store.user_model.get_by_id(userid)

            # delete all piskels for the current user
            piskels = models.get_piskels_for_user(userid)
            for piskel in piskels:
                piskel.delete()
                # force consistency
                db.get(piskel.key())

            # logout current user
            self.auth.unset_session()

            # from webapp2_extras.appengine.auth.models.User
            # http://webapp-improved.appspot.com/_modules/webapp2_extras/appengine/auth/models.html#User
            #
            # def add_auth_id(self, auth_id):
            #   ...
            #   unique = '%s.auth_id:%s' % (self.__class__.__name__, auth_id)
            #   ...
            Unique.delete_multi( map(lambda s: 'User.auth_id:' + s, user.auth_ids) )

            # delete user entry
            user.key.delete()

            return self.send_json_response({
                'status': 'ok'
            })

        except Exception as error:
            return self.send_json_error(repr(error))


    def send_json_error(self, error):
        obj = {
            'status': 'error',
            'error': error
        }
        self.send_json_response(obj)


    def send_json_response(self, obj):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(obj))
