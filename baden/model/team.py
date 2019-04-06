import logging

from mongoengine import *

from exceptions import BadenException
from model import properties

log = logging.getLogger('default')


class Team(Document):
    id = IntField(primary_key=True)  # do not fill automatically in order to re-write teams
    number = IntField()  # to randomly distribute the teams across the game
    code = StringField(unique=True, required=True, max_length=10)  # A1, A2, B1, ...
    section = StringField(max_length=100, required=True)
    sex = StringField(max_length=1, required=True)  # M F
    score = IntField(default=0)
    victories = IntField(default=0)
    evens = IntField(default=0)


def add_victory(code):
    """
    Add a victory to a team
    :param code: team code
    """
    team = Team.objects(code=code).get()
    team.victories += 1
    team.score += 2
    team.save()


def add_even(code):
    """
    Add an even to a team
    :param code: team code
    """
    team = Team.objects(code=code).get()
    team.evens += 1
    team.score += 1
    team.save()


def load_file(file_name):
    modified_teams = list()
    alphabet = []
    for letter in range(65, 91):
        alphabet.append(chr(letter))
    nb_iterator = 1
    letter_iterator = 0
    with open(file_name, mode="r", encoding='utf-8-sig') as file:
        for line in file.readlines():
            line = line[:-1]
            cells = line.split(properties.LIST_SEPARATOR)
            team_amount = int(cells[1])
            for i in range(team_amount):
                team = Team()
                team.id = nb_iterator
                team.section = cells[2]
                team.sex = cells[0]
                if cells[0] not in "MF":
                    raise BadenException("Gender field must be M or F")
                team.code = "{}{}".format(alphabet[letter_iterator], i + 1)
                modified_teams.append(team)
                nb_iterator += 1
            letter_iterator += 1
            if letter_iterator > 25:
                raise BadenException("The software does not handle more than 26 sections for now.")
    for team in modified_teams:
        team.save()


def reset_scores():
    """
    Reset the scores of all the teams
    """
    for team in Team.objects():
        team.score = 0
        team.victories = 0
        team.evens = 0
        team.save()


def drop_teams():
    """
    Clean teams collection
    """
    Team.objects().delete()
