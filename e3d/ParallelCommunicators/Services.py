from multiprocessing import Process, Queue

try:
    from queue import Full, Empty
except ImportError:
    from Queue import Full, Empty

from .._baseManager import BaseManager
from ..Logging import logLevelsEnum


class taskTypesEnum(object):
    Error = 'Error'
    RawData = 'RawData'
    NewTask = 'NewTask'
    TaskResult = 'TaskResult'
    Custom = 'Custom'
    Finish = 'Finish'


class Task(object):
    def __init__(self, taskType, data, name=''):
        self.taskType = taskType
        self.data = data
        self.name = name

    def __repr__(self):
        return self.taskType + '-' + self.name


class Communicator(object):
    def __init__(self):
        self._inQueue = Queue()
        self._outQueue = Queue()

    def _readTask(self):
        try:
            task = self._inQueue.get_nowait()
        except Empty:
            return

        if not isinstance(task, Task):
            self._engine.log('server sent data with wrong type. Ignored.', logLevelsEnum.warning)
        else:
            return task

    def _sendTask(self, task, wait=False):
        if not isinstance(task, Task):
            raise TypeError('task must be of type \'Task\'')
        try:
            if wait:
                self._outQueue.put(task, timeout=1)
            else:
                self._outQueue.put_nowait(task)
        except Full:
            self._engine.log('out queue is full. Missed data!', logLevelsEnum.warning)


class ParallelClient(BaseManager, Communicator):
    def __init__(self):
        BaseManager.__init__(self)
        Communicator.__init__(self)

    def terminate(self):
        self._outQueue.close()
        self._inQueue.close()


class ParallelServer(Communicator, Process):
    def __init__(self, inQueue, outQueue):
        Process.__init__(self)
        Communicator.__init__(self)
        self._outQueue = inQueue
        self._inQueue = outQueue
