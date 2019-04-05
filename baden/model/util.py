from mongoengine import *

from model import properties
from model.game import Game
from model.team import Team


def setup_db():
    connect(properties.DB_NAME, host=properties.DB_HOST, port=properties.DB_PORT)


def get_games(team_code):
    """
    Get list of game for a given team
    :param team_code: team code
    :return: list of tuple (game_number, game_name) ordered in time
    """
    game_list = list()
    team_number = Team.objects(code=team_code).get().number
    for game in Game.objects(players=team_number).order_by('time'):
        game_list.append((game.number, game.name))
    return game_list


def get_players(game_number):
    """
    Get list of players for all the rounds of a game
    :param game_number: game number
    :return: list of tuples (player1, player2) ordered in time
    """
    player_list = list()
    games = Game.objects(number=game_number).order_by('time')
    for game in games:
        players = game.players
        player1 = Team.objects(number=players[0])
        player2 = Team.objects(number=players[1])
        player_list.append((player1, player2))
    return player_list


