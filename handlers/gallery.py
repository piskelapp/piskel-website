from base import BaseHandler
from models.piskel import Piskel
import models

class BrowseHandler(BaseHandler):
    def is_admin(self):
        if not self.is_logged_in:
            return False

        user_id = self.session_user['user_id']
        user = self.auth.store.user_model.get_by_id(long(user_id))
        return user.is_admin

    def get(self):
        self.getPage(1)

    def get_page_piskels(self, index=1):
        piskels = models.get_recent_piskels(index)
        return Piskel.prepare_piskels_for_view(piskels)

    def getPage(self, index):
        if not self.is_admin():
            return self.render('error/piskel-unauthorized-action.html', {})

        index = int(index)
        values = {
            'is_home': False,
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
            'is_home': False,
            'has_footer' : False,
            'title': 'Featured pixel art',
            'path': '/featured',
            'has_previous_page' : index > 1,
            'has_next_page' : True,
            'index' : index,
            'page_piskels' : self.get_page_piskels(index)
        }

        self.render('gallery/list.html', values)
