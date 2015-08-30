from models import Framesheet, Piskel
from google.appengine.ext import db
from base import BaseHandler
from handlers import image as image_handler

_ANONYMOUS_USER = long(100000001)

def hasFramesheetChanged_(piskel, content, fps):
  current_framesheet = piskel.get_current_framesheet()
  if current_framesheet:
    return current_framesheet.content != content or current_framesheet.fps != fps
  else:
    return True

def encode_for_view_(text):
  encoded_text = ""
  if text:
    encoded_text = u''.join((text))
    encoded_text = encoded_text.encode('unicode_escape')
    encoded_text = encoded_text.replace("\"", "\\\"")
  return encoded_text

class PiskelHandler(BaseHandler):
  def _authorize(self, piskel):
    if self.is_logged_in:
      is_owner = self.session_user['user_id'] == piskel.owner
      if is_owner:
        return True
    return False

  def _authorize_for_view(self, piskel):
    return self._authorize(piskel) or not piskel.private

  def _authorize_for_clone(self, piskel):
    if piskel.private:
      return self._authorize(piskel)
    else:
      return self.is_logged_in

  def _get_logged_user_id(self):
    if self.is_logged_in:
      user = self.current_user
      user.put()
      return self.session_user['user_id']

  def create(self):
    user_id = self._get_logged_user_id() or _ANONYMOUS_USER
    piskel = Piskel(owner=user_id)
    piskel.garbage = True
    piskel.put()

    self.redirect('/p/'+str(piskel.key()) + '/edit')

  def edit(self, piskel_id):
    piskel = db.get(piskel_id)
    if self._authorize_for_view(piskel):
      framesheet = piskel.get_current_framesheet()
      if framesheet:
        content = framesheet.content
        fps = framesheet.fps
      else:
        content = 'null'
        fps = 12

      values = {
        'user': self.current_user if self.is_logged_in else False,
        'session': self.session_user if self.is_logged_in else False,
        'is_logged_in': self.is_logged_in,
        'piskel_id' : piskel_id,
        'piskel_content' : content,
        'piskel_fps' : fps,
        'piskel': piskel,
        'piskel_name' : encode_for_view_(piskel.name),
        'piskel_description' : encode_for_view_(piskel.description)
      }

      self.render("editor.html", values)
    else:
      self._render_piskel_private()

  def _clone_piskel(self, piskel, user_id):
    clone = Piskel(owner=user_id)
    clone.garbage = False
    clone.name = piskel.name + " clone"
    clone.private = piskel.private
    if piskel.description:
      clone.description = "(copied from original) " + piskel.description
    return clone


  def clone(self, piskel_id, action='view'):
    piskel = db.get(piskel_id)
    valid_for_clone = piskel and piskel.get_current_framesheet()
    if valid_for_clone:
      if self._authorize_for_clone(piskel):
        user_id = self.session_user['user_id']

        clone = self._clone_piskel(piskel, user_id)
        clone.put()
        clone_id = str(clone.key())

        active_framesheet = piskel.get_current_framesheet()
        framesheet = active_framesheet.clone(clone_id)
        clone.set_current_framesheet(framesheet)

        # trigger refresh
        db.get(framesheet.key())

        self.redirect('/p/' + clone_id + '/' + action)
      else:
        self._render_unauthorized_action()
    else:
      self.abort(404)

  def _get_piskel_details(self, piskel):
    framesheets = piskel.get_framesheets()
    return {
      # mandatory
      'user': self.current_user if self.is_logged_in else False,
      'session': self.session_user if self.is_logged_in else False,
      'is_logged_in': self.is_logged_in,
      # page-specific
      'is_author': self.is_logged_in and long(piskel.owner) == self.session_user['user_id'],
      'piskel_id' : piskel.key(),
      'framesheets' : framesheets,
      'piskel': piskel.prepare_for_view(),
      'owner': self.get_user(piskel.owner)
    }

  def get_history(self, piskel_id):
    piskel = db.get(piskel_id)
    if self._authorize(piskel):
      values = self._get_piskel_details(piskel)
      self.render("piskel/piskel-history.html", values)
    else:
      self._render_piskel_private()

  # Clone a previous version/framesheet of a piskel as the current version
  def rollback_piskel_to_framesheet (self, piskel_id, framesheet_id):
    piskel = db.get(piskel_id)
    framesheet = db.get(framesheet_id)
    valid = piskel and framesheet
    if valid:
      if self._authorize(piskel):
        piskel.set_current_framesheet(framesheet.clone(), True)
        self.redirect('/p/' + piskel_id + '/history')

  def view(self, piskel_id):
    piskel = db.get(piskel_id)
    if self._authorize_for_view(piskel):
      values = self._get_piskel_details(piskel)
      self.render("piskel/piskel-details.html", values)
    else:
      self._render_piskel_private()

  # Error page when user tries to view a private piskel
  def _render_piskel_private(self):
    self.render("error/piskel-private.html", {})

  # Error page when user tries to perform an unauthorized action on a piskel
  def _render_unauthorized_action(self):
    # TODO : error page should be different
    # as the piskel is not necessarily private
    self._render_piskel_private()

  def permanently_delete(self, piskel_id):
    piskel = db.get(piskel_id)
    if self._authorize(piskel):
      piskel.delete()
      db.get(piskel_id) # funny looks like this forces
      self.redirect(self.request.get('callback_url'))
    else:
      self._render_unauthorized_action()

  def delete(self, piskel_id):
    self._update_delete_status(piskel_id, True, self.request.get('callback_url'))

  def restore(self, piskel_id):
    self._update_delete_status(piskel_id, False, self.request.get('callback_url'))

  def _update_delete_status(self, piskel_id, status, redirect_url):
    piskel = db.get(piskel_id)
    if self._authorize(piskel):
      piskel.deleted = status
      piskel.put()

      # force consistency
      db.get(piskel_id)

      self.redirect(redirect_url)
    else:
      self._render_unauthorized_action()

  def updateinfo(self, piskel_id):
    piskel = db.get(piskel_id)
    if self._authorize(piskel):
      post_data = self.request.POST
      piskel.name = post_data.get('name')
      piskel.description = post_data.get('description')
      piskel.private = not bool(post_data.get('public'))
      piskel.put()

      # consistency will be forced by get made on view(self)
      self.redirect('/p/' + piskel_id + '/view')
    else:
      self._render_unauthorized_action()

  # Save a new framesheet on an existing piskel
  def save(self, piskel_id):
    piskel = db.get(piskel_id)

    # Claim anonymous piskel ownership
    is_anonymous = _ANONYMOUS_USER == piskel.owner
    if is_anonymous:
      piskel.owner =  self._get_logged_user_id()

    if self._authorize(piskel):
      post_data = self.request.POST

      content = post_data.get('framesheet')
      fps = post_data.get('fps')
      frames = long(post_data.get('frames'))

      preview_link=image_handler.create_link(post_data.get('first_frame_as_png'))
      framesheet_link=image_handler.create_link(post_data.get('framesheet_as_png'))

      if hasFramesheetChanged_(piskel, content, fps):
        framesheet = Framesheet(
          piskel_id=piskel_id,
          fps=fps,
          content=content,
          frames=frames,
          preview_link=preview_link,
          framesheet_link=framesheet_link,
          active=True
        )
        piskel.set_current_framesheet(framesheet)

      piskel.name = post_data.get('name')
      piskel.description = post_data.get('description')

      piskel.private = not bool(post_data.get('public'))

      piskel.garbage = False # remove garbage flag to avoid collection by CRON task + enable listing
      piskel.put()

      # force consistency
      db.get(piskel_id)

      self.response.out.write(piskel.key())
    else:
      self.abort(403)


