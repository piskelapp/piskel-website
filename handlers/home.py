from base import BaseHandler

class HomeHandler(BaseHandler):
  def get(self):
    values = {
      'user': self.current_user if self.is_logged_in else False,
      'session': self.session_user if self.is_logged_in else False,
      'is_logged_in': self.is_logged_in,
      'hide_create': True,
      'has_footer' : True
    }

    self.render("home.html", values)