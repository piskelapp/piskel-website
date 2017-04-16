from base import BaseHandler

class HomeHandler(BaseHandler):
  def get(self):
    values = {
      'hide_create': True,
      'has_footer' : True,
      'has_previous_page' : True,
      'has_next_page' : True
    }

    self.render('home/home.html', values)


class PrivacyHandler(BaseHandler):
  def get(self):
    values = {
      'hide_create': False,
      'has_footer' : True,
      'has_previous_page' : True,
      'has_next_page' : True
    }

    self.render('privacy/privacy.html', values)


class TermsHandler(BaseHandler):
  def get(self):
    values = {
      'hide_create': False,
      'has_footer' : True,
      'has_previous_page' : True,
      'has_next_page' : True
    }

    self.render('terms/terms.html', values)