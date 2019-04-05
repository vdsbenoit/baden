import configparser
from os.path import abspath, dirname, join

from exceptions import ConfigurationException, BadenException

PROJECT_ROOT = abspath(dirname(dirname(__file__)))
SETTINGS_FILE = join(PROJECT_ROOT, "settings.ini")
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
