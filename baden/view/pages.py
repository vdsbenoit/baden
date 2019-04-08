import logging
from os.path import join

import cherrypy

from model import properties

HTML_DIR = join(properties.PROJECT_ROOT, "view", "html")

log = logging.getLogger('default')


class Pages:
    @cherrypy.expose
    def index(self):
        return open(join(HTML_DIR, "index.html"), 'r').read()


