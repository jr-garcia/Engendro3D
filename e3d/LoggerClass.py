from time import time
from datetime import datetime


class logLevelsEnum(object):
    debug = 0
    info = 1
    warning = 2
    error = 3


class __Logger(object):
    def __init__(self):
        self.__lasttime = 0
        self.logLevel = logLevelsEnum.error

    def log(self, message, warnlevel=logLevelsEnum.error):
        """


        @type message: str
        @type warnlevel: int
        """
        if warnlevel >= self.logLevel:
            date = datetime.now().time()
            print(u'{0:0>2}:{1:0>2}:{2:0>2} -> {3}'.format(date.hour, date.minute, int(date.second),
                                                           message))

    def meassure(self, message):
        if self.logLevel > 0:
            return
        t = int(round(time() * 1000))

        if self.__lasttime == 0:
            self.__lasttime = t
            et = 0
        else:
            et = t - self.__lasttime
            self.__lasttime = t
        print (str(et) + ' ms << ' + message + ':')


logger = __Logger()
dt = datetime.now().time()
# logger.log('{0:0>2}:{1:0>2}:{2:0>2} -> Logger started.'.format(dt.hour, dt.minute, int(dt.second)),
#            logLevelsEnum.error)
print('{0:0>2}:{1:0>2}:{2:0>2} -> Logger started ({3}).'.format(dt.hour, dt.minute, int(dt.second),
                                                                str(datetime.now().date())))