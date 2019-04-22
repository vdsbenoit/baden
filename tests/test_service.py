import hashlib

import pytest
from mongoengine import DoesNotExist

from baden.model import service
from exceptions import BadenException
from model.game import Game
from model.team import Team
from tests.conftest import SCHEDULES


def test_is_team(distributed_clean_db):
    assert service.is_team("A1")
    assert service.is_team("B2")
    assert service.is_team("C3")
    assert service.is_team("D4")
    assert not service.is_team("A6")
    assert not service.is_team("2A")
    assert not service.is_team("1")
    assert not service.is_team("A")
    assert not service.is_team("")


def test_is_game(distributed_clean_db):
    assert service.is_game(1)
    assert service.is_game(10)
    assert service.is_game(21)
    assert service.is_game("1")
    assert not service.is_game("0")
    assert not service.is_game(0)
    assert not service.is_game(-1)
    assert not service.is_game(64)


def test_get_game_name(distributed_clean_db):
    assert service.get_game_name(1) == "Jeu 1", "Wrong game name"
    assert service.get_game_name(21) == "Jeu 21", "Wrong game name"
    assert service.get_game_name(25) == "Jeu 25", "Wrong game name"
    assert service.get_game_name(50) == "Jeu 50", "Wrong game name"
    assert service.get_game_name(63) == "Jeu 63", "Wrong game name"


def test_get_section(distributed_clean_db):
    assert service.get_section("A1") == "Lutin St Symphorien Villers-Saint-Ghislain", "Wrong section name"
    assert service.get_section("J3") == "louveteaux Saintes", "Wrong section name"
    assert service.get_section("X2") == "Louveteaux Lessines", "Wrong section name"


def test_resolve_hash(distributed_clean_db):
    game_numbers = [1, 20, 23, 63]
    team_codes = ["A1", "B3", "J4", "X3"]
    for number in game_numbers:
        assert service.resolve_hash(hashlib.sha1("Baden {} Battle".format(number).encode()).hexdigest()) == number
    for code in team_codes:
        assert service.resolve_hash(hashlib.sha1("Baden {} Battle".format(code).encode()).hexdigest()) == code
    with pytest.raises(BadenException) as e:
        hash_value = hashlib.sha1("Baden {} Battle".format(0).encode()).hexdigest()
        service.resolve_hash(hash_value)
        assert "No teams nor games found for hash {}".format(hash_value) in str(e.value)
    with pytest.raises(BadenException) as e:
        hash_value = hashlib.sha1("Baden {} Battle".format("Z2").encode()).hexdigest()
        service.resolve_hash(hash_value)
        assert "No teams nor games found for hash {}".format(hash_value) in str(e.value)


def test_get_opponent_code(distributed_clean_db):
    assert service.get_opponent_code(1, "A1") == "I3", "A1 is supposed to play against I3 at game 1"
    assert service.get_opponent_code(14, "I1") == "C3", "I1 is supposed to play against C3 at game 14"
    assert service.get_opponent_code(14, "C3") == "I1", "I1 is supposed to play against C3 at game 14"


def check_games(team_code, expected_game_numbers):
    matches = service.get_matches(team_code)
    for i, match in enumerate(matches):
        assert match.game_number == expected_game_numbers[i], \
            "Team {} is supposed to play game {} at time {}. Got {} instead".format(
                team_code, expected_game_numbers[i], i+1, match.game_number)


def test_get_games(distributed_clean_db):
    check_games("A1", [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 21, 19, 17, 15, 13, 11, 9, 7, 5, 3])
    check_games("B5", [10, 8, 6, 4, 2, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 20, 18, 16, 14, 12])
    check_games("D5", [21, 19, 17, 15, 13, 11, 9, 7, 5, 3, 1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])


def check_players(game_number, expected_players):
    matches = Game.objects(number=game_number).get().matches
    for i, match in enumerate(matches):
        expected_player_number_set = {expected_players[i*2], expected_players[i*2+1]}
        actual_player_numbers_set = {*match.players_number}
        assert actual_player_numbers_set == expected_player_number_set, \
            "At time {} players {} and {} are supposed to play. Got {} and {} instead".format(
                i+1,
                expected_players[i * 2],
                expected_players[i * 2 + 1],
                match.players_number[0],
                match.players_number[1])


def test_get_players(distributed_clean_db):
    check_players(1, [1,42,3,2,5,4,7,6,9,8,11,10,13,12,15,14,17,16,19,18,21,20,23,22,25,24,27,26,29,28,31,30,33,32,35,34,37,36,39,38,41,40])
    check_players(10, [10,33,12,35,14,37,16,39,18,41,20,1,22,3,24,5,26,7,28,9,30,11,32,13,34,15,36,17,38,19,40,21,42,23,2,25,4,27,6,29,8,31])
    check_players(21, [21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])


def test_set_winner(distributed_clean_db):
    service.set_winner(1, "A1", "I3"), "No matches found for game 1 with team A1 and team I3"
    service.set_winner(2, "A3", "B1"), "No matches found for game 3 with team A3 and team B1"
    with pytest.raises(DoesNotExist):
        service.set_winner(2, "A1", "I3"), "This combination should not exists"
    with pytest.raises(DoesNotExist):
        service.set_winner(3, "A0", "I3"), "Team A0 should not exist"
    with pytest.raises(DoesNotExist):
        service.set_winner(0, "A0", "I3"), "Game 0 should not exist"


