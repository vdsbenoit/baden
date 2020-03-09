from os.path import abspath, dirname, join

import pytest
from mongoengine import *

import controller.util
from baden.model import game, team
from model import properties, service

TEST_DATA_DIR = abspath(join(dirname(__file__), "data"))
GOOD_TEST_GAME_FILE = join(TEST_DATA_DIR, "distribution_right.csv")
GOOD_TEST_TEAM_FILE = join(TEST_DATA_DIR, "teams_right.csv")
SCHEDULES = ["10h08-10h23", "10h25-10h40", "10h42-10h57", "10h59-11h14", "11h16-11h31", "11h33-11h48", "11h50-12h05",
             "12h07-12h22", "12h24-12H39", "13h38-13h53", "13h55-14h10", "14h12-14h27", "14h29-14h44", "14h46-15h01",
             "15H03-15h18", "15h20-15h35", "15h37-15h52", "15h54-16h09", "16h11-16h26", "16h28-16h43", "16h45-17h00"]


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
    game.create_schedule(21, 3)
    # game.load_file(GOOD_TEST_GAME_FILE)
    # game.load_file(join(TEST_DATA_DIR, "distribution2.csv"))
    # game.load_file(join(TEST_DATA_DIR, "distribution3.csv"))
    service.set_player_codes()
    team.set_matches()
    return empty_db

