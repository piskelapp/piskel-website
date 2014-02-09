import webapp2
from webapp2_extras import jinja2
from base import BaseHandler

class LoginHandler(BaseHandler):      
  def get(self):
    if self.is_logged_in:
      self.redirect_to('home')

    values = {
      'username': self.username if self.is_logged_in else False,
      'is_logged_in': self.is_logged_in
    }

    self.render("login.html", values)