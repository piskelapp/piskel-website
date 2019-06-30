from google.appengine.ext import db


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
