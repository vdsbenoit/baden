from baden.model import match
from baden.model import service


def test_get_match_quantity(distributed_clean_db):
    assert match.get_match_quantity() == 21, "There should be 21 matches"


def test_recorded_score_amount(distributed_clean_db):
    service.set_winner(1, "A1", "I3")  # time 1
    service.set_even(2, "A1", "A4")  # time 2
    service.set_winner(1, "A2", "A3")  # time 2
    service.set_winner(2, "A2", "I2")  # time 1
    service.set_even(2, "A3", "B1")  # time 3
    service.set_even(3, "A3", "I1")  # time 1
    assert match.get_recorded_scores_amount(1) == 3, "There should be 3 recorded scores at time 1"
    assert match.get_recorded_scores_amount(2) == 2, "There should be 2 recorded scores at time 2"
    assert match.get_recorded_scores_amount(3) == 1, "There should be 1 recorded scores at time 3"


def test_reset_scores(distributed_clean_db):
    service.set_winner(1, "A1", "I3")
    service.set_even(2, "A1", "A4")
    service.set_winner(1, "A2", "A3")
    service.set_winner(2, "A2", "I2")
    service.set_even(2, "A3", "B1")
    service.set_even(3, "A3", "I1")
    match.reset_scores()
    assert service.get_score("A1")[0] == 0, "Team A1 should have 0 points"
    assert service.get_score("A1")[1] == 0, "Team A1 should have 0 victories"
    assert service.get_score("A1")[2] == 0, "Team A1 should have 0 evens"
    assert service.get_score("A2")[0] == 0, "Team A2 should have 0 points"
    assert service.get_score("A2")[1] == 0, "Team A2 should have 0 victories"
    assert service.get_score("A2")[2] == 0, "Team A2 should have 0 evens"
    assert service.get_score("A3")[0] == 0, "Team A3 should have 0 points"
    assert service.get_score("A3")[1] == 0, "Team A3 should have 0 victories"
    assert service.get_score("A3")[2] == 0, "Team A3 should have 0 evens"
    assert service.get_score("A4")[0] == 0, "Team A4 should have 0 points"
    assert service.get_score("A4")[1] == 0, "Team A4 should have 0 victories"
    assert service.get_score("A4")[2] == 0, "Team A4 should have 0 evens"
