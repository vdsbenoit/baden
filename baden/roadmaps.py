# -*-coding:UTF-8 -*

"""
Baden Battle scores tool.
Roadmaps generation
"""
import logging
import controller.util
import controller.roadmap


__author__ = 'Benoit Vander Stappen'

log = logging.getLogger('default')


if __name__ == "__main__":
    controller.util.initialize()
    controller.roadmap.generate_team_roadmaps()
    controller.roadmap.generate_game_roadmaps()
