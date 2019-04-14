# -*-coding:UTF-8 -*

"""
Baden Battle scores tool.
Database initialization
"""
import logging
from os.path import join

import controller.server
import controller.util
import model.game
import model.service
import model.team
from model import properties

__author__ = 'Benoit Vander Stappen'

log = logging.getLogger('default')


if __name__ == "__main__":
    controller.util.initialize()
    model.team.drop_teams()
    model.game.drop_games()  # collection is cleared before loading the same files otherwise it would be duplicated
    model.team.load_file(join(properties.PROJECT_ROOT, "data", "teams.csv"))
    model.game.load_file(join(properties.PROJECT_ROOT, "data", "distribution.csv"))
    model.game.load_file(join(properties.PROJECT_ROOT, "data", "distribution2.csv"))
    model.game.load_file(join(properties.PROJECT_ROOT, "data", "distribution3.csv"))
    model.service.distribute_numbers()
    model.game.validate_game_collection()

