from base import BaseHandler

class PickedHandler(BaseHandler):
  def get(self):
    self.getPage(1)

  def getPage(self, index):
    index = int(index)
    values = {
      'user': self.current_user if self.is_logged_in else False,
      'session': self.session_user if self.is_logged_in else False,
      'is_logged_in': self.is_logged_in,
      'hide_create': False,
      'has_footer' : False,
      'has_previous_page' : index > 1,
      'has_next_page' : index < 10 ,
      'index' : index
    }

    self.render("gallery/list.html", values)