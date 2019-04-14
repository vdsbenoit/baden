import os

import pytest

from baden.model import team
from exceptions import BadenException
from .conftest import TEST_DATA_DIR, GOOD_TEST_TEAM_FILE

WRONG_TEST_TEAM_FILE = os.path.join(TEST_DATA_DIR, "teams_wrong.csv")


def test_load_good_team_file(empty_db):
    team.load_file(GOOD_TEST_TEAM_FILE)
    assert team.Team.objects.count() == 126, "There must be 126 teams"


def test_load_wrong_team_file(empty_db):
    with pytest.raises(BadenException):
        team.load_file(WRONG_TEST_TEAM_FILE)


def test_drop_teams(clean_db):
    team.drop_teams()
    team_amount = len(team.Team.objects())
    assert team_amount == 0, "There are still {} teams in the db after clean up".format(team_amount)
