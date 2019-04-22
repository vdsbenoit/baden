import logging

from mongoengine import *

log = logging.getLogger("default")


class Match(Document):
    time = IntField(required=True)
    schedule = StringField(required=True, max_length=11)
    game_number = IntField(required=True)
    players_number = ListField(IntField(), required=True)  # player numbers
    players_code = ListField(StringField(max_length=5))
    winner = StringField(max_length=5)
    loser = StringField(max_length=5)
    even = BooleanField(default=False)
    recorded = BooleanField(default=False)


def get_match_quantity():
    """
    Get the quantity of matches a team has to play
    :return:
    """
    return len(Match.objects().distinct("time"))


def get_recorded_scores_amount(time):
    """
    Get the quantity of recorded scores
    :param time:
    :return:
    """
    return Match.objects(time=time, recorded=True).count()


def reset_scores():
    """
    Reset all the scores
    """
    for m in Match.objects():
        m.winner = ""
        m.loser = ""
        m.even = False
        m.recorded = False
        m.save()

