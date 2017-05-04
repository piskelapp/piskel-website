from base import BaseHandler
import models
import json


# Handler dedicated to return stat information for a user as json
class UserStatsHandler(BaseHandler):
    def get(self, user_id):
        user = self.auth.store.user_model.get_by_id(long(user_id))
        if user:
            stats = models.get_stats_for_user(user_id)
            self.response.headers['Content-Type'] = 'application/json'
            # Set cache control to 10 minutes
            self.response.headers['Cache-Control'] = 'public, max-age=600'
            obj = {
                'piskelsCount': int(stats['piskels_count']),
                'framesCount': int(stats['frames_count']),
                'animationDuration': float(stats['anim_length']),
            }
            self.response.out.write(json.dumps(obj))
