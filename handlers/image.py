import re, logging
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import webapp

from models import image as image_model

def respond_image(db_image, response):
    file_name = db_image.key().name()

    response.headers['Expires'] = 'Thu, 01 Dec 2504 16:00:00 GMT'
    response.headers['Content-Type'] = str('image/'+db_image.extension)

    # Cache-Control
    # public means the cached version can be saved by proxies and other intermediate servers, where everyone can see it
    response.headers['Cache-Control'] = 'public, max-age= 31536000' # 1 year in second (about infinity on Internet Time)
    response.headers['X-Image-Name'] = str(file_name)
    response.out.write(db_image.content)

def match_extension(data):
    return re.search('data:image/(\w+);base64', data)

def validate_data(data):
    return match_extension(data) is not None

def get_extension(data):
    return match_extension(data).group(1)

def create_link(data):
    image = store_image_from_data(data)
    return image.key().name()

def store_image_from_data(data):
    # prepare extension and image data
    extension = get_extension(data)
    image_data = str.replace(str(data), 'data:image/'+extension+';base64', '')
    return image_model.store_image(image_data, extension)

class UploadSingleImage(webapp.RequestHandler):
    def post(self):
        data = self.request.get('data')
        if validate_data(data):
            image = store_image_from_data(data)
            if image:
                self.response.out.write(image.key().name())
            else:
                self.response.out.write('Sorry, could not add image. Image is probably too big')
        else:
            self.response.out.write("Unexpected data argument. data should start with 'data:image/[ext];base64'")


class GetImageHandler(webapp.RequestHandler):
    def get(self, image_name):
        image = image_model.get_image(image_name)
        if image:
            respond_image(image, self.response)
        else:
            self.response.out.write('Sorry, could not find image.')

    def get_framesheet_preview(self, framesheet_id):
        mem_key = 'image_preview_' + str(framesheet_id)
        link = memcache.get(mem_key)
        if link:
            self.get(link)
        else:
            framesheet = db.get(framesheet_id)
            if framesheet:
                memcache.set(mem_key, framesheet.preview_link)
                self.get(framesheet.preview_link)
            else:
                self.response.out.write('Sorry, could not find image.')

    def get_framesheet(self, framesheet_id):
        mem_key = 'image_framesheet_' + str(framesheet_id)
        link = memcache.get(mem_key)
        if link:
            self.get(link)
        else:
            framesheet = db.get(framesheet_id)
            if framesheet:
                framesheet_link = framesheet.framesheet_link
                if framesheet_link:
                    memcache.set(mem_key, framesheet_link)
                    self.get(framesheet_link)
                else:
                    # fallback on preview_link if framesheet_link not generated yet
                    # only needed for backward compatibility of entities, all framesheets now should have a preview link
                    self.get(framesheet.preview_link)
            else:
                self.response.out.write('Sorry, could not find image.')

    def get_piskel_sprite(self, piskel_id):
        piskel = db.get(piskel_id)
        mem_key = 'image_piskel_' + str(piskel_id)
        if memcache.get(mem_key):
            self.get(memcache.get(mem_key))
        else:
            if piskel:
                framesheet = piskel.get_current_framesheet()
                if framesheet and framesheet.framesheet_link:
                    memcache.set(mem_key, framesheet.framesheet_link)
                    self.get(framesheet.framesheet_link)
                    return
        self.response.out.write('Sorry, could not find image.')
