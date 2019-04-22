import hashlib
import logging
from random import randint

from mongoengine import *

from exceptions import BadenException
from model import properties
from model.match import Match

log = logging.getLogger('default')


class Team(Document):
    id = IntField(primary_key=True)  # do not fill automatically in order to re-write teams
    number = IntField()  # to randomly distribute the teams across the game
    code = StringField(unique=True, required=True, max_length=10)  # A1, A2, B1, ...
    section = StringField(max_length=100, required=True)
    sex = StringField(max_length=1, required=True)  # M F
    hash = StringField(required=True, unique=True, max_length=40)
    matches = ListField(ReferenceField(Match))


def set_matches():
    modified_teams = list()
    for t in Team.objects():
        for m in Match.objects(players_code=t.code).order_by('time'):
            t.matches.append(m)
        modified_teams.append(t)
    for t in modified_teams:
        t.save()


def distribute_numbers(ignore_sex):
    """
    Distribute numbers to the teams.
    :param ignore_sex: cf. load_file doc
    """
    def shuffle(teams, floor_number):
        """
        Distribute random numbers to a list of Team objects, starting at number floor_number
        :param teams: Team QuerySet
        :param floor_number: starting point for the number counter
        :return the list of modified teams
        """
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

    modified_teams = []
    if ignore_sex:
        shuffle(Team.objects(), 1)
    else:
        shuffle(Team.objects(sex="M"), 1)
        shuffle(Team.objects(sex="F"), len(modified_teams) + 1)
    for t1 in modified_teams:
        for t2 in modified_teams:
            if t1.number == t2.number and t1.id != t2.id:
                raise BadenException("There are two teams ({} & {}) with the same number ({}). Distribution not saved"
                                     .format(t1.id, t2.id, t1.number))
    for team in modified_teams:
        team.save()


def load_file(file_name, shuffle, ignore_sex=False):
    """
    Load team data from a file.
    :param file_name: path to the file
    The collection does not have to be cleared before loading from the file as the primary key is the identifier number.
    :param shuffle: shuffle teams in the games
    :param ignore_sex: mix sexes across the distribution, else distribute the first numbers to the guys and then to the girls
    """
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
                team.hash = hashlib.sha1("Baden {} Battle".format(team.code).encode()).hexdigest()
                modified_teams.append(team)
                nb_iterator += 1
            letter_iterator += 1
            if letter_iterator > 25:
                raise BadenException("The software does not handle more than 26 sections for now.")
    for team in modified_teams:
        team.save()
    if shuffle:
        distribute_numbers(ignore_sex)
    else:
        iterator = 1
        for t in Team.objects().order_by("code"):
            t.number = iterator
            iterator += 1
            t.save()
