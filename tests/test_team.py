import os

import pytest

from baden.model import team
from exceptions import BadenException
from .conftest import TEST_DATA_DIR, GOOD_TEST_TEAM_FILE

WRONG_TEST_TEAM_FILE = os.path.join(TEST_DATA_DIR, "teams_wrong.csv")


def test_load_good_team_file(empty_db):
    team.load_file(GOOD_TEST_TEAM_FILE, False)
    assert team.Team.objects.count() == 126, "There must be 126 teams"


def test_load_good_team_file_and_shuffle(empty_db):
    team.load_file(GOOD_TEST_TEAM_FILE, True)
    assert team.Team.objects.count() == 126, "There must be 126 teams"


def test_load_wrong_team_file(empty_db):
    with pytest.raises(BadenException):
        team.load_file(WRONG_TEST_TEAM_FILE, False)


def test_distribution(empty_db):
    team.load_file(GOOD_TEST_TEAM_FILE, True, False)
    for t in team.Team.objects(sex="M"):
        assert t.number > 0, "A male team received a number lower than 1 : {}".format(t.number)
        assert t.number <= 84, "A male team received a number higher than 42 : {}".format(t.number)
    for t in team.Team.objects(sex="F"):
        assert t.number > 84, "A female team received a number lower than 42 : {}".format(t.number)
        assert t.number <= 126, "A female team received a number higher than 126 : {}".format(t.number)
    team.distribute_numbers(True)
    for t in team.Team.objects():
        assert t.number > 0, "A team received a number lower than 0 : {}".format(t.number)
        assert t.number <= 126, "A team received a number higher than 126 : {}".format(t.number)
