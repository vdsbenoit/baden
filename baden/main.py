# -*-coding:UTF-8 -*

"""
Baden Battle scores tool.
"""
import configparser
import logging

import model.util
import model.team
from model import properties
from model.properties import SETTINGS_FILE

__author__ = 'Benoit Vander Stappen'

log = logging.getLogger('default')


def logger_setup():
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)
    log.setLevel(logging.DEBUG)
    # console handler
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    log.addHandler(sh)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(config["MISC"]["log_file"], mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]\t%(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    log.addHandler(fh)
    log.debug("####################  NEW INSTANCE  ####################")


def main():
    logger_setup()
    properties.parse_settings()
    model.util.setup_db()

    print("end")


if __name__ == "__main__":
    main()
