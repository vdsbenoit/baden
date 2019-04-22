from os.path import abspath, dirname, join

import pytest
from mongoengine import *

import controller.util
from baden.model import game, team
from model import properties, service

TEST_DATA_DIR = abspath(join(dirname(__file__), "data"))
GOOD_TEST_GAME_FILE = join(TEST_DATA_DIR, "distribution_right.csv")
GOOD_TEST_TEAM_FILE = join(TEST_DATA_DIR, "teams_right.csv")


def pytest_addoption(parser):
    parser.addoption(
        "--realdb", action="store_true", default=False,
        help="Perform tests on a real DB, else on a mock DB"
    )


@pytest.fixture(scope="session")
def db(request):
    """
    Connect to test database.
    Use a real db local if --realdb option is used, else a mongomock db
    """
    controller.util.logger_setup()
    properties.parse_settings()
    if request.config.getoption("--realdb"):
        db = connect("baden_test_db", host=properties.DB_HOST, port=properties.DB_PORT)
        print("Connected to local database")
    else:
        db = connect('mongoenginetest', host='mongomock://localhost')
        print("Connected to mock database")
    return db


@pytest.fixture(scope="function")
def empty_db(db):
    """
    Empty database
    """
    team.Team.drop_collection()
    game.Game.drop_collection()
    game.Match.drop_collection()
    return db


@pytest.fixture(scope="function")
def distributed_clean_db(empty_db):
    """
    Distribute team numbers in an ascending way.
    """
    team.load_file(GOOD_TEST_TEAM_FILE, False)
    game.load_file(GOOD_TEST_GAME_FILE)
    game.load_file(join(TEST_DATA_DIR, "distribution2.csv"))
    game.load_file(join(TEST_DATA_DIR, "distribution3.csv"))
    service.set_player_codes()
    team.set_matches()
    return empty_db

