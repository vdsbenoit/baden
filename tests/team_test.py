import os

import pytest

from baden.model import team
from baden.model import util
from exceptions import BadenException
from .conftest import TEST_DATA_DIR

GOOD_TEST_TEAM_FILE = os.path.join(TEST_DATA_DIR, "teams_right.csv")
WRONG_TEST_TEAM_FILE = os.path.join(TEST_DATA_DIR, "teams_wrong.csv")


def test_load_good_team_file(test_db):
    team.load_file(GOOD_TEST_TEAM_FILE)
    assert team.Team.objects.count() == 126, "There must be 126 teams"


def test_load_wrong_team_file(test_db):
    with pytest.raises(BadenException):
        team.load_file(WRONG_TEST_TEAM_FILE)


def test_distribution(test_db):
    util.distribute_numbers(False)
    for t in team.Team.objects(sex="F"):
        assert t.number > 0, "A female team received a number lower than 1 : {}".format(t.number)
        assert t.number < 43, "A female team received a number higher than 42 : {}".format(t.number)
    for t in team.Team.objects(sex="M"):
        assert t.number > 42, "A male team received a number lower than 1 : {}".format(t.number)
        assert t.number < 127, "A male team received a number higher than 42 : {}".format(t.number)
    util.distribute_numbers(True)


def test_add_score(test_db):
    team.add_victory("A1")
    team.add_even("A1")
    team.add_victory("A2")
    team.add_victory("A2")
    team.add_even("A3")
    team.add_even("A3")
    assert team.Team.objects(code="A1").first().score == 3, "Team 1 should have 3 points"
    assert team.Team.objects(code="A2").first().score == 4, "Team 2 should have 4 points"
    assert team.Team.objects(code="A3").first().score == 2, "Team 3 should have 2 points"


def test_reset_scores(test_db):
    team.add_victory("A1")
    team.add_even("A2")
    team.reset_scores()
    for t in team.Team.objects():
        assert t.score == 0, "Team {} still has a scores of {}".format(t.id, t.score)
        assert t.victories == 0, "Team {} still has {} victories".format(t.id, t.victories)
        assert t.evens == 0, "Team {} still has {} evens".format(t.id, t.s)


def test_drop_teams(test_db):
    team.drop_teams()
    team_amount = len(team.Team.objects())
    assert team_amount == 0, "There are still {} teams in the db after clean up".format(team_amount)
