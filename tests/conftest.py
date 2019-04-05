from os.path import abspath, dirname, join

import pytest
from mongoengine import *

import main
from baden.model import game, team
from model import properties

TEST_DATA_DIR = abspath(join(dirname(__file__), "data"))


@pytest.fixture(scope="session")
def test_db():
    main.logger_setup()
    properties.parse_settings()
    db = connect("baden_test_db", host="localhost", port=27017)
    game.drop_games()
    team.drop_teams()
    return db
