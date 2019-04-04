import logging
from random import randint

from mongoengine import *

from exceptions import BadenException
from model import properties

log = logging.getLogger('default')


class Team(Document):
    id = IntField(primary_key=True)  # ne pas compléter automatiquement pour les réécritures
    number = IntField()  # pour la répartition dans les jeux
    code = StringField(unique=True, required=True, max_length=10)  # A1, A2, B1, ...
    unit = StringField(max_length=100, required=True)
    sex = StringField(max_length=1, required=True)  # M F
    games = ListField(ReferenceField('Game'))
    score = IntField(default=0)
    victories = IntField(default=0)
    evens = IntField(default=0)


def add_victory(code):
    team = Team.objects(code=code).first()
    team.victories += 1
    team.score += 2
    team.save()


def add_even(code):
    team = Team.objects(code=code).first()
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
                team.unit = cells[2]
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


def _shuffle(teams, floor_number):
    """
    Distribute random numbers to a list of Team objects, starting at number floor_number
    :param teams: list of Team objects
    :param floor_number: starting point for the number counter
    :return: None
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


def distribute_numbers(ignore_sex=True):
    """
    Distribute numbers to the teams.
    :param ignore_sex: mix sex across the distribution, else distribute the first numbers to the girls and then to the guys
    :return:
    """
    modified_teams = []
    if ignore_sex:
        modified_teams += _shuffle(Team.objects(), 1)
    else:
        modified_teams += _shuffle(Team.objects(sex="F"), 1)
        modified_teams += _shuffle(Team.objects(sex="M"), Team.objects(sex="F").count() + 1)
    for t1 in modified_teams:
        for t2 in modified_teams:
            if t1.number == t2.number and t1.id != t2.id:
                raise BadenException("There are two teams ({} & {}) with the same number ({}). Distribution not saved"
                                     .format(t1.id, t2.id, t1.number))
    for team in modified_teams:
        team.save()


def reset_scores():
    for team in Team.objects():
        team.score = 0
        team.victories = 0
        team.evens = 0
        team.save()


def drop_teams():
    Team.objects().delete()
