import hashlib
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
    hash = StringField(required=True, max_length=40)


def load_file(file_name):
    """
    Load team data from a file.
    The collection does not have to be cleared before loading from the file as the primary key is the identifier number.
    :param file_name: path to the file
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


def drop_teams():
    """
    Clean teams collection
    """
    Team.drop_collection()
