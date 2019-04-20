# -*-coding:UTF-8 -*

import logging
from os.path import join

import cherrypy
from mongoengine import DoesNotExist

from model import properties
from model import service, team, game
from model.helloworld import Hello
from view import html_util as html

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


def add_login_attempt():
    if cherrypy.session.get('failed_login_count'):
        cherrypy.session["failed_login_count"] += 1
    else:
        cherrypy.session["failed_login_count"] = 1


def is_brute_force_attack():
    if cherrypy.session.get('failed_login_count') and cherrypy.session.get('failed_login_count') > 15:
        log.warning("IP {} tried to brute force the password".format(str(cherrypy.request.remote.ip))) 
        return True
    else:
        return False


class UserPages:
    leader_password = ""

    def request_login(self, origin, password):
        login_page = get_html("login.html")
        login_page = login_page.replace("{target-page}", "/{}".format(origin))
        if is_brute_force_attack():
            return login_page.replace(
                'id="attack" style="display:none;"',
                'id="attack"'
            )
        if password:
            if password == self.leader_password:
                cherrypy.session['logged'] = True
            else:
                add_login_attempt()
                login_page = login_page.replace(
                    'id="wrong-password" style="display:none;"',
                    'id="wrong-password"'
                )
        if cherrypy.session.get('logged'):
            return None
        else:
            return login_page

    @cherrypy.expose
    def index(self):
        return Hello.objects().first().world

    @cherrypy.expose
    def home(self):
        if self.leader_password and AdminPages.admin_password:
            return get_html("home.html")
        else:
            return self.setup()  # fixme: remove before deploy

    @cherrypy.expose
    def player(self, team_code=None):
        page = get_html("player.html")
        if team_code:
            if not service.is_team(team_code):
                page = page.replace("{teamcode}", team_code)
                return page.replace('id="wrong-teamcode" style="display:none;"', 'id="wrong-teamcode"')
            cherrypy.session['player_teamcode'] = team_code
        else:
            team_code = cherrypy.session.get('player_teamcode', None)
        if team_code:
            log.info("Team {} checked its score".format(team_code))
            page = page.replace("{teamcode}", team_code)
            page = page.replace("{section-name}", service.get_section(team_code))
            page = page.replace("{section-score}", str(round(service.get_team_section_score(team_code), 2)))
            page = page.replace("{team-score}", str(service.get_score(team_code)[0]))
            page = page.replace('id="scores" style="display:none;"', 'id="scores"')
        else:
            page = page.replace("{teamcode}", "")

        return page

    @cherrypy.expose
    def leader(self, password=None, team1_code=None, team2_code=None, game_number=None, winner=None, confirmed=None):
        login_page = self.request_login("leader", password)
        if login_page:
            return login_page

        page = get_html("leader.html")
        notification = ""
        if team1_code and team2_code and game_number:
            if confirmed:
                cherrypy.session['game_number'] = game_number
                try:
                    service.set_winner(int(game_number), team1_code, team2_code)
                    notification = 'Le score a bien &eacute;t&eacute; enregistr&eacute;'
                except Exception:
                    log.exception("Something bad occurred while an user tried to set a score")
                    notification = "Le score n'a pas pu &ecirc;tre enregistr&eacute;"
            else:
                page = get_html("confirm_score.html")
                page = page.replace('{game_number}', str(game_number))
                page = page.replace('{team1_code}', team1_code)
                page = page.replace('{team2_code}', team2_code)
                if winner == "even":
                    page = page.replace('{team1_title}', "Team 1")
                    page = page.replace('{team2_title}', "Team 2")
                    page = page.replace('id="equally-scored" style="display: none;"', 'id="equally-scored"')
                else:
                    page = page.replace('{team1_title}', "Gagnant")
                    page = page.replace('{team2_title}', "Perdant")
                try:
                    game_info = service.get_game_info(game_number=game_number, team_code=team1_code)
                    page = page.replace("{time}", str(game_info["time"]))
                except Exception:
                    log.error("An user tried to encode an non existing combination: game_number={}, team1={}, "
                              "team2={}".format(game_number, team1_code, team2_code))
                    page = page.replace('{notification}', "Cette combinaison n'existe pas")
                    page = page.replace('id="time-row"', 'id="time-row" style="display: none;"')
                    page = page.replace('id="confirm-score"', 'id="confirm-score" style="display: none;"')
                    page = page.replace(
                        'id="retry-button" style="display: none;"',
                        'id="retry-button" style="display: block;"'
                    )
                    page = page.replace('{notification}', notification)
                    return page
                if game_info["winner"] >= 0:
                    page = page.replace(
                        'id="previous-equally-scored" style="display: none;"',
                        'id="previous-equally-scored" style="display: block;"'
                    )
                    page = page.replace('{previous_team1_code}', game_info["players"][0])
                    page = page.replace('{previous_team2_code}', game_info["players"][1])
                    if game_info["winner"] == 0:
                        page = page.replace(
                            'id="previous-equally-scored" style="display: none;"',
                            'id="previous-equally-scored"'
                        )
                        page = page.replace('{previous_team1_title}', "Team 1")
                        page = page.replace('{previous_team2_title}', "Team 2")
                    else:
                        page = page.replace('{previous_team1_title}', "Gagnant")
                        page = page.replace('{previous_team2_title}', "Perdant")
        page = page.replace('{notification}', notification)
        game_number = cherrypy.session.get('game_number', "")
        page = page.replace("{game-number}", game_number)
        return page

    @cherrypy.expose
    def setup(self, adminpwd=None, userpwd=None):
        if adminpwd and userpwd:
            log.info("Passwords set up")
            AdminPages.admin_password = adminpwd
            self.leader_password = userpwd
        if self.leader_password and AdminPages.admin_password:
            return "Server is set up."
        else:
            return get_html("setup.html").replace("{target-page}", "./setup")

    @cherrypy.expose
    def log(self):
        log_content = open(join(properties.PROJECT_ROOT, "activity.log"), 'r').read()
        log_content = log_content.replace('\n', "<br/>")
        return log_content


