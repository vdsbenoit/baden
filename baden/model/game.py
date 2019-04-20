import hashlib

from mongoengine import *

import logging

from model import properties

log = logging.getLogger("default")


class Game(Document):
    circuit = StringField(required=True, max_length=2)
    number = IntField(required=True)
    name = StringField(max_length=100)
    leader = StringField(max_length=100)
    players = ListField(IntField(), required=True)  # player numbers
    winner = IntField(default=-1)
    time = IntField(required=True)
    hash = StringField(required=True, max_length=40)


def load_file(file_name):
    """
    Load game data from a file.
    Do not forget to drop the collection before re-importing a same file!
    :param file_name: path to the file
    """
    modified_games = list()
    circuit = ""
    with open(file_name, mode="r", encoding="utf-8-sig") as file:
        for line in file:
            line = line[:-1]
            cells = line.split(properties.LIST_SEPARATOR)
            if not circuit:
                circuit = cells[0]
                continue
            if cells[0].lower() == "jeu":
                continue
            for i in range(3, len(cells), 2):
                game = Game()
                game.circuit = circuit
                game.number = int(cells[0])
                game.hash = hashlib.sha1(
                    "Baden {} Battle".format(cells[0]).encode()
                ).hexdigest()
                game.name = cells[1]
                game.leader = cells[2]
                game.players.append(int(cells[i]))
                game.players.append(int(cells[i + 1]))
                game.time = (i - 1) / 2
                modified_games.append(game)
    for game in modified_games:
        game.save()


def validate_game_collection():
    """
    Assert the game setup complies with the following constraints:
        - a team cannot play against itself
        - a team cannot play against another team more one than once
        - a team cannot play a game more than once
        - a team cannot play two games at the same time
        - a game cannot have the same hash as another game
    """
    duel_set_list = list()
    for time in range(1, len(Game.objects().distinct('time')) + 1):
        player_list = list()
        for g in Game.objects(time=time):
            players = g.players
            players_set = {players[0], players[1]}
            assert (
                players[0] not in player_list
            ), "Team {} plays two games at time {}".format(players[0], time)
            assert (
                players[1] not in player_list
            ), "Team {} plays two games at time {}".format(players[1], time)
            assert (
                players[0] != players[1]
            ), "Player {} plays against itself in game {} at time {}".format(
                players[0], g.number, time
            )
            assert (
                players_set not in duel_set_list
            ), "Team {} already played against team {}".format(players[0], players[1])
            player_list.append(players[0])
            player_list.append(players[1])
            duel_set_list.append(players_set)

    hash_list = list()

    for game_number in range(1, len(Game.objects().distinct('number')) + 1):
        player_list = list()
        games = Game.objects(number=game_number)
        game_hash = games.first().hash
        assert game_hash not in hash_list, "Hash {} is used twice".format(game_hash)
        hash_list.append(game_hash)
        for g in games:
            players = g.players
            assert (
                players[0] not in player_list
            ), "Team {} plays twice the game {}".format(players[0], game_number)
            assert (
                players[1] not in player_list
            ), "Team {} plays twice the game {}".format(players[1], game_number)
            player_list.append(players[0])
            player_list.append(players[1])


def get_round_quantity():
    return len(Game.objects().distinct("time"))


def get_gathered_point_amount(time):
    return Game.objects(time=time, winner__gte=0).count()


def reset_scores():
    """
    Reset all the scores
    """
    for game in Game.objects():
        game.winner = -1
        game.save()


def drop_games():
    """
    Drop games collection
    """
    Game.drop_collection()
