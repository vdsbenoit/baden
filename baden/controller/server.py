import os

import cherrypy

from controller.api import Api
from model import properties
from view.pages import UserPages, AdminPages


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
    if properties.SLL_CERTIFICATE:
        cherrypy.server.sll_module = "builtin"
        cherrypy.server.ssl_certificate = os.path.join(properties.PROJECT_ROOT, properties.SLL_CERTIFICATE)
        cherrypy.server.ssl_private_key = os.path.join(properties.PROJECT_ROOT, properties.SSL_KEY)

    static_root_dir = os.path.join(properties.PROJECT_ROOT, "view")
    conf_pages = {
        '/': {
            'tools.staticdir.root': static_root_dir,
            'tools.staticfile.root': static_root_dir
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static'
        },
        "/favicon.ico": {
            "tools.staticfile.on": True,
            "tools.staticfile.filename": "static/images/favicon/favicon.ico"
        }
    }
    conf_api = {
        '/': {
            'tools.staticdir.root': False
        }
    }

    # mount application
    cherrypy.tree.mount(UserPages(), "/", conf_pages)
    cherrypy.tree.mount(AdminPages(), "/admin/", conf_pages)
    cherrypy.tree.mount(Api(), "/api/", conf_api)

    # Start the server engine
    cherrypy.engine.start()
    cherrypy.engine.block()
