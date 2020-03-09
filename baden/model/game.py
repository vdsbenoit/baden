import hashlib
import itertools
import logging

from mongoengine import *

from model import properties
from model.match import Match

log = logging.getLogger("default")


class Game(Document):
    circuit = StringField(required=True, max_length=2)
    number = IntField(required=True)
    name = StringField(max_length=100)
    leader = StringField(max_length=100)
    hash = StringField(required=True, max_length=40)
    matches = ListField(ReferenceField(Match))


def load_file(file_name):
    """
    Load game data from a file.
    Do not forget to drop the collection before re-importing a same file!
    :param file_name: path to the file
    """
    circuit = ""
    schedules = dict()
    with open(file_name, mode="r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file):
            line = line[:-1]
            cells = line.split(properties.LIST_SEPARATOR)
            game = Game()
            if line_number == 0:
                circuit = cells[0]
                continue
            if line_number == 1:
                for i in range(3, len(cells), 2):
                    schedules[i] = (cells[i])
                continue
            game.number = int(cells[0])
            game.hash = hashlib.sha1("Baden {} Battle".format(cells[0]).encode()).hexdigest()
            game.name = cells[1]
            game.leader = cells[2]
            game.circuit = circuit
            for i in range(3, len(cells), 2):
                match = Match()
                match.time = (i - 1) / 2
                match.schedule = schedules[i]
                match.game_number = int(cells[0])
                match.players_number.append(int(cells[i]))
                match.players_number.append(int(cells[i + 1]))
                match.save()
                game.matches.append(match)
            game.save()


def create_schedule(nb_games, nb_circuits):
    """
    Generate a new schedule and save it in DB
    :param nb_games: amount of games per circuit (= amount of matches / team)
    :param nb_circuits: amount of circuits
    """
    if nb_games % 2 == 0:
        raise Exception("The game amount must be a odd value")
    if nb_circuits < 1:
        raise Exception("The circuit amount must be greater than 0")

    for circuit_idx in range(nb_circuits):
        teams = [i for i in range(1 + (nb_games * 2 * circuit_idx), 1 + nb_games * 2 * (circuit_idx + 1))]
        first_game = circuit_idx * nb_games + 1
        last_game = (circuit_idx + 1) * nb_games
        game_distribution = [i for i in itertools.chain(range(first_game, 1 + last_game), range(last_game, first_game - 1, -1))]

        # Game setup
        games = dict()
        for i in range(1, nb_games + 1):
            game = Game()
            game.number = (circuit_idx * nb_games) + i
            game.hash = hashlib.sha1(f"Baden {game.number} Battle".encode()).hexdigest()
            game.circuit = chr(circuit_idx + 98)
            games[game.number] = game

        # Match setup
        for i in range(nb_games):
            matches = dict()
            time = i + 1
            for j, game_number in enumerate(game_distribution):
                team = teams[(j + i * 2) % (2 * nb_games)]
                if game_number in matches:
                    match = matches[game_number]
                else:
                    match = Match()
                    games[game_number].matches.append(match)
                match.time = time
                match.game_number = game_number
                match.players_number.append(team)
                matches[game_number] = match
                match.save()
                games[game_number].save()
                # print("Time {} Game {} Team {}".format(time, game_number, team))


def validate_game_collection():
    """
    To perform AFTER the method model.service.set_player_codes() is called
    Assert the game setup complies with the following constraints:
        - a team cannot play against itself
        - a team cannot play against another team more one than once
        - a team cannot play a game more than once
        - a team cannot play two matches at the same time
        - a game cannot have the same hash as another game
    """
    duel_set_list = list()
    for time in range(1, len(Match.objects().distinct('time')) + 1):
        player_list = list()
        for m in Match.objects(time=time):
            players = m.players_number
            players_set = {players[0], players[1]}
            assert (
                players[0] not in player_list
            ), "Team {} plays two games at time {}".format(players[0], time)
            assert (
                players[1] not in player_list
            ), "Team {} plays two games at time {}".format(players[1], time)
            assert (
                players[0] != players[1]
            ), "Player {} plays against itself in game {} at time {}".format(players[0], m.game_number, time)
            assert (
                players_set not in duel_set_list
            ), "Team {} already played against team {}".format(players[0], players[1])
            player_list.append(players[0])
            player_list.append(players[1])
            duel_set_list.append(players_set)

    hash_list = list()

    for g in Game.objects():
        game_hash = g.hash
        assert game_hash not in hash_list, "Hash {} is used twice".format(game_hash)
        hash_list.append(game_hash)

        player_list = list()
        matches = Match.objects(game_number=g.number)
        for m in matches:
            players = m.players_number
            assert (
                players[0] not in player_list
            ), "Team {} plays twice the game {}".format(players[0], g.number)
            assert (
                players[1] not in player_list
            ), "Team {} plays twice the game {}".format(players[1], g.number)
            player_list.append(players[0])
            player_list.append(players[1])
