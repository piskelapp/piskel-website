from google.appengine.ext import db
from google.appengine.api import memcache
import urllib
from time import gmtime, strftime

BUCKET_SIZE = 100
MAX_BUCKETS = 100
CATEGORIES = ['all', 'public', 'private', 'deleted']


def _clear_get_piskels_cache(user_id):
    keys = []
    # Piskels are retrieved by buckets and each bucket is memcached independently to avoid
    # exceeding the memcache size limit.
    # We can not really store the used memcache keys here, so instead we aggressively clear caches
    # for the first 100 buckets for each category.
    for cat in CATEGORIES:
        for offset in range(0, MAX_BUCKETS):
            keys.append(cat + '_' + str(offset * BUCKET_SIZE))

    memcache.delete_multi(keys, key_prefix='user_piskels_' + str(user_id) + '_' + str(BUCKET_SIZE) + '_')


def get_query(cat):
    if cat == 'all':
        return 'SELECT * FROM Piskel WHERE owner = :1 and garbage=False and deleted=False ORDER BY creation_date DESC'
    if cat == 'public':
        return 'SELECT * FROM Piskel WHERE owner = :1 and garbage=False and private=False and deleted=False ORDER BY creation_date DESC'
    if cat == 'private':
        return 'SELECT * FROM Piskel WHERE owner = :1 and garbage=False and private=True and deleted=False ORDER BY creation_date DESC'
    if cat == 'deleted':
        return 'SELECT * FROM Piskel WHERE owner = :1 and garbage=False and deleted=True ORDER BY creation_date DESC'


def get_piskels(user_id, cat, offset, limit):
    piskels = None
    mem_key = None

    # only memcache if the query respects the current default bucket size
    if limit == BUCKET_SIZE and (offset % BUCKET_SIZE) == 0:
        mem_key = 'user_piskels_' + str(user_id) + '_' + str(BUCKET_SIZE) + '_' + cat + '_' + str(offset)
        piskels = memcache.get(mem_key)

    if not piskels:
        q = db.GqlQuery(get_query(cat), long(user_id))
        piskels = q.fetch(offset=offset, limit=limit)
        if mem_key:
            memcache.set(mem_key, piskels)

    return piskels


def get_recent_piskels(index):
    mem_key = 'recent_piskels_' + str(index) + '_' + strftime('%Y%m%d%H', gmtime())
    piskels = memcache.get(mem_key)
    if not piskels:
        q = db.GqlQuery('SELECT * FROM Piskel WHERE garbage=False and private=False and deleted=False ORDER BY creation_date DESC')
        piskels = q.fetch(offset=(index-1)*20, limit=20)
        memcache.set(mem_key, piskels)
    return piskels


def get_piskels_for_user(user_id):
    offset = 0

    piskels = []
    while True:
        bucket = get_piskels(user_id, 'all', offset, BUCKET_SIZE)
        if len(bucket) == 0:
            break
        piskels += bucket
        offset += BUCKET_SIZE

    return piskels


def invalidate_user_cache(user_id):
    memcache.delete('user_piskels_' + str(user_id))
    memcache.delete('user_stats_' + str(user_id))
    _clear_get_piskels_cache(user_id)


def get_stats_for_piskel(piskel):
    mem_key = 'piskel_stats_' + str(piskel.key())
    stat = memcache.get(mem_key)
    if stat:
        return stat

    framesheet = piskel.get_current_framesheet()
    if framesheet:
        frames_count = long(framesheet.frames)
        fps = float(framesheet.fps)
        if fps > 0:
            anim_length = float(frames_count) * (1/float(fps))
        else:
            anim_length = 0

        stat = {
            'frames_count': frames_count,
            'anim_length': anim_length
        }
        memcache.set(mem_key, stat)
        return stat
    else:
        return None


def get_stats_for_user(user_id):
    mem_key = 'user_stats_' + str(user_id)
    stat = memcache.get(mem_key)
    if stat:
        return stat

    frames_count = 0
    anim_length = 0
    piskels = get_piskels_for_user(user_id)
    for piskel in piskels:
        piskel_stats = get_stats_for_piskel(piskel)
        if piskel_stats:
            frames_count = frames_count + long(piskel_stats['frames_count'])
            anim_length = anim_length + float(piskel_stats['anim_length'])

    stat = {
        'piskels_count': len(piskels),
        'frames_count': frames_count,
        'anim_length': '{:10.2f}'.format(anim_length)
    }
    memcache.set(mem_key, stat)
    return stat


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
        invalidate_user_cache(self.owner)
        if self.is_saved():
            memcache.delete('piskel_json_' + str(self.key()))
        return db.Model.put(self)

    #override
    def delete(self):
        invalidate_user_cache(self.owner)
        return db.Model.delete(self)

    def set_current_framesheet(self, framesheet, force_consistency=False):
        memcache.delete('image_piskel_' + str(self.key()))
        memcache.delete('piskel_json_' + str(self.key()))
        memcache.delete('user_stats_' + str(self.owner))

        current = self.get_current_framesheet()
        if current:
            current.active = False
            current.put()

        framesheet.active = True
        framesheet.put()

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
            piskel_id=piskel_id if piskel_id else self.piskel_id,
            fps=self.fps,
            content=self.content,
            frames=self.frames,
            preview_link=self.preview_link,
            framesheet_link=self.framesheet_link
        )
