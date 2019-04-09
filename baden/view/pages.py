import logging
from os.path import join

import cherrypy

from model import properties
from model.helloworld import Hello

HTML_DIR = join(properties.PROJECT_ROOT, "view", "html")

log = logging.getLogger('default')


class Pages:
    @cherrypy.expose
    def index(self):
        return Hello.objects().first().world


    # @cherrypy.expose
    # def index(self):
    #     return open(join(HTML_DIR, "index.html"), 'r').read()


