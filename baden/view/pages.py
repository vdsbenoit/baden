# -*-coding:UTF-8 -*

import logging
from os.path import join

import cherrypy

from model import properties
from model import service
from model.helloworld import Hello

HTML_DIR = join(properties.PROJECT_ROOT, "view", "html")

log = logging.getLogger('default')


def get_html(page_name):
    """
    Concatenate the html header, body and footer
    :param page_name: name of the page html file
    :return: concatenated html string
    """
    res = open(join(HTML_DIR, "header.html"), 'r').read()
    res += open(join(HTML_DIR, page_name), 'r').read()
    res += open(join(HTML_DIR, "footer.html"), 'r').read()
    return res


class Pages:
    leader_password = ""
    admin_password = ""

    @cherrypy.expose
    def index(self):
        return Hello.objects().first().world

    @cherrypy.expose
    def home(self):
        return get_html("home.html")

    @cherrypy.expose
    def player(self, teamcode=None):
        page = get_html("player.html")
        if teamcode:
            cherrypy.session['player_teamcode'] = teamcode
        else:
            teamcode = cherrypy.session.get('player_teamcode', None)
        if teamcode:
            page = page.replace("{teamcode}", teamcode)
            page = page.replace("{section-name}", str(service.get_section(teamcode)))
            page = page.replace("{section-score}", str(service.get_section_score(teamcode)))
            page = page.replace("{team-score}", str(service.get_score(teamcode)))
            page = page.replace('id="scores" style="display:none;"', 'id="scores"')
        else:
            page = page.replace("{teamcode}", "")

        return page

    @cherrypy.expose
    def leader(self, password=None):
        login_page = get_html("login.html")
        login_page = login_page.replace("{target-page}", "./leader")
        if self.is_brute_force_attack():
            return login_page.replace(
                'id="attack" style="display:none;"',
                'id="attack"'
            )
        if password:
            if password == self.leader_password:
                cherrypy.session['logged'] = True
            else:
                self.add_login_attempt()
                login_page = login_page.replace(
                    'id="wrong-password" style="display:none;"',
                    'id="wrong-password"'
                )
        if cherrypy.session.get('logged'):
            return get_html("leader.html")
        else:
            return login_page

    @cherrypy.expose
    def admin(self, password=None):
        login_page = get_html("login.html")
        login_page = login_page.replace("{target-page}", "./admin")
        if self.is_brute_force_attack():
            return login_page.replace(
                'id="attack" style="display:none;"',
                'id="attack"'
            )
        if password:
            if password == self.admin_password:
                cherrypy.session['admin_logged'] = True
            else:
                self.add_login_attempt()
                login_page = login_page.replace(
                    'id="wrong-password" style="display:none;"',
                    'id="wrong-password"'
                )
        if not cherrypy.session.get('admin_logged'):
            return get_html("admin.html")
        else:
            return login_page

    @cherrypy.expose
    def setup(self, adminpwd=None, userpwd=None):
        if adminpwd and userpwd:
            self.admin_password = adminpwd
            self.leader_password = userpwd
        if self.leader_password and self.admin_password:
            return "Server is set up."
        else:
            return get_html("setup.html").replace("{target-page}", "./setup")

    @cherrypy.expose
    def log(self):
        log_content = open(join(properties.PROJECT_ROOT, "activity.log"), 'r').read()
        log_content = log_content.replace('\n', "<br/>")
        return log_content

    @staticmethod
    def add_login_attempt():
        if cherrypy.session.get('failed_login_count'):
            cherrypy.session["failed_login_count"] += 1
        else:
            cherrypy.session["failed_login_count"] = 1

    @staticmethod
    def is_brute_force_attack():
        if cherrypy.session.get('failed_login_count') and cherrypy.session.get('failed_login_count') > 15:
            log.warning("IP {} tried to brute force the password".format(str(cherrypy.request.remote.ip))) 
            return True
        else:
            return False

