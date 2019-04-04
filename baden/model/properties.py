import configparser
import os

from exceptions import ConfigurationException, BadenException

APP_ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
SETTINGS_FILE = os.path.join(APP_ROOT_DIR, "settings.ini")
LIST_SEPARATOR = ""
GAMES_TABLE_FILE = ""
DB_NAME = ""
DB_HOST = ""
DB_PORT = 0


def parse_settings():
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)

    try:
        globals()['LIST_SEPARATOR'] = config["SYSTEM"]["list_separator"]
        globals()['GAMES_TABLE_FILE'] = config["CONFIGURATION"]["game_table_file"]
        globals()['DB_NAME'] = config["DATABASE"]["name"]
        globals()['DB_HOST'] = config["DATABASE"]["host"]
        globals()['DB_PORT'] = config["DATABASE"].getint("port")
    except KeyError:
        raise ConfigurationException("list_separator")
