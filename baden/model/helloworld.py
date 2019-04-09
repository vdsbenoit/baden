from mongoengine import *

import logging

from model import properties

log = logging.getLogger('default')


class Hello(Document):
    world = StringField(required=True)
