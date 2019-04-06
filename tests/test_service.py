import os

import pytest

from baden.model import game, service, team
from .conftest import TEST_DATA_DIR


def test_distribution(clean_db):
    service.distribute_numbers(False)
    for t in team.Team.objects(sex="F"):
        assert t.number > 0, "A female team received a number lower than 1 : {}".format(t.number)
        assert t.number < 43, "A female team received a number higher than 42 : {}".format(t.number)
    for t in team.Team.objects(sex="M"):
        assert t.number > 42, "A male team received a number lower than 1 : {}".format(t.number)
        assert t.number < 127, "A male team received a number higher than 42 : {}".format(t.number)
    service.distribute_numbers(True)

