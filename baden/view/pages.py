# -*-coding:UTF-8 -*

import logging
from os.path import join

import cherrypy

from model import properties
from model.helloworld import Hello

HTML_DIR = join(properties.PROJECT_ROOT, "view", "html")

log = logging.getLogger('default')


class Pages:
    leader_password = ""
    admin_password = ""

    @cherrypy.expose
    def index(self):
        return Hello.objects().first().world

    @cherrypy.expose
    def home(self):
        return open(join(HTML_DIR, "index.html"), 'r').read()

    @cherrypy.expose
    def leader(self, password=""):
        login_page = open(join(HTML_DIR, "login.html"), 'r').read()
        login_page = login_page.replace("{target-page}", "./leader")
        if self.is_brute_force_attack():
            return login_page.replace(
                'id="attack" style="display:none;"',
                'id="attack"'
            )
        if password != self.leader_password:
            self.add_login_attempt()
            login_page = login_page.replace(
                'id="wrong-password" style="display:none;"',
                'id="wrong-password"'
            )
        if cherrypy.session.get('logged'):
            return open(join(HTML_DIR, "leader.html"), 'r').read()
        else:
            return login_page

    @cherrypy.expose
    def admin(self, password=""):
        login_page = open(join(HTML_DIR, "login.html"), 'r').read()
        login_page = login_page.replace("{target-page}", "./admin")
        if self.is_brute_force_attack():
            return login_page.replace(
                'id="attack" style="display:none;"',
                'id="attack"'
            )
        if password != self.admin_password:
            self.add_login_attempt()
            login_page = login_page.replace(
                'id="wrong-password" style="display:none;"',
                'id="wrong-password"'
            )
        if not cherrypy.session.get('admin_logged'):
            return open(join(HTML_DIR, "admin.html"), 'r').read()
        else:
            return login_page

    @cherrypy.expose
    def setup(self, admin="", leader=""):
        if admin:
            self.admin_password = admin
        if leader:
            self.leader_password = leader
        if self.leader_password and self.admin_password:
            return "Server is already set up."
        else:
            return open(join(HTML_DIR, "setup.html"), 'r').read()

    @cherrypy.expose
    def log(self):
        return open(join(properties.PROJECT_ROOT, "activity.log"), 'r').read()

    @staticmethod
    def add_login_attempt():
        if cherrypy.session.get('failed_login_count'):
            cherrypy.session["failed_login_count"] += 1
        else:
            cherrypy.session["failed_login_count"] = 1

    @staticmethod
    def is_brute_force_attack():
        if cherrypy.session.get('failed_login_count') > 15:
            log.warning("IP {} tried to brute force the password".format(str(cherrypy.request.remote.ip))) 
            return True
        else:
            return False