class AdminPages:
    admin_password = ""

    def request_login(self, origin, password):
        login_page = get_html("login.html")
        login_page = login_page.replace("{target-page}", "/admin/{}".format(origin))
        if is_brute_force_attack():
            return login_page.replace(
                'id="attack" style="display:none;"',
                'id="attack"'
            )
        if password:
            if password == self.admin_password:
                cherrypy.session['admin_logged'] = True
                cherrypy.session['logged'] = True
            else:
                add_login_attempt()
                login_page = login_page.replace(
                    'id="wrong-password" style="display:none;"',
                    'id="wrong-password"'
                )
        if cherrypy.session.get('admin_logged'):
            return None
        else:
            return login_page

    @cherrypy.expose
    def index(self, password=None):
        login_page = self.request_login("index", password)
        return login_page if login_page else get_html("admin.html")

    @cherrypy.expose
    def teams(self, password=None):
        login_page = self.request_login("teams", password)
        if login_page:
            return login_page
        round_quantity = game.get_round_quantity()
        section_scores = service.get_all_sections_score()
        code_list = list()
        code_list.append(open(join(HTML_DIR, "header_admin.html"), 'r').read())
        with html.div(code_list, 'class="table-responsive-sm text-nowrap text-center"'):
            with html.table(code_list, 'class="table table-bordered table-hover"'):
                with html.thead(code_list, 'class="thead-light"'):
                    with html.tr(code_list):
                        with html.th(code_list, scope="col"):
                            code_list.append("Teams")
                        with html.th(code_list, scope="col"):
                            code_list.append("Score")
                        with html.th(code_list, scope="col"):
                            code_list.append("Section")
                        with html.th(code_list, scope="col"):
                            code_list.append("V")
                        with html.th(code_list, scope="col"):
                            code_list.append("E")
                        with html.th(code_list, scope="col"):
                            code_list.append("D")
                        for i in range(1, round_quantity + 1):
                            with html.th(code_list, scope="col"):
                                code_list.append("t{}".format(i))
                with html.tbody(code_list):
                    for tm in team.Team.objects().order_by('code'):
                        score, victories, evens, defeat = service.get_score(tm.code)
                        with html.tr(code_list):
                            color_tag = "table-primary" if tm.sex == "M" else "table-danger"
                            with html.th(code_list, scope="row", params='class="{}"'.format(color_tag)):
                                code_list.append(tm.code)
                            with html.td(code_list):
                                code_list.append(str(score))
                            with html.td(code_list):
                                code_list.append(str(round(section_scores[tm.section], 3)))
                            with html.td(code_list):
                                code_list.append(str(victories))
                            with html.td(code_list):
                                code_list.append(str(evens))
                            with html.td(code_list):
                                code_list.append(str(defeat))
                            for g in service.get_games(tm.code):
                                if g.winner == -1:
                                    color_tag = ""
                                elif g.winner == tm.number:
                                    color_tag = "table-success"
                                elif g.winner == 0:
                                    color_tag = "table-warning"
                                else:
                                    color_tag = "table-danger"
                                with html.td(code_list, 'class="{}"'.format(color_tag)):
                                    with html.a(code_list, "/admin/game?number={}".format(g.number)):
                                        code_list.append(str(g.number))

        code_list.append(open(join(HTML_DIR, "footer.html"), 'r').read())
        return ''.join(code_list)

    @cherrypy.expose
    def games(self, password=None):
        login_page = self.request_login("games", password)
        if login_page:
            return login_page
        round_quantity = game.get_round_quantity()
        game_numbers = game.Game.objects().distinct("number")
        code_list = list()
        code_list.append(open(join(HTML_DIR, "header_admin.html"), 'r').read())
        with html.div(code_list, 'class="table-responsive-sm text-nowrap text-center"'):
            with html.table(code_list, 'class="table table-bordered table-hover"'):
                with html.thead(code_list, 'class="thead-light"'):
                    with html.tr(code_list):
                        with html.th(code_list, scope="col"):
                            code_list.append("Jeu")
                        for i in range(1, round_quantity + 1):
                            with html.th(code_list, scope="col"):
                                code_list.append("t{}".format(i))
                with html.tbody(code_list):
                    with html.tr(code_list):
                        with html.th(code_list, scope="row"):
                            code_list.append("OK")
                        for t in range(1, round_quantity + 1):
                            gathered_point_amount = game.get_gathered_point_amount(t)
                            if gathered_point_amount == properties.SCORED_GAME_AMOUNT:
                                color_tag = "table-success"
                            elif gathered_point_amount < properties.SCORED_GAME_AMOUNT:
                                color_tag = ""
                            else:
                                color_tag = "table-danger"
                            with html.td(code_list, 'class="{}"'.format(color_tag)):
                                code_list.append(" ")
                    for game_number in game_numbers:
                        with html.tr(code_list):
                            with html.th(code_list, scope="row"):
                                code_list.append("Jeu {}".format(game_number))
                            for t in range(1, round_quantity + 1):
                                g = service.get_game_info(game_number=game_number, time=t)
                                color_tag = "table-success" if g["winner"] >= 0 else ""
                                with html.td(code_list, 'class="{}"'.format(color_tag)):
                                    with html.a(code_list, "/admin/game?number={}".format(game_number)):
                                        code_list.append("{} - {}".format(*g["players"]))
        code_list.append(open(join(HTML_DIR, "footer.html"), 'r').read())
        return ''.join(code_list)

