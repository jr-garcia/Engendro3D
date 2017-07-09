from collections import defaultdict
import inspect

import logging


class logLevelsEnum(object):
    debug = 0
    info = 1
    warning = 2
    error = 3


class _Logger(object):
    def __init__(self):
        self.loggers = {}

    def log(self, message, messageType=logLevelsEnum.debug):
        """


        @type message: str
        @type messageType: int
        """
        mod = inspect.getmodule(inspect.stack()[2][0])
        if mod:
            modName = mod.__name__
            del mod
        else:
            modName = 'root'

        logger = self.loggers.get(modName, logging.getLogger(modName))

        if messageType == logLevelsEnum.debug:
            logger.debug(message)
        elif messageType == logLevelsEnum.info:
            logger.info(message)
        elif messageType == logLevelsEnum.warning:
            logger.warning(message)
        elif messageType == logLevelsEnum.error:
            logger.error(message)
