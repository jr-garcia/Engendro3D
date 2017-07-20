class BaseManager(object):
    def __init__(self):
        self._engine = None

    def initialize(self, engine):
        pass

    def terminate(self):
        pass