from mongoengine import *
from model import properties


def setup_db():
    connect(properties.DB_NAME, host=properties.DB_HOST, port=properties.DB_PORT)

