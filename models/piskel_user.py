from webapp2_extras.appengine.auth.models import User as Webapp2User
from google.appengine.ext import ndb

class User(Webapp2User):
    is_admin = ndb.BooleanProperty(default=False)
    is_searchable = ndb.BooleanProperty(default=False)