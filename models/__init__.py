from google.appengine.ext import db
from google.appengine.api import memcache
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


def get_framesheet_fps(framesheet):
    try:
        return float(framesheet.fps)
    except:
        # FPS might be undefined. In this case return 0 and fixup the model
        framesheet.fps = "0"
        framesheet.put()
        return 0


def get_stats_for_piskel(piskel):
    mem_key = 'piskel_stats_' + str(piskel.key())
    stat = memcache.get(mem_key)
    if stat:
        return stat

    framesheet = piskel.get_current_framesheet()
    if framesheet:
        frames_count = long(framesheet.frames)
        fps = get_framesheet_fps(framesheet)

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
