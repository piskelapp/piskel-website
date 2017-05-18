from google.appengine.ext import db


class UserDetails(db.Model):
    user_id = db.IntegerProperty()
    name = db.StringProperty()
    localisation = db.StringProperty()
    avatar_url = db.StringProperty()
    admin = db.BooleanProperty(default=False)


def get_by_userid(user_id):
    q = db.GqlQuery('SELECT * FROM UserDetails WHERE user_id = :1', long(user_id))
    userdetails = q.get()
    if not userdetails:
        userdetails = UserDetails(user_id=user_id)
        userdetails.put()

    return userdetails


# Merge the user details and user object
def get_user_for_view(user):
    details = get_by_userid(user.key.id())
    view_user = {
        'name': details.name or user.name,
        'localisation': details.localisation,
        'avatar_url': details.avatar_url or user.avatar_url,
        'admin': details.admin,
    }
    return view_user
