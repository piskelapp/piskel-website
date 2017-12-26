from google.appengine.ext import db

from base import BaseHandler
from models import user_details as user_details_model

import models

class AdminHandler(BaseHandler):
    def is_admin(self):
        if not self.is_logged_in:
            return False

        user_id = self.session_user['user_id']
        userdetails = user_details_model.get_by_userid(user_id)
        return userdetails.admin

    def get(self):
        if not self.is_admin():
            self.render('error/piskel-unauthorized-action.html', {})

        self.render('admin/admin.html', {})

    def transfer(self):
        post_data = self.request.POST
        from_id = long(post_data.get('from'))
        to_id = long(post_data.get('to'))

        from_user = self.auth.store.user_model.get_by_id(from_id)
        to_user = self.auth.store.user_model.get_by_id(to_id)

        if not from_user:
            self.render('error/piskel-server-error.html', {
                'error': 'Could not find FROM user for TRANSFER'
            })

        if not to_user:
            self.render('error/piskel-server-error.html', {
                'error': 'Could not find TO user for TRANSFER'
            })

        piskels = models.get_piskels_for_user(from_id)
        msg = ""
        for piskel in piskels:
            msg += "Transfer " + str(piskel.key()) + " from " + str(from_id) + " to " + str(to_id) + ".\n"
            piskel.owner = to_id
            piskel.put()
            # force consistency
            db.get(piskel.key())

        models.invalidate_user_cache(from_id)
        models.invalidate_user_cache(to_id)

        self.render('error/piskel-server-error.html', {
            'error': msg
        })
