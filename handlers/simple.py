from base import BaseHandler


def get_template(handler, template, is_home=False):
  values = {
    'is_home': is_home,
    'has_footer' : True,
    'has_previous_page' : True,
    'has_next_page' : True
  }

  handler.render(template, values)


class HomeHandler(BaseHandler):
  def get(self):
    get_template(self, 'home/home.html', True)


class PrivacyHandler(BaseHandler):
  def get(self):
    get_template(self, 'privacy/privacy.html', False)


class TermsHandler(BaseHandler):
  def get(self):
    get_template(self, 'terms/terms.html', False)


class DownloadHandler(BaseHandler):
  def get(self):
    get_template(self, 'download/download.html', False)


class FaqHandler(BaseHandler):
  def get(self):
    get_template(self, 'faq/faq.html', False)
