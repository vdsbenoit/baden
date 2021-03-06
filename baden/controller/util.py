# -*-coding:UTF-8 -*
import configparser
import logging
from os.path import dirname, abspath, join

import model.game
import model.service
import model.team
from model import properties
from model.properties import SETTINGS_FILE

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
    log_file = join(abspath(dirname(dirname(__file__))), config["MISC"]["log_file"])
    fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]\t%(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    log.addHandler(fh)
    log.debug("####################  NEW INSTANCE  ####################")


def initialize():
    logger_setup()
    properties.parse_settings()
    model.service.setup_db()


