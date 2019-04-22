# -*-coding:UTF-8 -*

import logging
from os.path import join

import cherrypy

import model
from model import properties
from model import service
from model.team import Team
from model.game import Game
from model.match import Match
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
            section = service.get_section(team_code)
            page = page.replace("{teamcode}", team_code)
            page = page.replace("{section-name}", section)
            page = page.replace("{section-score}", str(round(service.get_section_score(section), 2)))
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

        notification = ""
        warning = ""
        page = get_html("leader.html")
        if team1_code and team2_code and game_number:
            wrong_team1 = False if service.is_team(team1_code) else True
            wrong_team2 = False if service.is_team(team2_code) else True
            wrong_game = False if service.is_game(game_number) else True
            good_values = False if wrong_game or wrong_team1 or wrong_team2 else True
            if winner and team2_code == winner:
                team2_code = team1_code
                team1_code = winner
            if confirmed and good_values:
                cherrypy.session['game_number'] = game_number
                try:
                    if winner == "even":
                        service.set_even(int(game_number), team1_code, team2_code)
                    else:
                        service.set_winner(int(game_number), team1_code, team2_code)
                    notification = 'Le score a bien &eacute;t&eacute; enregistr&eacute;'
                except Exception:
                    log.exception("Something bad occurred while an user tried to set a score")
                    warning = "Le score n'a pas pu &ecirc;tre enregistr&eacute.\n" \
                              "Merci de le signaler à l'administrateur.;"
            else:
                page = get_html("confirm_score.html")
                page = page.replace('{game_number}', str(game_number))
                page = page.replace('{team1_code}', team1_code)
                page = page.replace('{team2_code}', team2_code)
                if winner == "even":
                    page = page.replace('{team1_title}', "Team 1")
                    page = page.replace('{team2_title}', "Team 2")
                    page = page.replace('{even-hidden-input}', '<input type="hidden" name="winner" value="even"/>')
                    page = html.show(page, "equally-scored")
                else:
                    page = page.replace('{team1_title}', "Gagnant")
                    page = page.replace('{team2_title}', "Perdant")
                    page = page.replace('{even-hidden-input}', '')
                try:
                    match = Match.objects(game_number=game_number, players_code=team1_code).get()
                    page = page.replace("{time}", str(match.time))
                    if match.recorded:
                        page = html.show(page, "previous-score")
                        if match.even:
                            page = html.show(page, "previous-equally-scored")
                            page = page.replace('{previous_team1_title}', "Team 1")
                            page = page.replace('{previous_team2_title}', "Team 2")
                            page = page.replace('{previous_team1_code}', match.players_code[0])
                            page = page.replace('{previous_team2_code}', match.players_code[1])
                        else:
                            page = page.replace('{previous_team1_title}', "Gagnant")
                            page = page.replace('{previous_team2_title}', "Perdant")
                            page = page.replace('{previous_team1_code}', match.winner)
                            page = page.replace('{previous_team2_code}', match.loser)
                except Exception:
                    log.exception("An user tried to encode an non existing combination: game_number={}, team1={}, "
                              "team2={}".format(game_number, team1_code, team2_code))
                    warning = "Cette combinaison n'existe pas"
                    page = html.hide(page, "time-row")
                    page = html.hide(page, "confirm-score")
                    page = html.show(page, "retry-button")
                finally:
                    page = page.replace('{previous_team1_title}', "Team 1")
                    page = page.replace('{previous_team2_title}', "Team 2")
                    page = page.replace('{previous_team1_code}', "")
                    page = page.replace('{previous_team2_code}', "")

        page = page.replace("{game-number}", cherrypy.session.get('game_number', ""))
        page = page.replace('{notification}', notification)
        page = page.replace('{warning}', warning)
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
        match_quantity = model.match.get_match_quantity()
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
                            code_list.append("V")
                        with html.th(code_list, scope="col"):
                            code_list.append("E")
                        with html.th(code_list, scope="col"):
                            code_list.append("D")
                        for i in range(1, match_quantity + 1):
                            with html.th(code_list, scope="col"):
                                code_list.append("t{}".format(i))
                with html.tbody(code_list):
                    for team in Team.objects().order_by('code'):
                        score, victories, evens, defeat = service.get_score(team.code)
                        with html.tr(code_list):
                            color_tag = "table-primary" if team.sex == "M" else "table-danger"
                            with html.th(code_list, scope="row", params='class="{}"'.format(color_tag)):
                                code_list.append(team.code)
                            with html.td(code_list):
                                code_list.append(str(score))
                            with html.td(code_list):
                                code_list.append(str(victories))
                            with html.td(code_list):
                                code_list.append(str(evens))
                            with html.td(code_list):
                                code_list.append(str(defeat))
                            for match in team.matches:
                                if not match.recorded:
                                    color_tag = ""
                                elif match.even:
                                    color_tag = "table-warning"
                                elif match.winner == team.code:
                                    color_tag = "table-success"
                                else:
                                    color_tag = "table-danger"
                                with html.td(code_list, 'class="{}"'.format(color_tag)):
                                    with html.a(code_list, "/admin/match?id={}".format(match.id)):
                                        code_list.append(str(match.game_number))

        code_list.append(open(join(HTML_DIR, "footer.html"), 'r').read())
        return ''.join(code_list)

    @cherrypy.expose
    def games(self, password=None):
        login_page = self.request_login("games", password)
        if login_page:
            return login_page
        match_quantity = model.match.get_match_quantity()
        code_list = list()
        code_list.append(open(join(HTML_DIR, "header_admin.html"), 'r').read())
        with html.div(code_list, 'class="table-responsive-sm text-nowrap text-center"'):
            with html.table(code_list, 'class="table table-bordered table-hover"'):
                with html.thead(code_list, 'class="thead-light"'):
                    with html.tr(code_list):
                        with html.th(code_list, scope="col"):
                            code_list.append("Jeux")
                        with html.th(code_list, scope="col"):
                            code_list.append("Circuit")
                        for i in range(1, match_quantity + 1):
                            with html.th(code_list, scope="col"):
                                code_list.append("t{}".format(i))
                with html.tbody(code_list):
                    with html.tr(code_list):
                        with html.th(code_list, scope="row"):
                            code_list.append("OK")
                        with html.td(code_list):
                            code_list.append("")
                        for t in range(1, match_quantity + 1):
                            recorded_scores_amount = model.match.get_recorded_scores_amount(t)
                            if recorded_scores_amount == properties.SCORED_GAME_AMOUNT:
                                color_tag = "table-success"
                            elif recorded_scores_amount < properties.SCORED_GAME_AMOUNT:
                                color_tag = ""
                            else:
                                color_tag = "table-danger"
                                log.error("There were {} recorded scores at time {} (> {})".format(
                                    recorded_scores_amount, t, properties.SCORED_GAME_AMOUNT))
                            with html.td(code_list, 'class="{}"'.format(color_tag)):
                                code_list.append(" ")
                    for game in Game.objects():
                        with html.tr(code_list):
                            with html.th(code_list, scope="row"):
                                code_list.append("Jeu {}".format(game.number))
                            with html.td(code_list):
                                code_list.append(game.circuit)
                            for match in game.matches:
                                color_tag = "table-success" if match.recorded else ""
                                with html.td(code_list, 'class="{}"'.format(color_tag)):
                                    with html.a(code_list, "/admin/game?match={}".format(match.id)):
                                        code_list.append("{} - {}".format(*match.players_code))
        code_list.append(open(join(HTML_DIR, "footer.html"), 'r').read())
        return ''.join(code_list)
