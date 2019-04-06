import os

import pytest

from baden.model import game
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
    with pytest.raises(AssertionError) as exception_info:
        game.validate_game_collection()
    assert "Player 14 plays against itself in game 10 at time 3" in str(exception_info.value)


def test_player_plays_against_same_opponent_twice(empty_db):
    game.load_file(TEST_GAME_FILE_SAME_OPPONENT)
    with pytest.raises(AssertionError) as exception_info:
        game.validate_game_collection()
    assert "Team 9 already played against team 38" in str(exception_info.value)


def test_player_plays_game_twice(empty_db):
    game.load_file(TEST_GAME_FILE_TWICE_GAME)
    with pytest.raises(AssertionError) as exception_info:
        game.validate_game_collection()
    assert "Team 1 plays twice the game 1" in str(exception_info.value)


def test_player_plays_time_twice(empty_db):
    game.load_file(TEST_GAME_FILE_TWICE_TIME)
    with pytest.raises(AssertionError) as exception_info:
        game.validate_game_collection()
    assert "Team 6 plays two games at time 2" in str(exception_info.value)

