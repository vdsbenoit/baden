from mongoengine import *

import logging

from model import properties

log = logging.getLogger('default')


class Game(Document):
    circuit = IntField(required=True)
    number = IntField(required=True)
    name = StringField(max_length=100)
    players = ListField(IntField(), required=True)
    time = IntField(required=True)


def load_file(file_name):
    modified_games = list()
    circuit = 0
    with open(file_name, mode="r", encoding='utf-8-sig') as file:
        for line in file:
            line = line[:-1]
            cells = line.split(properties.LIST_SEPARATOR)
            if not circuit:
                circuit = int(cells[0])
                continue
            if cells[0].lower() == "id":
                continue
            for i in range(2, len(cells), 2):
                game = Game()
                game.circuit = circuit
                game.number = int(cells[0])
                game.name = cells[1]
                game.players.append(int(cells[i]))
                game.players.append(int(cells[i+1]))
                game.time = i/2
                modified_games.append(game)
    for game in modified_games:
        game.save()


def drop_games():
    """
    Drop games collection
    """
    Game.objects().delete()
