import numpy
from time import time
from os import path

from .._baseManager import BaseManager
from ..ParallelCommunicators import ParallelServer, ParallelClient, taskTypesEnum, Task
from ..ParallelCommunicators import Empty
from ..sound_management import SoundStatesEnum
from .ffmpeg_reader import FFMPEG_VideoReader, ffmpeg_parse_infos


class VideoStatesEnum(object):
    Stopped = 'Stopped'
    Playing = 'Playing'
    Paused = 'Paused'


class VideoManager(BaseManager):
    def __init__(self):
        self._videos = []
        super(VideoManager, self).__init__()

    def load(self, filePath, resizeTo=None):
        video = Video(self._engine, filePath, resizeTo)
        self._videos.append(video)
        return video

    def terminate(self):
        for video in self._videos:
            video.terminate()

    def update(self):
        for video in self._videos:
            video.update()

    def getVideoInfo(self, filePath):
        infos = ffmpeg_parse_infos(filePath)
        return infos


class VideoFiller(ParallelServer):
    def __init__(self, inQueue, outQueue, filePath, infos, target_resolution):
        super(VideoFiller, self).__init__(inQueue, outQueue)
        self.vr = FFMPEG_VideoReader(filePath, infos, None, 'bgra', target_resolution=target_resolution)
        self.lastFrame = None
        self.running = True
        self.state = VideoStatesEnum.Stopped
        self.isInit = False
        self.startTime = 0

    def checkQueue(self):
        task = self._readTask()

        if task:
            taskName = task.name
            taskData = task.data
            if task.taskType == taskTypesEnum.Finish:
                self.running = False
                return False
            elif taskName == 'state':
                self.state = taskData
            elif taskName == 'startTime':
                self.startTime = taskData
            else:
                print('unknown task name:' + taskName)
        return True

    def _removeTask(self):
        try:
            self._outQueue.get_nowait()
        except Empty:
            return

    def run(self):
        vr = self.vr
        startTime = 0
        frameDuration = 1.0 / vr.fps
        while self.running:
            try:
                if not self.checkQueue():
                    self._removeTask()
                    break
                if self.state == VideoStatesEnum.Playing:
                    if not self.isInit:
                        startTime = self.startTime
                        self.isInit = True
                    if vr.pos < vr.nframes:
                        currentTime = time() - startTime
                        neededFrameN = int(round(currentTime / frameDuration)) 
                        toSkip = (neededFrameN - vr.pos) 
                        if toSkip > 0:
                            vr.skip_frames(toSkip)

                        if neededFrameN >= vr.pos:
                            frame = vr.read_frame()  # .flatten()
                            self._removeTask()
                            self._sendTask(Task(taskTypesEnum.TaskResult, frame, 'frame'))
            except Exception:
                raise

        try:
            self._outQueue.cancel_join_thread()
            self._inQueue.cancel_join_thread()
        except AttributeError:
            pass

    def terminate(self):
        self.running = False

        super(VideoFiller, self).terminate()


class Video(ParallelClient):
    def __init__(self, engine, filePath, resizeTo, streamSound=False):
        super(Video, self).__init__()
        self._engine = engine
        self._state = VideoStatesEnum.Stopped
        # self._lastFrame = None
        self._isStarted = False

        infos = ffmpeg_parse_infos(filePath)
        if resizeTo is None:
            resizeTo = infos['video_size']

        w, h = (int(val) for val in resizeTo)
        self._size = (h, w)  # invert is needed for some reason

        ID = path.splitext(path.basename(filePath))[0]
        i = 0
        while self._engine.textures.exists(ID):
            ID = ID + str(i)
            i += 1

        self._textureID = ID + '_texture'
        self._engine.textures.createEmpty2DTexture(self._textureID, h, w)

        soundID = ID + '_sound'
        sound = engine.sounds.load(soundID, filePath, isStream=streamSound)
        self._soundID = soundID
        self._sound = sound

        self._filler = VideoFiller(self._inQueue, self._outQueue, filePath, infos, (w, h))
        self._filler.start()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if self._state == value:
            return
        if value == VideoStatesEnum.Playing and not self._isStarted:
            self._sendTask(Task(taskTypesEnum.RawData, time(), 'startTime'))
        self._sound.state = value
        self._sendTask(Task(taskTypesEnum.NewTask, value, 'state'))
        self._state = value

    def play(self):
        self.state = VideoStatesEnum.Playing

    def stop(self):
        self.state = VideoStatesEnum.Stopped
        self._sound.stop()

    def pause(self):
        self.state = VideoStatesEnum.Paused
        self._sound.pause()

    def getTextureID(self):
        return self._textureID

    def getSound(self):
        return self._sound

    def update(self):
        task = self._readTask()
        if task:
            if task.name == 'frame':
                self._engine.textures.update2DTexture(self._textureID, task.data, (0, 0), self._size)

    def terminate(self):
        self._sendTask(Task(taskTypesEnum.Finish, ''), True)
        super(Video, self).terminate()
        self._filler.join(1)
        # self._filler.terminate()
