import logging

import cherrypy

from exceptions import BadenException
from model import service
from mongoengine import DoesNotExist

log = logging.getLogger('default')


class Api:
    @cherrypy.expose
    def get_team_section(self, team_code):
        if service.is_team(team_code):
            return service.get_section(team_code)
        else:
            log.error("{} unsuccessfully tried to get the section name of team code {}".format(
                str(cherrypy.request.remote.ip), team_code))
            return "Error: il n'y a pas de team {}".format(team_code)

    @cherrypy.expose
    def get_game_name(self, game_number):
        try:
            int_game_number = int(game_number)
        except ValueError:
            log.error("{} unsuccessfully tried to get the game name of game number {}".format(
                str(cherrypy.request.remote.ip), game_number))
            return "Error: {} n'est pas un chiffre".format(game_number)
        if game_number and service.is_game(int_game_number):
            return service.get_game_name(int_game_number)
        else:
            log.error("{} unsuccessfully tried to get the game name of game number {}".format(
                str(cherrypy.request.remote.ip), game_number))
            return "Error: il n'y a pas de jeu numéro {}".format(game_number)

    @cherrypy.expose
    def get_opponent_code(self, game_number, team_code):
        try:
            int_game_number = int(game_number)
        except ValueError:
            log.error(
                "{} unsuccessfully tried to get the opponent of team code {} but the game number {} is not an integer".format(
                    str(cherrypy.request.remote.ip), team_code, game_number))
            return ""
        if not service.is_game(int(int_game_number)):
            log.error(
                "{} unsuccessfully tried to get the opponent of team code {} but the game number {} was wrong".format(
                    str(cherrypy.request.remote.ip), team_code, int_game_number))
            return ""
        if not service.is_team(team_code):
            log.error(
                "{} unsuccessfully tried to get the opponent of at game {} but the team number {} was wrong".format(
                    str(cherrypy.request.remote.ip), int_game_number, team_code))
            return ""
        try:
            return service.get_opponent_code(int_game_number, team_code)
        except DoesNotExist:
            msg = "Pas de combinaison trouvée pour {} au jeu {}".format(team_code, int_game_number)
            log.info(msg)
            return "Error: " + msg

    @cherrypy.expose
    def get_game_number(self, team1_code, team2_code):
        if not service.is_team(team1_code):
            log.error(
                "{} unsuccessfully tried to get the game number of team code {} but the opponent team code {} was wrong".format(
                    str(cherrypy.request.remote.ip), team2_code, team1_code))
            return ""
        if not service.is_team(team2_code):
            log.error(
                "{} unsuccessfully tried to get the game number of team code {} but the opponent team code {} was wrong".format(
                    str(cherrypy.request.remote.ip), team1_code, team2_code))
            return ""
        try:
            return str(service.get_game_info(team_code=team1_code, team2_code=team2_code)["number"])
        except DoesNotExist:
            msg = "Les équipes {} et {} ne sont pas censées jouer ensemble".format(team1_code, team2_code)
            log.info(msg)
            return "Error: " + msg

    @cherrypy.expose
    def get_hash_translation(self, value):
        try:
            return str(service.get_hash_translation(value))
        except BadenException:
            return "Error: Le code QR n'est pas valide"

    @cherrypy.expose
    def set_winner(self, game_number, winner_code, loser_code):
        try:
            int_game_number = int(game_number)
        except ValueError:
            log.error(
                "{} unsuccessfully tried to set point to team {} at game {} but the game number is not an interger".format(
                    str(cherrypy.request.remote.ip), winner_code, game_number))
            return "Error: {} n'est pas un chiffre".format(game_number)
        if cherrypy.session.get("logged"):
            if not service.is_team(winner_code):
                log.error(
                    "{} unsuccessfully tried to set point to team {} at game {} but the team code was wrong".format(
                        str(cherrypy.request.remote.ip), winner_code, int_game_number))
                return "Error: il n'y a pas de team avec le code {}".format(winner_code)
            if not service.is_team(loser_code):
                log.error(
                    "{} unsuccessfully tried to set point to team {} at game {} but loser team code ({}) was wrong".format(
                        str(cherrypy.request.remote.ip), winner_code, int_game_number, loser_code))
                return "Error: il n'y a pas de team avec le code {}".format(loser_code)
            if not service.is_game(int_game_number):
                log.error(
                    "{} unsuccessfully tried to set point to team {} at game {} but loser game number was wrong".format(
                        str(cherrypy.request.remote.ip), winner_code, int_game_number))
                return "Error: il n'y a pas de jeu numéro {}".format(int_game_number)
            return service.set_winner(int(int_game_number), winner_code, loser_code)
        else:
            log.error("{} tried to set a victory for team {} without being logged".format(
                str(cherrypy.request.remote.ip), winner_code
            ))
            return "Error: vous n'êtes pas connecté"



