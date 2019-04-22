import logging

from mongoengine import *

import model
from exceptions import BadenException
from model import properties
from model.game import Game
from model.match import Match
from model.team import Team

log = logging.getLogger('default')


def setup_db():
    connect(
        properties.DB_NAME,
        host=properties.DB_HOST,
        port=properties.DB_PORT,
    )


def set_player_codes():
    """
    Set players codes in all the Match objects
    """
    for match in Match.objects():
        for number in match.players_number:
            match.players_code.append(Team.objects(number=number).get().code)
        match.save()


def is_team(team_code):
    return Team.objects(code=team_code).count() > 0


def is_game(game_number):
    return Game.objects(number=game_number).count() > 0


def get_game_name(game_number):
    return Game.objects(number=game_number).get().name


def get_section(team_code):
    return Team.objects(code=team_code).get().section


def resolve_hash(hash_value):
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
    match = Match.objects(game_number=game_number, players_code=team_code).get()
    for p in match.players_code:
        if p != team_code:
            return p


def get_matches(team_code):
    """
    Get list of matches for a given team
    :param team_code: team code
    :return: Match QuerySet ordered in time
    """
    return Match.objects(players_code=team_code).order_by('time')


def set_winner(game_number, winner_team_code, loser_team_code):
    """
    Set a team as the winner of a match.
    Assert the match exists.
    :param game_number: a game number
    :param winner_team_code: the winner team code
    :param loser_team_code: the loser team code
    :return: True if the match was updated, False if the match was not found
    """
    match = Match.objects(game_number=game_number, players_code__all=[winner_team_code, loser_team_code]).get()
    match.winner = winner_team_code
    match.loser = loser_team_code
    match.even = False
    match.recorded = True
    match.save()
    log.info("Team {} won the game {} against {}".format(winner_team_code, game_number, loser_team_code))


def set_even(game_number, team1_code, team2_code):
    """
    Set a match as equally won.
    Assert the match exists.
    :param game_number: a game number
    :param team1_code: a team code
    :param team2_code: another team code
    """
    match = Match.objects(game_number=game_number, players_code__all=[team1_code, team2_code]).get()
    match.winner = ""
    match.loser = ""
    match.even = True
    match.recorded = True
    match.save()
    log.info("Team {} and team {} are equally placed at the game {}".format(team1_code, team2_code, game_number))


def get_score(team_code):
    """
    Get the score of a given team
    :param team_code: a team code
    :return: a tuple (score, victories, evens, defeats)
    """
    evens = Match.objects(players_code=team_code, even=True).count()
    victories = Match.objects(winner=team_code).count()
    defeats = Match.objects(loser=team_code).count()
    score = victories * 2 + evens
    return score, victories, evens, defeats


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


def get_ranking_by_section(gender_filter=None):
    """
    Get the ranking by section. Scores is based on the average of all the teams of each section
    :param gender_filter: (optional) filter the ranking on a gender
    :return: list of tuples (section, mean score)
    """
    if gender_filter:
        sections = Team.objects(sex=gender_filter).distinct('section')
    else:
        sections = Team.objects().distinct('section')
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
        scores.append((team.code, team.section, get_score(team.code)[0]))
    return sorted(scores, key=lambda xyz: xyz[2], reverse=True)


def get_all_schedules():
    schedules = list()
    highest_time_game_number = Match.objects(time=model.match.get_match_quantity()).first().game_number
    for match in Game.objects(number=highest_time_game_number).get().matches:
        schedules.append(match.schedule)
    return schedules

