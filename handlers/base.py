import webapp2, logging
from webapp2_extras import jinja2, auth, sessions
from config import secrets

class BaseHandler(webapp2.RequestHandler):
  def dispatch(self):
    # Get a session store for this request.
    self.session_store = sessions.get_store(request=self.request)

    try:
        # Dispatch the request.
        webapp2.RequestHandler.dispatch(self)
    finally:
        # Save all sessions.
        self.session_store.save_sessions(self.response)

  @webapp2.cached_property
  def auth(self):
      return auth.get_auth()

  @webapp2.cached_property
  def jinja2(self):
    # Returns a Jinja2 renderer cached in the app registry.
    return jinja2.get_jinja2(app=self.app)

  @webapp2.cached_property
  def is_logged_in(self):
    """Returns true if a user is currently logged in, false otherwise"""
    return self.auth.get_user_by_session() is not None

  @webapp2.cached_property
  def username(self):
    return self.current_user.name  

  @webapp2.cached_property
  def session_user(self):
    return self.auth.get_user_by_session()

  @webapp2.cached_property
  def session_user_id(self):
    return self.session_user['user_id']

  @webapp2.cached_property
  def current_user(self):
    return self.auth.store.user_model.get_by_id(self.session_user['user_id']) 

  def get_user(self, user_id):
    return self.auth.store.user_model.get_by_id(user_id)

  def render(self, template, values):
    # Add user (auth) specific variables
    values.update(
      {
        'user': self.current_user if self.is_logged_in else False,
        'session': self.session_user if self.is_logged_in else False,
        'is_logged_in': self.is_logged_in
      }
    )

    try:
      self.response.write(self.jinja2.render_template(template, **values))
    except Exception, e:
      self.abort(404, detail=e)