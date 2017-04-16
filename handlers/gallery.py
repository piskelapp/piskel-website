from base import BaseHandler
from models import Piskel
from models import user_details as user_details_model
import models

class BrowseHandler(BaseHandler):
    def is_admin(self):
        if not self.is_logged_in:
            return False

        user_id = self.session_user['user_id']
        userdetails = user_details_model.get_by_userid(user_id)
        return userdetails.admin

    def get(self):
        self.getPage(1)

    def get_page_piskels(self, index=1):
        if not self.is_admin():
            self.render('error/piskel-unauthorized-action.html', {})

        piskels = models.get_recent_piskels(index)
        return Piskel.prepare_piskels_for_view(piskels)

    def getPage(self, index):
        index = int(index)
        values = {
            'hide_create': False,
            'has_footer' : False,
            'title': 'Browse all',
            'path': '/admin/browse',
            'has_previous_page' : index > 1,
            'has_next_page' : True,
            'index' : index,
            'page_piskels' : self.get_page_piskels(index)
        }

        self.render('gallery/list.html', values)


class FeaturedHandler(BaseHandler):
    def get(self):
        self.getPage(1)

    def get_page_piskels(self, index):
        piskels = models.get_featured_piskels(index)
        return Piskel.prepare_piskels_for_view(piskels)

    def getPage(self, index):
        index = int(index)
        values = {
            'hide_create': False,
            'has_footer' : False,
            'title': 'Featured pixel art',
            'path': '/featured',
            'has_previous_page' : index > 1,
            'has_next_page' : True,
            'index' : index,
            'page_piskels' : self.get_page_piskels(index)
        }

        self.render('gallery/list.html', values)
