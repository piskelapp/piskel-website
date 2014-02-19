import webapp2
from webapp2_extras import jinja2
from google.appengine.ext import db
from base import BaseHandler
import models, logging

class HomeHandler(BaseHandler):
  def get(self):
    values = {
      'user': self.current_user if self.is_logged_in else False,
      'session': self.session_user if self.is_logged_in else False,
      'is_logged_in': self.is_logged_in,
      'hide_create': True
    }

    self.render("home.html", values)