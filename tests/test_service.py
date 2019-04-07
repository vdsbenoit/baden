import os

import pytest

from baden.model import game, service, team
from .conftest import TEST_DATA_DIR


def distribute_ascending_team_numbers():
    """
    Distribute team numbers in an ascending way.
    """
    iterator = 1
    for t in team.Team.objects().order_by("code"):
        t.number = iterator
        iterator += 1
        t.save()


def check_games(team_code, expected_game_numbers):
    games = service.get_games(team_code)
    for i in range(len(games)):
        assert games[i].number == expected_game_numbers[i], \
            "Team {} is supposed to play game {} at time {}. Got {} instead".format(
                team_code, expected_game_numbers[i], i+1, games[i].number)


def test_get_games(clean_db):
    distribute_ascending_team_numbers()
    check_games("A1", [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 21, 19, 17, 15, 13, 11, 9, 7, 5, 3])
    check_games("B5", [10, 8, 6, 4, 2, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 20, 18, 16, 14, 12])
    check_games("D5", [21, 19, 17, 15, 13, 11, 9, 7, 5, 3, 1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])


def check_players(game_number, expected_players):
    player_list = service.get_players(game_number)
    for i in range(len(player_list)):
        expected_player_number_set = {expected_players[i*2], expected_players[i*2+1]}
        actual_player_numbers_set = {player_list[i][0].number, player_list[i][1].number}
        assert actual_player_numbers_set == expected_player_number_set, \
            "At time {} players {} and {} are supposed to play. Got {} and {} instead".format(
                i+1,
                expected_players[i * 2],
                expected_players[i * 2 + 1],
                player_list[i][0].number,
                player_list[i][1].number)


def test_get_players(clean_db):
    distribute_ascending_team_numbers()
    check_players(1, [1,42,3,2,5,4,7,6,9,8,11,10,13,12,15,14,17,16,19,18,21,20,23,22,25,24,27,26,29,28,31,30,33,32,35,34,37,36,39,38,41,40])
    check_players(10, [10,33,12,35,14,37,16,39,18,41,20,1,22,3,24,5,26,7,28,9,30,11,32,13,34,15,36,17,38,19,40,21,42,23,2,25,4,27,6,29,8,31])
    check_players(21, [21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])


def test_distribution(clean_db):
    service.distribute_numbers(False)
    for t in team.Team.objects(sex="F"):
        assert t.number > 0, "A female team received a number lower than 1 : {}".format(t.number)
        assert t.number < 43, "A female team received a number higher than 42 : {}".format(t.number)
    for t in team.Team.objects(sex="M"):
        assert t.number > 42, "A male team received a number lower than 42 : {}".format(t.number)
        assert t.number < 127, "A male team received a number higher than 126 : {}".format(t.number)
    service.distribute_numbers(True)
    for t in team.Team.objects():
        assert t.number > 0, "A male team received a number lower than 0 : {}".format(t.number)
        assert t.number < 127, "A male team received a number higher than 126 : {}".format(t.number)
