from sys import version_info


class ThreadingManager:
    def __init__(self):
        self._maxThreads = 0
    #     TODO: Reimplement multiprocess here.

    def initialize(self, maxThreads):
        self._maxThreads = maxThreads

    def map(self, func, iter):
        return map(func, iter)

    def terminate(self):
        pass
