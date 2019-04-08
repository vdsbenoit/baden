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
WEB_SOCKET_IP = ""
WEB_SOCKET_PORT = 0
CHERRYPY_MAX_THREAD_POOL = 0
WEB_SESSION_TIMEOUT = 0


def parse_settings():
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)

    try:
        globals()['LIST_SEPARATOR'] = config['SYSTEM']['list_separator']
        globals()['GAMES_TABLE_FILE'] = config['CONFIGURATION']['game_table_file']
        globals()['DB_NAME'] = config['DATABASE']['name']
        globals()['DB_HOST'] = config['DATABASE']['host']
        globals()['DB_PORT'] = config['DATABASE'].getint('port')
        globals()['WEB_SOCKET_IP'] = config['WEB']['socket_ip']
        globals()['WEB_SOCKET_PORT'] = config['WEB'].getint('socket_port')
        globals()['CHERRYPY_MAX_THREAD_POOL'] = config['WEB'].getint('max_thread_pool')
        globals()['WEB_SESSION_TIMEOUT'] = config['WEB'].getint('session_timeout')

    except KeyError:
        raise ConfigurationException
