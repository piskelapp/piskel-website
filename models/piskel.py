from google.appengine.ext import db
from google.appengine.api import memcache


import urllib
import models


class Piskel(db.Model):
    owner = db.IntegerProperty()
    creation_date = db.DateTimeProperty(auto_now_add=True)
    private = db.BooleanProperty(default=False)
    deleted = db.BooleanProperty(default=False)
    garbage = db.BooleanProperty(default=False)
    name = db.StringProperty(required=True, default='New piskel')
    description = db.TextProperty()

    #override
    def put(self):
        models.invalidate_user_cache(self.owner)
        if self.is_saved():
            memcache.delete('piskel_json_' + str(self.key()))
        return db.Model.put(self)

    #override
    def delete(self):
        models.invalidate_user_cache(self.owner)
        return db.Model.delete(self)

    def set_current_framesheet(self, framesheet, force_consistency=False):
        memcache.delete('image_piskel_' + str(self.key()))
        memcache.delete('piskel_json_' + str(self.key()))
        memcache.delete('user_stats_' + str(self.owner))

        current = self.get_current_framesheet()

        framesheet.active = True
        framesheet.put()

        # Only flip current.active if framesheet put completed successfully.
        if current:
            current.active = False
            current.put()

        if force_consistency:
            db.get(current.key())
            db.get(framesheet.key())
            db.get(self.key())

    def get_current_framesheet(self):
        q = db.GqlQuery('SELECT * FROM Framesheet WHERE piskel_id = :1 AND active=true', str(self.key()))
        return q.get()

    def get_framesheets(self):
        q = db.GqlQuery('SELECT * FROM Framesheet WHERE piskel_id = :1 ORDER BY date DESC', str(self.key()))
        return q.fetch(None)

    # @return an object {key, fps, frames, preview_link, name, date} or None if the piskel has no framesheet
    def prepare_for_view(self):
        mem_key = 'piskel_json_' + str(self.key())
        if memcache.get(mem_key):
            return memcache.get(mem_key)

        framesheet = self.get_current_framesheet()
        if framesheet:
            url = 'http://www.piskelapp.com/img/' + framesheet.preview_link
            resize_service_url = 'http://piskel-resizer.appspot.com/resize?size=200&url='
            view = {
                'key': str(self.key()),
                'fps': framesheet.fps,
                'framesheet_key': str(framesheet.key()),
                'preview_url': resize_service_url + urllib.quote(url, '&'),
                'frames': framesheet.frames,
                'name': self.name,
                'description': self.description if self.description else None,
                'private': self.private,
                'deleted': self.deleted,
                'date': self.creation_date.strftime('%A, %d. %B %Y %I:%M%p')
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
            if piskel_v is not None:
                view_piskels.append(piskel_v)
        return view_piskels
