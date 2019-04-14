import logging

import cherrypy

from model import service

log = logging.getLogger('default')


class Api:
    @cherrypy.expose
    def get_team_section(self, team_code):
        if service.is_team(team_code):
            return service.get_section(team_code)
        else:
            log.error("{} unsuccessfully tried to get the section name of team code {}".format(
                str(cherrypy.request.remote.ip), team_code))
            return "Error: il n'existe pas de team avec le code {}".format(team_code)

    @cherrypy.expose
    def get_game_name(self, game_number):
        if service.is_game(int(game_number)):
            return service.get_game_name(int(game_number))
        else:
            log.error("{} unsuccessfully tried to get the game name of game number {}".format(
                str(cherrypy.request.remote.ip), game_number))
            return "Error: il n'existe pas de jeu avec le numéro {}".format(game_number)

    @cherrypy.expose
    def get_opponent_code(self, game_number, team_code):
        if not service.is_game(int(game_number)):
            log.error(
                "{} unsuccessfully tried to get the opponent of team code {} but the game number {} was wrong".format(
                    str(cherrypy.request.remote.ip), team_code, game_number))
            return "Error: il n'existe pas de jeu avec le numéro {}".format(int(game_number))
        if not service.is_team(team_code):
            log.error(
                "{} unsuccessfully tried to get the opponent of at game {} but the team number {} was wrong".format(
                    str(cherrypy.request.remote.ip), game_number, team_code))
            return "Error: il n'existe pas de team avec le code {}".format(team_code)
        return service.get_opponent(game_number, team_code)

    @cherrypy.expose
    def get_game_number(self, team1_code, team2_code):
        if not service.is_team(team1_code):
            log.error(
                "{} unsuccessfully tried to get the game number of team code {} but the opponent team code {} was wrong".format(
                    str(cherrypy.request.remote.ip), team2_code, team1_code))
            return "Error: il n'existe pas de team avec le code {}".format(team1_code)
        if not service.is_team(team2_code):
            log.error(
                "{} unsuccessfully tried to get the game number of team code {} but the opponent team code {} was wrong".format(
                    str(cherrypy.request.remote.ip), team1_code, team2_code))
            return "Error: il n'existe pas de team avec le code {}".format(team2_code)
        return service.get_game_from_players(team1_code, team2_code)




