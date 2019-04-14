import configparser
from os.path import abspath, dirname, join

from exceptions import BadenException

PROJECT_ROOT = abspath(dirname(dirname(__file__)))
SETTINGS_FILE = join(PROJECT_ROOT, "settings.ini")
LIST_SEPARATOR = ""
SCORE_DIGITS = 0  # todo: remove if not used
GAMES_TABLE_FILE = ""
DB_NAME = ""
DB_HOST = ""
DB_PORT = 0
WEB_SOCKET_IP = ""
WEB_SOCKET_PORT = 0
CHERRYPY_MAX_THREAD_POOL = 0
WEB_SESSION_TIMEOUT = 0
SLL_CERTIFICATE = ""
SSL_KEY = ""


def parse_settings():
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)

    try:
        globals()['LIST_SEPARATOR'] = config['SYSTEM']['list_separator']
        globals()['SCORE_DIGITS'] = config['GAME'].getint('score_digits')
        globals()['DB_NAME'] = config['DATABASE']['name']
        globals()['DB_HOST'] = config['DATABASE']['host']
        globals()['DB_PORT'] = config['DATABASE'].getint('port')
        globals()['WEB_SOCKET_IP'] = config['WEB']['socket_ip']
        globals()['WEB_SOCKET_PORT'] = config['WEB'].getint('socket_port')
        globals()['CHERRYPY_MAX_THREAD_POOL'] = config['WEB'].getint('max_thread_pool')
        globals()['WEB_SESSION_TIMEOUT'] = config['WEB'].getint('session_timeout')
        globals()['SLL_CERTIFICATE'] = config['WEB']['ssl_certificate']
        globals()['SSL_KEY'] = config['WEB']['ssl_key']

    except KeyError as e:
        raise BadenException("{} key is not set properly in settings.ini".format(str(e)))
