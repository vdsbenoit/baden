# -*-coding:UTF-8 -*

import logging
from os.path import join

import cherrypy
from mongoengine import DoesNotExist

import model
from model import properties
from model import service
from model.game import Game
from model.match import Match
from model.team import Team
from view import html_util as html

HTML_DIR = join(properties.PROJECT_ROOT, "view", "html")

log = logging.getLogger('default')
login_passwords = None


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
        log.error("IP {} tried to brute force the password".format(str(cherrypy.request.remote.ip)))
        return True
    else:
        return False


def request_login(origin, password, level):
    login_page = get_html("login.html")
    login_page = login_page.replace("{target-page}", "{}".format(origin))
    if is_brute_force_attack():
        login_page = login_page.replace('name="password"', 'name="password" disabled')
        return html.show(login_page, "attack")
    if not login_passwords:
        return "Please ask an admin to initiate the server first"
    if password:
        for l, p in enumerate(login_passwords):
            if p == password and p != "":
                cherrypy.session['user_rights'] = l
        else:
            add_login_attempt()
            login_page = html.show(login_page, "wrong-password")
    if cherrypy.session.get('user_rights', -1) >= level:
        return None
    else:
        return login_page


class UserPages:
    @cherrypy.expose
    def index(self, **unknown_args):
        if login_passwords:
            return get_html("home.html")
        else:
            return "Please ask an admin to initiate the server"

    @cherrypy.expose
    def player(self, team_code=None, **unknown_args):
        page = get_html("player.html")
        if team_code:
            if not service.is_team(team_code):
                page = page.replace("{teamcode}", team_code)
                return html.show(page, "wrong-teamcode")
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
            page = html.show(page, "scores")
        else:
            page = page.replace("{teamcode}", "")

        return page

    @cherrypy.expose
    def leader(self, password=None, team1_code=None, team2_code=None, game_number=None, winner=None, confirmed=None, **unknown_args):
        login_page = request_login("/leader", password, 0)
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
                # confirm page
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
                    page = page.replace("{schedule}", match.schedule)
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


