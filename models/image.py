import logging
import uuid
import base64
import pickle

from google.appengine.api import memcache
from google.appengine.ext import db


class Image(db.Model):
    content = db.BlobProperty(default=None)
    extension = db.StringProperty(default='png')


class ImageInfo(db.Model):
    pass


def store_image(image_data, extension):
    file_name = str(uuid.uuid1()) + '.' + extension
    image = Image(key_name=file_name)
    image.content = db.Blob(base64.decodestring(image_data))
    image.extension = extension
    image.put()

    image_info = ImageInfo(key_name=file_name)
    image_info.put()

    return image


def get_image(file_name):
    image = memcache.get(file_name)
    if not image:
        image = Image.get_by_key_name(file_name)
        memcache.set(file_name, image)

    return image