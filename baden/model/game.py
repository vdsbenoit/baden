from mongoengine import *

import logging

from model import properties

log = logging.getLogger('default')


class Game(Document):
    number = IntField(primary_key=True)  # ne pas compléter automatiquement pour les réécritures
    name = StringField(max_length=100)
    circuit = StringField(max_length=10)
    players1 = ListField(ReferenceField('Team'))
    players2 = ListField(ReferenceField('Team'))


def load_game_file(file_name):
    circuit = 0
    with open(file_name, mode="r", encoding='utf-8-sig') as file:
        for line in file:
            line = line[:-1]
            cells = line.split(properties.LIST_SEPARATOR)
            if not circuit:
                circuit = int(cells[0])
            if cells[0].lower() == "id":
                continue
            game = Game()
            game.circuit = circuit
            game.number = int(cells[0])
            game.name = cells[1]
            for i in range(2, len(cells), 2):
                game.players1.append(Team.objects(id=int(cells[i])))
                game.players2.append(Team.objects(id=int(cells[i+1])))
            game.save()


