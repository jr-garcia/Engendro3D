from openal import audio, al


class SoundStatesEnum(object):
    playing = 'playing'
    stopped = 'stopped'
    paused = 'paused'
    states = {al.AL_PLAYING: playing, al.AL_STOPPED: stopped, al.AL_PAUSED: paused}


class Sound(object):
    # todo: inherit from attachable
    def __init__(self, buffer, sink):
        """

        @type buffer: audio.SoundData
        """
        self.internalSound = sink
        self.soundSource = audio.SoundSource()
        self.soundSource.queue(buffer)
        self.__channels = buffer.channels
        self.soundSource.looping = False
        self.soundSource.reference_distance = 2
        self.soundSource.max_distance = 200
        self._state = SoundStatesEnum.stopped
        self._lastState = None
        # self.soundSource.rolloff_factor = .1

    def _play(self):
        self._lastState = SoundStatesEnum.playing
        self.internalSound.activate()
        self.internalSound.play(self.soundSource)
        self.internalSound.update()

    def play(self):
        self._state = SoundStatesEnum.playing

    def _stop(self):
        self._lastState = SoundStatesEnum.stopped
        self.internalSound.activate()
        self.internalSound.stop(self.soundSource)
        self.internalSound.update()

    def stop(self):
        self._state = SoundStatesEnum.stopped

    def _pause(self):
        self._lastState = SoundStatesEnum.paused
        self.internalSound.activate()
        self.internalSound.pause(self.soundSource)
        self.internalSound.update()

    def pause(self):
        self._state = SoundStatesEnum.paused

    def _get_looped(self):
        return self.soundSource.looping

    def _set_looped(self, value):
        self.soundSource.looping = value

    looped = property(fget=_get_looped, fset=_set_looped)

    def getState(self):
        return SoundStatesEnum.states[self.internalSound.getState(self.soundSource)]

    def _get_volume(self):
        return self.soundSource.gain

    def _set_volume(self, value):
        self.soundSource.gain = value / 100.0

    volume = property(fget=_get_volume, fset=_set_volume)

    def _getPosition(self):
        return self.soundSource.position

    def _setPosition(self, value):
        self.soundSource.position = value
        # self.internalSound.update()

    position = property(_getPosition, _setPosition)

    def _get_ChannelCount(self):
        return self.__channels

    channelCount = property(fget=_get_ChannelCount)

    def _getMinDistance(self):
        return self.soundSource.reference_distance

    def _setMinDistance(self, value):
        self.soundSource.reference_distance = value

    minDistance = property(_getMinDistance, _setMinDistance)

    def _getMaxDistance(self):
        return self.soundSource.max_distance

    def _setMaxDistance(self, value):
        self.soundSource.max_distance = value

    maxDistance = property(_getMaxDistance, _setMaxDistance)

    def update(self):
        if self._lastState == self._state:
            return
        if self._state == SoundStatesEnum.paused:
            self._pause()
        elif self._state == SoundStatesEnum.playing:
            self._play()
        else:
            self._stop()


    def terminate(self):
        print('Urgent Todo: Reimplement Sound system')
        self.stop()
        self.internalSound.deleteSources(self.soundSource)
        # self.internalSound.deleteBuffers(self.soundSource)