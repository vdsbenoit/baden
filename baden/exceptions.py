import logging

logger = logging.getLogger('default')


class BadenException(Exception):
    def __init__(self, msg):
        self.msg = msg
        logger.error(self)

    def __str__(self):
        return 'Baden encountered an issue: {}'.format(self.msg)


class BadenError(Exception):
    def __init__(self, msg):
        self.msg = msg
        logger.error(self)

    def __str__(self):
        return 'Baden faced an error: {}'.format(self.msg)


class ConfigurationException(Exception):
    def __init__(self, parameter, msg=""):
        self.parameter = parameter
        self.msg = msg
        logger.error(self)

    def __str__(self):
        return "'{}' is not set properly in settings file. {}".format(self.parameter, self.msg)
