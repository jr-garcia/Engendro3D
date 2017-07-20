class BaseManager(object):
    def __init__(self):
        self._engine = None

    def initialize(self, engine):
        self._engine = engine

    def terminate(self):
        pass
