# -*-coding:UTF-8 -*

"""
Baden Battle scores tool.
Database initialization
"""
import logging
from os.path import join

import controller.util
import model.game
import model.service
import model.team
from model import properties

__author__ = 'Benoit Vander Stappen'

log = logging.getLogger('default')


if __name__ == "__main__":
    controller.util.initialize()
    model.team.Team.drop_collection()
    model.game.Game.drop_collection()
    model.game.Match.drop_collection()
    # collection is cleared before loading the same files otherwise it would be duplicated
    model.team.load_file(join(properties.DATA_DIR, "teams.csv"), True)
    model.game.load_file(join(properties.DATA_DIR, "distribution1.csv"))
    model.game.load_file(join(properties.DATA_DIR, "distribution2.csv"))
    model.game.load_file(join(properties.DATA_DIR, "distribution3.csv"))
    model.service.set_player_codes()
    model.team.set_matches()
    model.game.validate_game_collection()