class AdminPages:
    @cherrypy.expose
    def index(self, password=None, **unknown_args):
        login_page = request_login("index", password, 2)
        if login_page:
            return login_page
        page = get_html("admin.html")
        return page

    @cherrypy.expose
    def log(self, password=None, **unknown_args):
        login_page = request_login("log", password, 2)
        if login_page:
            return login_page
        log_content = open(join(properties.PROJECT_ROOT, "activity.log"), 'r', encoding='utf-8').read()
        log_content = log_content.replace('\n', "<br/>")
        return log_content

    @cherrypy.expose
    def setup(self, userpwd=None, modpwd=None, adminpwd=None, **unknown_args):
        global login_passwords
        if login_passwords:
            return "Server is set up."
        elif userpwd and modpwd and adminpwd:
            login_passwords = [userpwd, "", modpwd, "", adminpwd]
            return "Server is set up."
        else:
            return get_html("setup.html")

    @cherrypy.expose
    def teams(self, password=None, **unknown_args):
        login_page = request_login("teams", password, 2)
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
                            with html.a(code_list, "/admin"):
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
                                    with html.a(code_list, "/admin/match?mid={}".format(match.id)):
                                        code_list.append(str(match.game_number))

        code_list.append(open(join(HTML_DIR, "footer.html"), 'r').read())
        return ''.join(code_list)

    @cherrypy.expose
    def games(self, password=None, **unknown_args):
        login_page = request_login("games", password, 2)
        if login_page:
            return login_page
        match_quantity = model.match.get_match_quantity()
        schedules = service.get_all_schedules()
        code_list = list()
        code_list.append(open(join(HTML_DIR, "header_admin.html"), 'r').read())
        with html.div(code_list, 'class="table-responsive-sm text-nowrap text-center"'):
            with html.table(code_list, 'class="table table-bordered table-hover"'):
                with html.thead(code_list, 'class="thead-light"'):
                    with html.tr(code_list):
                        with html.th(code_list, scope="col"):
                            with html.a(code_list, "/admin"):
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
                                code_list.append(schedules[t-1])
                    for game in Game.objects().order_by('number'):
                        with html.tr(code_list):
                            with html.th(code_list, scope="row"):
                                code_list.append("Jeu {}".format(game.number))
                            with html.td(code_list):
                                code_list.append(game.circuit)
                            for match in game.matches:
                                color_tag = "table-success" if match.recorded else ""
                                with html.td(code_list, 'class="{}"'.format(color_tag)):
                                    with html.a(code_list, "/admin/match?mid={}".format(match.id)):
                                        code_list.append("{} - {}".format(*match.players_code))
        code_list.append(open(join(HTML_DIR, "footer.html"), 'r').read())
        return ''.join(code_list)

    @cherrypy.expose
    def ranking(self, password=None, size=1000, **unknown_args):
        login_page = request_login("ranking", password, 2)
        if login_page:
            return login_page
        try:
            size = int(size)
        except ValueError:
            return "Size argument not an integer"
        female_section_ranking = service.get_ranking_by_section("F")
        male_section_ranking = service.get_ranking_by_section("M")
        male_ranking = service.get_ranking("M")
        female_ranking = service.get_ranking("F")
        code_list = list()
        code_list.append(open(join(HTML_DIR, "header_admin.html"), 'r').read())
        with html.div(code_list, 'class="container-fluid text-center"'):
            with html.div(code_list, 'class="row"'):
                with html.div(code_list, 'class="col"'):
                    with html.h(4, code_list, 'class="ranking-title"'):
                        code_list.append("Sections lutins")
                    with html.table(code_list, 'class="table table-sm table-bordered"'):
                        with html.thead(code_list, 'class="table-success"'):
                            with html.tr(code_list):
                                with html.th(code_list, scope="col"):
                                    code_list.append("#")
                                with html.th(code_list, scope="col"):
                                    code_list.append("Section")
                                with html.th(code_list, scope="col"):
                                    code_list.append("Pts")
                        with html.tbody(code_list):
                            for i, score in enumerate(female_section_ranking):
                                if i < size:
                                    with html.tr(code_list):
                                        with html.th(code_list, "row"):
                                            code_list.append(str(i+1))
                                        with html.td(code_list, 'class="text-left"'):
                                            code_list.append(score[0])
                                        with html.td(code_list):
                                            code_list.append(str(round(score[1], 2)))
                with html.div(code_list, 'class="col"'):
                    with html.h(4, code_list, 'class="ranking-title"'):
                        code_list.append("Sections louveteaux")
                    with html.table(code_list, 'class="table table-sm table-bordered"'):
                        with html.thead(code_list, 'class="table-success"'):
                            with html.tr(code_list):
                                with html.th(code_list, scope="col"):
                                    code_list.append("#")
                                with html.th(code_list, scope="col"):
                                    code_list.append("Section")
                                with html.th(code_list, scope="col"):
                                    code_list.append("Pts")
                        with html.tbody(code_list):
                            for i, score in enumerate(male_section_ranking):
                                if i < size:
                                    with html.tr(code_list):
                                        with html.th(code_list, "row"):
                                            code_list.append(str(i+1))
                                        with html.td(code_list, 'class="text-left"'):
                                            code_list.append(score[0])
                                        with html.td(code_list):
                                            code_list.append(str(round(score[1], 2)))
                with html.div(code_list, 'class="col"'):
                    with html.h(4, code_list, 'class="ranking-title"'):
                        code_list.append("Lutins")
                    with html.table(code_list, 'class="table table-sm table-bordered"'):
                        with html.thead(code_list, 'class="table-success"'):
                            with html.tr(code_list):
                                with html.th(code_list, scope="col"):
                                    code_list.append("#")
                                with html.th(code_list, scope="col"):
                                    code_list.append("Team")
                                with html.th(code_list, scope="col"):
                                    code_list.append("Section")
                                with html.th(code_list, scope="col"):
                                    code_list.append("Pts")
                        with html.tbody(code_list):
                            for i, score in enumerate(female_ranking):
                                if i < size:
                                    with html.tr(code_list):
                                        with html.th(code_list, "row"):
                                            code_list.append(str(i+1))
                                        with html.td(code_list):
                                            code_list.append(score[0])
                                        with html.td(code_list, 'class="text-left"'):
                                            code_list.append(score[1])
                                        with html.td(code_list):
                                            code_list.append(str(score[2]))
                with html.div(code_list, 'class="col"'):
                    with html.h(4, code_list, 'class="ranking-title"'):
                        code_list.append("Louveteaux")
                    with html.table(code_list, 'class="table table-sm table-bordered"'):
                        with html.thead(code_list, 'class="table-success"'):
                            with html.tr(code_list):
                                with html.th(code_list, scope="col"):
                                    code_list.append("#")
                                with html.th(code_list, scope="col"):
                                    code_list.append("Team")
                                with html.th(code_list, scope="col"):
                                    code_list.append("Section")
                                with html.th(code_list, scope="col"):
                                    code_list.append("Pts")
                        with html.tbody(code_list):
                            for i, score in enumerate(male_ranking):
                                if i < size:
                                    with html.tr(code_list):
                                        with html.th(code_list, "row"):
                                            code_list.append(str(i+1))
                                        with html.td(code_list):
                                            code_list.append(score[0])
                                        with html.td(code_list, 'class="text-left"'):
                                            code_list.append(score[1])
                                        with html.td(code_list):
                                            code_list.append(str(score[2]))
        code_list.append(open(join(HTML_DIR, "footer.html"), 'r').read())
        return ''.join(code_list)

    @cherrypy.expose
    def match(self, password=None, mid=None, winner=None, **unknown_args):
        login_page = request_login("match", password, 2)
        if login_page:
            return login_page
        page = get_html("match.html")
        notification = ""
        error = ""
        try:
            match = Match.objects(id=mid).get()
            game = Game.objects(number=match.game_number).get()
        except DoesNotExist:
            page = html.show(page, "error-not-found")
            page = html.hide(page, "match-form")
            log.error("{} tried to load a not-existing match (id={})".format(str(cherrypy.request.remote.ip), mid))
        except Exception:
            page = html.show(page, "error-not-found")
            page = html.hide(page, "match-form")
            log.exception("{} tried to load a not-existing match (id={})".format(str(cherrypy.request.remote.ip), mid))
        else:
            team1_code = match.players_code[0]
            team2_code = match.players_code[1]
            if winner:
                notification = "Le changement de score a bien &eacute;t&eacute; enregistr&eacute;"
                if winner == "even":
                    service.set_even(game.number, team1_code, team2_code)
                elif winner == team1_code:
                    service.set_winner(game.number, team1_code, team2_code)
                elif winner == team2_code:
                    service.set_winner(game.number, team2_code, team1_code)
                elif winner == "no-scores":
                    service.reset_match(game.number, team1_code, team2_code)
                else:
                    error = "Le changement de score n'a pas pu &ecirc;tre enregistr&eacute;"
                    notification = ""
                    log.error("{} tried to set an unknown type of winner ({}) at match id {}".format(str(cherrypy.request.remote.ip), winner, mid))
                match = Match.objects(id=mid).get()
            team1_section = service.get_section(team1_code)
            team2_section = service.get_section(team2_code)
            page = page.replace("{game-number}", str(game.number))
            page = page.replace("{game-name}", game.name)
            page = page.replace("{time}", str(match.time))
            page = page.replace("{schedule}", match.schedule)
            page = page.replace("{team1-code}", team1_code)
            page = page.replace("{team2-code}", team2_code)
            page = page.replace("{team1}", "{} - {}".format(team1_code, team1_section))
            page = page.replace("{team2}", "{} - {}".format(team2_code, team2_section))
            page = page.replace("{mid}", str(match.id))
            if not match.recorded:
                page = page.replace('value="no-scores"', 'value="no-scores" checked')
            elif match.even:
                page = page.replace('value="even"', 'value="even" checked')
            elif match.winner == team1_code:
                page = page.replace('value="{}"'.format(team1_code), 'value="{}" checked'.format(team1_code))
            elif match.winner == team2_code:
                page = page.replace('value="{}"'.format(team2_code), 'value="{}" checked'.format(team2_code))
        page = page.replace('{notification}', notification)
        page = page.replace('{error}', error)
        return page

