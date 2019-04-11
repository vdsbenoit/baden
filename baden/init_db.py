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
    model.team.load_file(join(properties.PROJECT_ROOT, "data", "teams.csv"))
    model.game.load_file(join(properties.PROJECT_ROOT, "data", "distribution.csv"))
    # model.service.distribute_numbers()

