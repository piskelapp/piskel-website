from base import BaseHandler
from models import Piskel
import models

class PickedHandler(BaseHandler):
  def get(self):
    self.getPage(1)

  def get_page_piskels(self, index=1):
    piskels = models.get_recent_piskels(index)
    return Piskel.prepare_piskels_for_view(piskels)

  def getPage(self, index):
    index = int(index)
    public_count = models.get_public_piskels_count()
    values = {
      'user': self.current_user if self.is_logged_in else False,
      'session': self.session_user if self.is_logged_in else False,
      'is_logged_in': self.is_logged_in,
      'hide_create': False,
      'has_footer' : False,
      'has_previous_page' : index > 1,
      'has_next_page' : (index-1) < (public_count/20) ,
      'index' : index,
      'page_piskels' : self.get_page_piskels(index)
    }

    self.render("gallery/list.html", values)