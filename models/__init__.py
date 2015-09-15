from google.appengine.ext import db
from google.appengine.api import memcache
import urllib
from time import gmtime, strftime

def _get_all_piskels_for_user(user_id, limit=20):
  mem_key = "user_piskels_" + str(user_id)
  piskels = memcache.get(mem_key)
  if not piskels:
    q = db.GqlQuery("SELECT * FROM Piskel WHERE owner = :1 ORDER BY creation_date DESC", long(user_id))
    piskels = q.fetch(limit=None)
    memcache.set(mem_key, piskels)
  return [p for p in piskels if not p.garbage]


def get_recent_piskels(index):
  mem_key = "recent_piskels_" + str(index) + "_" + strftime("%Y%m%d%H", gmtime());
  piskels = memcache.get(mem_key)
  if not piskels:
    q = db.GqlQuery("SELECT * FROM Piskel WHERE garbage=False and private=False and deleted=False ORDER BY creation_date DESC")
    piskels = q.fetch(offset=(index-1)*20, limit=20)
    memcache.set(mem_key, piskels)
  return piskels


def get_public_piskels_count():
  return 10000


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
  memcache.delete("user_piskels_" + str(user_id))
  memcache.delete("user_stats_" + str(user_id))


def get_stats_for_user(user_id):
  mem_key = "user_stats_" + str(user_id)
  stat = memcache.get(mem_key)
  if stat:
    return stat

  frames_count = 0
  anim_length = 0
  piskels = get_piskels_for_user(user_id, None)
  for piskel in piskels:
    framesheet = piskel.get_current_framesheet()
    if framesheet:
      frames_count = frames_count + long(framesheet.frames)
      fps = float(framesheet.fps)
      if fps > 0:
        anim_length = anim_length + float(framesheet.frames) * (1/float(framesheet.fps))
  stat = {
    'piskels_count' : len(piskels),
    'frames_count' : frames_count,
    'anim_length' : "{:10.2f}".format(anim_length)
  }
  memcache.set(mem_key, stat)
  return stat

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
    if self.is_saved():
      memcache.delete("current_view_piskel_" + str(self.key()))
    return db.Model.put(self)

  #override
  def delete(self):
    invalidate_user_cache(self.owner)
    return db.Model.delete(self)

  def set_current_framesheet(self, framesheet, force_consistency=False):
    memcache.delete("image_piskel_" + str(self.key()))
    memcache.delete("current_view_piskel_" + str(self.key()))
    memcache.delete("user_stats_" + str(self.owner))

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
    mem_key = "current_view_piskel_" + str(self.key())
    if memcache.get(mem_key) :
      return memcache.get(mem_key)

    framesheet = self.get_current_framesheet()
    if framesheet:
      url = 'http://www.piskelapp.com/img/' + framesheet.preview_link
      resize_service_url = 'http://piskel-resizer.appspot.com/resize?size=200&url='
      view = {
        'key' : self.key(),
        'fps' : framesheet.fps,
        'framesheet_key' : framesheet.key(),
        'preview_url' : resize_service_url + urllib.quote(url, '&'),
        'frames' : framesheet.frames,
        'name' : self.name,
        'description' : self.description if self.description else None,
        'private' : self.private,
        'deleted' : self.deleted,
        'date' : self.creation_date.strftime("%A, %d. %B %Y %I:%M%p")
      }
      memcache.set(mem_key, view)
      return view
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
