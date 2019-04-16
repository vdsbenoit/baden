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


def get_team_code(team_number):
    return Team.objects(number=team_number).get().code


def get_hash_translation(hash_value):
    game = Game.objects(hash=hash_value).first()
    if game:
        return game.number
    try:
        return Team.objects(hash=hash_value).get().code
    except DoesNotExist:
        raise BadenException("No teams nor games found for hash {}".format(hash_value))


def get_opponent_code(game_number, team_code):
    """
    Get the opponent of a given player at a given game
    :param game_number: the game number
    :param team_code: the player code
    :return: the opponent code
    """
    game = get_game_info(game_number=game_number, team_code=team_code)
    for p in game["players"]:
        if p != team_code:
            return p


def get_game_info(game_number=None, time=None, team_code=None, team2_code=None):
    """
    Find the game object according to given parameters
    There must be minimum 2 parameters set.
    :return: a dict with the game info
    """
    lst = [game_number, time, team_code, team2_code]
    if(len([x for x in lst if x is not None])) < 2:
        raise BadenException("You must give minimum 2 parameters to find a game")
    if team_code:
        try:
            team1_number = Team.objects(code=team_code).get().number
        except DoesNotExist:
            raise BadenException("Team {} does not exist".format(team_code))
        if game_number:
            game = Game.objects(number=game_number, players=team1_number).get()
        elif time:
            game = Game.objects(time=time, players=team1_number).get()
        elif team2_code:
            try:
                team2_number = Team.objects(code=team2_code).get().number
            except DoesNotExist:
                raise BadenException("Team {} does not exist".format(team2_code))
            game = Game.objects(players__all=[team1_number, team2_number]).get()
    elif team2_code:
        raise BadenException("You must give a team_code if you want to use team2_code")
    else:
        game = Game.objects(time=time, number=game_number).get()
    game_info = dict({
        "circuit": game.circuit,
        "number": game.number,
        "name": game.name,
        "time": game.time,
        "winner": game.winner,
    })
    game_info["players"] = [
        get_team_code(game.players[0]),
        get_team_code(game.players[1])
        ]
    return game_info


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


def set_winner(game_number, winner_team_code, loser_team_code):
    """
    Set a team as the winner of a game.
    Assert the game exists.
    :param game_number: a game number
    :param winner_team_code: the winner team code
    :param loser_team_code: the loser team code
    :return: True if the game was update, False if the game was not found
    """
    winner = Team.objects(code=winner_team_code).get()
    loser = Team.objects(code=loser_team_code).get()
    try:
        game = Game.objects(number=game_number, players__all=[winner.number, loser.number]).get()
        game.winner = winner.number
        game.save()
        log.info("Team {} won the game {} against {}".format(winner_team_code, game_number, loser_team_code))
        return True
    except DoesNotExist:
        return False


def set_even(game_number, team1_code, team2_code):
    """
    Set a game as equally won.
    Assert the game exists.
    :param game_number: a game number
    :param team1_code: a team code
    :param team2_code: another team code
    :return: True if the game was update, False if the game was not found
    """
    team1 = Team.objects(code=team1_code).get()
    team2 = Team.objects(code=team1_code).get()
    try:
        game = Game.objects(number=game_number, players__all=[team1.number, team2.number]).get()
        game.winner = 0
        game.save()
        log.info("Team {} and team {} are equally placed at the game {}".format(team1_code, team2_code, game_number))
        return True
    except DoesNotExist:
        return False


def get_score(team_code):
    """
    Get the score of a given team
    :param team_code: a team code
    :return: a tuple (score, victories, evens)
    """
    team_number = Team.objects(code=team_code).get().number
    victories = Game.objects(winner=team_number).count()
    evens = Game.objects(winner=0, players=team_number).count()
    score = victories * 2 + evens
    return score, victories, evens


def get_team_section_score(team_code):
    """
    Get the mean score of the section of a given team
    :param team_code: a team code
    :return: the mean score
    """
    scores = list()
    teams = Team.objects(section=get_section(team_code))
    for team in teams:
        scores.append(get_score(team.code)[0])
    return sum(scores) / len(scores)


def get_section_score(section):
    """
    Get the mean score of a given section
    :param section: a section name
    :return: the mean score
    """
    scores = list()
    teams = Team.objects(section=section)
    for team in teams:
        scores.append(get_score(team.code)[0])
    return sum(scores) / len(scores)


def get_ranking_by_section(gender=None):
    """
    Get the ranking by section. Scores is based on the average of all the teams of each section
    :param gender: (optional) filter the ranking on a gender
    :return: list of tuples (section, mean score)
    """
    sections = Team.objects(sex=gender).distinct('section') if gender else Team.objects().distinct('section')
    section_scores = dict()
    for section in sections:
        section_scores[section] = get_section_score(section)
    return sorted(section_scores.items(), key=lambda kv: kv[1], reverse=True)


def get_ranking(gender=None):
    """
    Get the ranking by team.
    :param gender: (optional) filter the ranking on a gender
    :return: list of tuples (team code, section, score)
    """
    teams = Team.objects(sex=gender) if gender else Team.objects()
    scores = list()
    for team in teams:
        scores.append((team.code, team.section, get_score(team.code)))
    return sorted(scores, key=lambda xyz: xyz[2], reverse=True)


