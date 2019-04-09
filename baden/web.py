# -*-coding:UTF-8 -*

"""
Baden Battle scores tool.
Web server
"""
import logging

import controller.server
import controller.util

__author__ = 'Benoit Vander Stappen'

log = logging.getLogger('default')


if __name__ == "__main__":
    controller.util.initialize()
    controller.server.launch_web_server()

