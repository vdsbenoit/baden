import os

import pytest

from baden.model import game
from exceptions import BadenException
from .conftest import TEST_DATA_DIR

GOOD_TEST_GAME_FILE = os.path.join(TEST_DATA_DIR, "distribution_good.csv")
WRONG_TEST_GAME_FILE = os.path.join(TEST_DATA_DIR, "")


def test_load_good_team_file(test_db):
    game.load_file(GOOD_TEST_GAME_FILE)

