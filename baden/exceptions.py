import logging

logger = logging.getLogger('default')


class BadenException(Exception):
    def __init__(self, msg):
        self.msg = msg
        logger.error(self)

    def __str__(self):
        return self.msg


class BadenError(Exception):
    def __init__(self, msg):
        self.msg = msg
        logger.error(self)

    def __str__(self):
        return self.msg
