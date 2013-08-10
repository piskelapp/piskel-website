import webapp2
from webapp2_extras import jinja2
from google.appengine.ext import db
from base import BaseHandler
import models, logging

class HomeHandler(BaseHandler): 
  def get_showcase_piskel_ids(self):
    return [12, 15, 18]

  def get_current_user_piskels(self):
    if self.is_logged_in:
      piskels = models.get_piskels_for_user(self.session_user_id,20)
      return models.Piskel.prepare_piskels_for_view(piskels)[:3]
    else:
      return []

  def get(self):
    values = {
      'user': self.current_user if self.is_logged_in else False,
      'session': self.session_user if self.is_logged_in else False,
      'is_logged_in': self.is_logged_in,
      'showcase_piskels': self.get_showcase_piskel_ids(),
      'user_piskels': self.get_current_user_piskels() if self.is_logged_in else []
    }

    self.render("home.html", values)