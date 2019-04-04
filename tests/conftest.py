import os

import pytest
from mongoengine import *

import main
from model import properties

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture(scope="session")
def test_db():
    main.logger_setup()
    properties.parse_settings()
    return connect("baden_test_db", host="localhost", port=27017)
