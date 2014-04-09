from base import BaseHandler

class RedirectHandler(BaseHandler):
  def get(self, path):
    self.redirect("http://www.piskelapp.com" + path, permanent=True)