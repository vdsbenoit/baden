import os

import pytest

from baden.model import game
from model import service
from .conftest import TEST_DATA_DIR, GOOD_TEST_GAME_FILE

TEST_GAME_FILE_SAME_PLAYER = os.path.join(TEST_DATA_DIR, "distribution_same_player.csv")
TEST_GAME_FILE_SAME_OPPONENT = os.path.join(TEST_DATA_DIR, "distribution_same_opponent.csv")
TEST_GAME_FILE_TWICE_GAME = os.path.join(TEST_DATA_DIR, "distribution_twice_game.csv")
TEST_GAME_FILE_TWICE_TIME = os.path.join(TEST_DATA_DIR, "distribution_twice_time.csv")


def test_load_good_team_file(empty_db):
    game.load_file(GOOD_TEST_GAME_FILE)
    game.validate_game_collection()


def test_player_plays_against_itself(empty_db):
    game.load_file(TEST_GAME_FILE_SAME_PLAYER)
    with pytest.raises(AssertionError) as e:
        game.validate_game_collection()
    assert "Player 14 plays against itself in game 10 at time 3" in str(e.value)


def test_player_plays_against_same_opponent_twice(empty_db):
    game.load_file(TEST_GAME_FILE_SAME_OPPONENT)
    with pytest.raises(AssertionError) as e:
        game.validate_game_collection()
    assert "Team 9 already played against team 38" in str(e.value)


def test_player_plays_game_twice(empty_db):
    game.load_file(TEST_GAME_FILE_TWICE_GAME)
    with pytest.raises(AssertionError) as e:
        game.validate_game_collection()
    assert "Team 1 plays twice the game 1" in str(e.value)


def test_player_plays_time_twice(empty_db):
    game.load_file(TEST_GAME_FILE_TWICE_TIME)
    with pytest.raises(AssertionError) as e:
        game.validate_game_collection()
    assert "Team 6 plays two games at time 2" in str(e.value)


def test_get_round_quantity(clean_db):
    assert game.get_round_quantity() == 21, "There should be 21 rounds"


def test_reset_scores(distributed_clean_db):
    service.set_winner(1, "A1", "I3")
    service.set_even(2, "A1", "A4")
    service.set_winner(1, "A2", "A3")
    service.set_winner(2, "A2", "I2")
    service.set_even(2, "A3", "B1")
    service.set_even(3, "A3", "I1")
    game.reset_scores()
    assert service.get_score("A1")[0] == 0, "Team A1 should have 0 points"
    assert service.get_score("A1")[1] == 0, "Team A1 should have 0 victories"
    assert service.get_score("A1")[2] == 0, "Team A1 should have 0 evens"
    assert service.get_score("A2")[0] == 0, "Team A2 should have 0 points"
    assert service.get_score("A2")[1] == 0, "Team A2 should have 0 victories"
    assert service.get_score("A2")[2] == 0, "Team A2 should have 0 evens"
    assert service.get_score("A3")[0] == 0, "Team A3 should have 0 points"
    assert service.get_score("A3")[1] == 0, "Team A3 should have 0 victories"
    assert service.get_score("A3")[2] == 0, "Team A3 should have 0 evens"
    assert service.get_score("A4")[0] == 0, "Team A4 should have 0 points"
    assert service.get_score("A4")[1] == 0, "Team A4 should have 0 victories"
    assert service.get_score("A4")[2] == 0, "Team A4 should have 0 evens"
