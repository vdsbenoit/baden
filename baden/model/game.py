from mongoengine import *

import logging

from model import properties

log = logging.getLogger('default')


class Game(Document):
    id = IntField(primary_key=True)  # ne pas compléter automatiquement pour les réécritures
    name = StringField(max_length=100)
    circuit = IntField
    players1 = ListField(IntField())
    players2 = ListField(IntField())


def load_file(file_name):
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
            game = Game()
            game.circuit = circuit
            game.id = int(cells[0])
            game.name = cells[1]
            for i in range(2, len(cells), 2):
                game.players1.append(int(cells[i]))
                game.players2.append(int(cells[i+1]))
            game.save()


def drop_games():
    Game.objects().delete()
