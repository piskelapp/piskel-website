from google.appengine.ext import db


class UserDetails(db.Model):
    user_id = db.IntegerProperty()
    admin = db.BooleanProperty(default=False)


def get_by_userid(user_id):
    q = db.GqlQuery('SELECT * FROM UserDetails WHERE user_id = :1', long(user_id))
    userdetails = q.get()
    if not userdetails:
        userdetails = UserDetails(user_id=user_id)
        userdetails.put()

    return userdetails
