# -*-coding:UTF-8 -*

"""
Baden Battle scores tool.
Documents generation (roadmaps & tables)
"""
import logging
import os

import controller.util
import controller.roadmap
from model import properties

__author__ = 'Benoit Vander Stappen'

log = logging.getLogger('default')


if __name__ == "__main__":
    controller.util.initialize()
    controller.roadmap.generate_team_roadmaps(os.path.join(properties.PROJECT_ROOT, "team_roadmaps.docx"))
    controller.roadmap.generate_game_roadmaps(os.path.join(properties.PROJECT_ROOT, "game_roadmaps.docx"))
