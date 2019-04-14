import logging
from random import randint

from mongoengine import *

from exceptions import BadenException
from model import properties
from model.game import Game
from model.team import Team

log = logging.getLogger('default')


def setup_db():
    connect(
        properties.DB_NAME,
        host=properties.DB_HOST,
        port=properties.DB_PORT,
    )


def is_team(team_code):
    return Team.objects(code=team_code).count() > 0


def is_game(game_number):
    return Game.objects(number=game_number).count() > 0


def get_game_name(game_number):
    return Game.objects(number=game_number).first().name


def get_section(team_code):
    return Team.objects(code=team_code).get().section


def get_score(team_code):
    return Team.objects(code=team_code).get().score


def get_section_score(team_code):
    return Team.objects(section=get_section(team_code)).average('score')


def get_games(team_code):
    """
    Get list of game for a given team
    :param team_code: team code
    :return: list of games ordered in time
    """
    game_list = list()
    team_number = Team.objects(code=team_code).get().number
    for game in Game.objects(players=team_number).order_by('time'):
        game_list.append(game)
    return game_list


def get_game_object(game_number, player_code):
    """
    Get a game from a game number and a player code
    :param game_number: the game number
    :param player_code: the player code
    :return: the target Game object
    """
    player_number = Team.objects(code=player_code).get()
    return Game.objects(number=game_number, players=player_number).get()


def get_game_from_players(player1_code, player2_code):
    """
    Get a game number from the players codes
    :param player1_code: the first player code
    :param player2_code: the second player code
    :return: the target Game object
    """
    player1_number = Team.objects(code=player1_code).get()
    player2_number = Team.objects(code=player2_code).get()
    return Game.objects(players__all=[player1_number, player2_number]).get()


def get_opponent(game_number, player_code):
    """
    Get the opponent of a given player at a given game
    :param game_number: the game number
    :param player_code: the player code
    :return: the Team object of the opponent
    """
    player_number = Team.objects(code=player_code).get()
    game = Game.objects(number=game_number, players=player_number).get()
    for p in game.players:
        if p.number != player_number:
            return Team.objects(number=p.number).get()


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
        player1 = Team.objects(number=players[0]).get()
        player2 = Team.objects(number=players[1]).get()
        player_list.append((player1, player2))
    return player_list


def distribute_numbers(ignore_sex=False):
    """
    Distribute numbers to the teams.
    :param ignore_sex: mix sex across the distribution, else distribute the first numbers to the girls and then to the guys
    """
    def shuffle(teams, floor_number):
        """
        Distribute random numbers to a list of Team objects, starting at number floor_number
        :param teams: Team QuerySet
        :param floor_number: starting point for the number counter
        :return the list of modified teams
        """
        modified_teams = []
        ceil_number = len(teams) + floor_number - 1
        available_numbers = [i for i in range(floor_number, ceil_number + 1)]
        for team in teams:
            index = randint(0, len(available_numbers) - 1)
            team.number = available_numbers[index]
            available_numbers.pop(index)
            modified_teams.append(team)
        if len(available_numbers) > 0:
            raise BadenException("some numbers were not distributed during shuffle: {}".format(available_numbers))
        log.info("{} teams shuffled from number {} to {}".format(len(teams), floor_number, ceil_number))
        return modified_teams

    modified_teams = []
    if ignore_sex:
        modified_teams += shuffle(Team.objects(), 1)
    else:
        modified_teams += shuffle(Team.objects(sex="F"), 1)
        modified_teams += shuffle(Team.objects(sex="M"), Team.objects(sex="F").count() + 1)
    for t1 in modified_teams:
        for t2 in modified_teams:
            if t1.number == t2.number and t1.id != t2.id:
                raise BadenException("There are two teams ({} & {}) with the same number ({}). Distribution not saved"
                                     .format(t1.id, t2.id, t1.number))
    for team in modified_teams:
        team.save()


def get_ranking_by_section(gender=None):
    """
    Get the ranking by section. Scores is based on the average of all the teams of each section
    :param gender: (optional) filter the ranking on a gender
    :return: list of tuples (section, mean score)
    """
    teams = Team.objects(sex=gender) if gender else Team.objects()
    section_scores = dict()
    for team in teams:
        if team.section in section_scores:
            section_scores[team.section].append(team.score)
        else:
            section_scores[team.section] = [team.score]
    section_mean_scores = dict()
    for section, scores in section_scores.items():
        section_mean_scores[section] = sum(scores) / len(scores)
    return sorted(section_mean_scores.items(), key=lambda kv: kv[1])


def get_ranking_by_section2(gender=None):
    sections = Team.objects(sex=gender).distinct('section') if gender else Team.objects().distinct('section')
    mean_scores = dict()
    for section in sections:
        mean_scores[section] = Team.objects(section=section).average('score')
    return sorted(mean_scores.items(), key=lambda kv: kv[1])


def get_ranking(gender=None):
    """
    Get the ranking by team.
    :param gender: (optional) filter the ranking on a gender
    :return: list of tuples (section, team code, score)
    """
    teams = Team.objects(sex=gender).order_by('score') if gender else Team.objects().order_by('score')
    ranking = list()
    for team in teams:
        ranking.append((team.setion, team.code, team.score))
    return ranking


