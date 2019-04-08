import os

import cherrypy

from model import properties
from view.api import Api
from view.pages import Pages


def launch_web_server():
    # global configuration
    cherrypy.config.update({'global': {
        'tools.sessions.on': True,
        'tools.sessions.timeout': 60 * properties.WEB_SESSION_TIMEOUT,
        'engine.autoreload.on': False}})

    # Configure the server object
    cherrypy.server.socket_host = properties.WEB_SOCKET_IP
    cherrypy.server.socket_port = properties.WEB_SOCKET_PORT
    cherrypy.server.thread_pool = properties.CHERRYPY_MAX_THREAD_POOL

    conf_pages = {
        '/': {
            'tools.staticdir.root': os.path.join(properties.PROJECT_ROOT, "view", "includes")
        },
        '/includes': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './includes'
        },
        "/favicon.ico": {
            "tools.staticfile.on": True,
            "tools.staticfile.filename": "/includes/images/favicon.ico"
        }
    }
    conf_api = {
        '/': {
            'tools.staticdir.root': False
        }
    }

    # mount application
    cherrypy.tree.mount(Pages(), "/", conf_pages)
    cherrypy.tree.mount(Api(), "/api/", conf_api)

    # Start the server engine
    cherrypy.engine.start()
    cherrypy.engine.block()
