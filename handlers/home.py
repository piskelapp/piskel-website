from base import BaseHandler

class HomeHandler(BaseHandler):
  def get(self):
    values = {
      'hide_create': True,
      'has_footer' : True,
      'has_previous_page' : True,
      'has_next_page' : True
    }

    self.render('home.html', values)