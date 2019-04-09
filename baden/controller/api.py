import logging

import cherrypy

log = logging.getLogger('default')


class Api:
    @cherrypy.expose
    def foo(self):
        pass



