from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users
import logging

def _get_all_piskels_for_user(user_id, limit=20):
  mem_key = "user_piskels_" + str(user_id)
  piskels = memcache.get(mem_key)
  if not piskels:
    q = db.GqlQuery("SELECT * FROM Piskel WHERE owner = :1 ORDER BY creation_date DESC", long(user_id))
    piskels = q.fetch(limit=None)
    memcache.set(mem_key, piskels)
  return [p for p in piskels if not p.garbage]

def get_piskels_for_user(user_id, limit=20):
  piskels = _get_all_piskels_for_user(user_id, limit)
  return [p for p in piskels if not p.deleted]

def get_public_piskels_for_user(user_id, limit=20):
  piskels = get_piskels_for_user(user_id, limit)
  return [p for p in piskels if not p.private and not p.deleted]

def get_private_piskels_for_user(user_id, limit=20):
  piskels = get_piskels_for_user(user_id, limit)
  return [p for p in piskels if p.private and not p.deleted]

def get_deleted_piskels_for_user(user_id, limit=20):
  piskels = _get_all_piskels_for_user(user_id, limit)
  return [p for p in piskels if p.deleted]

def invalidate_user_cache(user_id):
  mem_key = "user_piskels_" + str(user_id)
  memcache.delete(mem_key)

def get_stats_for_user(user_id):
  frames_count = 0
  anim_length = 0
  piskels = get_piskels_for_user(user_id, None)
  for piskel in piskels:
    framesheet = piskel.get_current_framesheet()
    if framesheet:
      frames_count = frames_count + long(framesheet.frames)
      anim_length = anim_length + float(framesheet.frames) * (1/float(framesheet.fps))
  return {
    'piskels_count' : len(piskels),
    'frames_count' : frames_count,
    'anim_length' : "{:10.2f}".format(anim_length)
  }

class Piskel(db.Model):
  owner = db.IntegerProperty()
  creation_date = db.DateTimeProperty(auto_now_add=True)
  private = db.BooleanProperty(default=False)
  deleted = db.BooleanProperty(default=False)
  garbage = db.BooleanProperty(default=False)
  name = db.StringProperty(required=True, default="New piskel")
  description = db.TextProperty()

  #override
  def put(self):
    invalidate_user_cache(self.owner)
    return db.Model.put(self)

  #override
  def delete(self):
    invalidate_user_cache(self.owner)
    return db.Model.delete(self)

  def set_current_framesheet(self, framesheet, force_consistency=False):
    current = self.get_current_framesheet()
    if current:
      current.active = False
      current.put()
    
    framesheet.active =True
    framesheet.put()

    if force_consistency:
      db.get(current.key())
      db.get(framesheet.key())
      db.get(self.key())

  def get_current_framesheet(self):
    q = db.GqlQuery("SELECT * FROM Framesheet WHERE piskel_id = :1 AND active=true", str(self.key()))
    return q.get()

  def get_framesheets(self):
    q = db.GqlQuery("SELECT * FROM Framesheet WHERE piskel_id = :1 ORDER BY date DESC", str(self.key()))
    return q.fetch(None)

  # @return an object {key, fps, frames, preview_link, name, date} or None if the piskel has no framesheet 
  def prepare_for_view(self):
    framesheet = self.get_current_framesheet()
    if framesheet:
      return {
        'key' : self.key(),
        'fps' : framesheet.fps,
        'framesheet_key' : framesheet.key(),
        'frames' : framesheet.frames,
        'name' : self.name,
        'description' : self.description if self.description else None,
        'private' : self.private,
        'deleted' : self.deleted,
        'date' : self.creation_date.strftime("%A, %d. %B %Y %I:%M%p")
      }
    else:
      return None

  @classmethod
  def prepare_piskels_for_view(cls, piskels):
    view_piskels = []
    for piskel in piskels:
      piskel_v = piskel.prepare_for_view()
      if piskel_v != None:
        view_piskels.append(piskel_v)
    return view_piskels

class Framesheet(db.Model):
  """Models a framesheet entry containing only content."""
  content = db.TextProperty()
  fps = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  # piskel = db.ReferenceProperty(Piskel, collection_name='versions')
  piskel_id = db.StringProperty()
  active = db.BooleanProperty()
  frames = db.IntegerProperty()
  preview_link = db.StringProperty()
  framesheet_link = db.StringProperty()

  def clone(self, piskel_id=None): 
    return Framesheet(
      piskel_id= piskel_id if piskel_id else self.piskel_id, 
      fps=self.fps, 
      content=self.content, 
      frames=self.frames, 
      preview_link=self.preview_link, 
      framesheet_link=self.framesheet_link
    )
