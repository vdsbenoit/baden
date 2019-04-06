from os.path import abspath, dirname, join

import pytest
from mongoengine import *

import main
from baden.model import game, team
from model import properties

TEST_DATA_DIR = abspath(join(dirname(__file__), "data"))
GOOD_TEST_GAME_FILE = join(TEST_DATA_DIR, "distribution_right.csv")
GOOD_TEST_TEAM_FILE = join(TEST_DATA_DIR, "teams_right.csv")


@pytest.fixture(scope="session")
def db():
    main.logger_setup()
    properties.parse_settings()
    db = connect("baden_test_db", host="localhost", port=27017)
    return db


@pytest.fixture(scope="function")
def empty_db(db):
    game.drop_games()
    team.drop_teams()
    return db


@pytest.fixture(scope="function")
def clean_db(db):
    game.drop_games()
    team.drop_teams()
    game.load_file(GOOD_TEST_GAME_FILE)
    team.load_file(GOOD_TEST_TEAM_FILE)
    return db