def test_set_even(distributed_clean_db):
    service.set_winner(11, "D5", "I3"), "No matches found for game 1 with team A1 and team I3"
    service.set_winner(2, "D4", "D1"), "No matches found for game 3 with team A3 and team B1"
    with pytest.raises(DoesNotExist):
        service.set_winner(3, "B2", "I3"), "This combination should not exists"
    with pytest.raises(DoesNotExist):
        service.set_winner(3, "A0", "I3"), "Team A0 should not exist"
    with pytest.raises(DoesNotExist):
        service.set_winner(0, "A0", "I3"), "Game 0 should not exist"


def test_score(distributed_clean_db):
    service.set_winner(1, "A1", "I3")
    service.set_even(2, "A1", "A4")
    service.set_winner(1, "A2", "A3")
    service.set_winner(2, "A2", "I2")
    service.set_even(2, "A3", "B1")
    service.set_even(3, "A3", "I1")
    assert service.get_score("A1")[0] == 3, "Team A1 should have 3 points"
    assert service.get_score("A1")[1] == 1, "Team A1 should have 1 victory"
    assert service.get_score("A1")[2] == 1, "Team A1 should have 1 even"
    assert service.get_score("A2")[0] == 4, "Team A2 should have 4 points"
    assert service.get_score("A2")[1] == 2, "Team A2 should have 2 victories"
    assert service.get_score("A2")[2] == 0, "Team A2 should have 0 evens"
    assert service.get_score("A3")[0] == 2, "Team A3 should have 2 points"
    assert service.get_score("A3")[1] == 0, "Team A3 should have 0 victories"
    assert service.get_score("A3")[2] == 2, "Team A3 should have 2 evens"
    assert service.get_score("A3")[3] == 1, "Team A3 should have 1 defeat"
    assert service.get_score("A4")[0] == 1, "Team A4 should have 1 points"
    assert service.get_score("A4")[1] == 0, "Team A4 should have 0 victories"
    assert service.get_score("A4")[2] == 1, "Team A4 should have 1 even"
    a_section = Team.objects(code="A1").first().section
    assert service.get_section_score(a_section) == 10/5, "{} mean score should be {}".format(a_section, 10/5)

    service.set_winner(24, "J3", "Q1")
    service.set_even(22, "J3", "J2")
    service.set_winner(29, "J5", "M4")
    service.set_winner(30, "J5", "O2")
    service.set_even(29, "J6", "O5")
    service.set_even(30, "J6", "M7")
    assert service.get_score("J3")[0] == 3, "Team J3 should have 3 points"
    assert service.get_score("J3")[1] == 1, "Team J3 should have 1 victory"
    assert service.get_score("J3")[2] == 1, "Team J3 should have 1 even"
    assert service.get_score("J5")[0] == 4, "Team J5 should have 4 points"
    assert service.get_score("J5")[1] == 2, "Team J5 should have 2 victories"
    assert service.get_score("J5")[2] == 0, "Team J5 should have 0 evens"
    assert service.get_score("J6")[0] == 2, "Team J6 should have 2 points"
    assert service.get_score("J6")[1] == 0, "Team J6 should have 0 victories"
    assert service.get_score("J6")[2] == 2, "Team J6 should have 2 evens"
    assert service.get_score("J2")[0] == 1, "Team J2 should have 1 points"
    assert service.get_score("J2")[1] == 0, "Team J2 should have 0 victories"
    assert service.get_score("J2")[2] == 1, "Team J2 should have 1 even"
    j_section = Team.objects(code="J1").first().section
    assert service.get_section_score(j_section) == 10 / 6, "{} mean score should be {}".format(j_section, 10 / 6)

    global_section_ranking = service.get_ranking_by_section()
    assert global_section_ranking[0][0] == a_section, "{} should be first in the ranking".format(a_section)
    assert global_section_ranking[1][0] == j_section, "{} should be second in the ranking".format(j_section)

    assert service.get_ranking_by_section("F")[0][0] == a_section, "{} should be first in the girls ranking".format(a_section)
    assert service.get_ranking_by_section("M")[0][0] == j_section, "{} should be first in the boys  ranking".format(j_section)

    service.set_winner(27, "J5", "L6")
    service.set_winner(32, "J3", "M8")
    global_ranking = service.get_ranking()
    assert global_ranking[0][0] == "J5", "Global first team should be J5"
    assert global_ranking[1][0] == "J3", "Global second team should be J3"
    assert global_ranking[2][0] == "A2", "Global third team should be A2"
    assert global_ranking[3][0] == "A1", "Global fourth team should be A1"

    boys_ranking = service.get_ranking("M")
    assert boys_ranking[0][0] == "J5", "Boys first team should be J5"
    assert boys_ranking[1][0] == "J3", "Boys second team should be J3"
    assert boys_ranking[2][0] == "J6", "Boys third team should be J6"
    assert boys_ranking[3][0] == "J2", "Boys fourth team should be J2"

    girls_ranking = service.get_ranking("F")
    assert girls_ranking[0][0] == "A2", "Girls first team should be A2"
    assert girls_ranking[1][0] == "A1", "Girls second team should be A1"
    assert girls_ranking[2][0] == "A3", "Girls third team should be A3"
    assert girls_ranking[3][0] == "A4", "Girls fourth team should be A4"


def test_get_all_schedules(distributed_clean_db):
    assert service.get_all_schedules() == SCHEDULES, "Schedules do not match"

