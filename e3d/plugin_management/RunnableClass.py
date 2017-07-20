MAINFILENAME = 'main.py'

MAINCLASSNAME = 'MAIN'


class Runnable(object):
    def __init__(self, engine):
        self.engine = engine
        self.repiteCurrentPass = False

    def preparePlugin(self, data):
        pass

    def onDrawPass(self, passNumber):
        pass

    def onPreUpdate(self):
        pass

    def onPostUpdate(self):
        pass

    def terminate(self):
        pass
