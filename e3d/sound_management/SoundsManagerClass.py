from openal import al, audio, loaders
from cycgkit.cgtypes import vec3

from .SoundClass import Sound


class SoundsManager(object):
    def __init__(self):
        """
        Loads, unloads and returns references to sound buffers
        as usable sounds
        @rtype : SoundsManager
        """
        self._buffers = {}
        self._sounds = {}
        self.sink = audio.SoundSink()
        self.sink.activate()
        self._lastListenerPosition = vec3(0)
        self._lastListenerOrientation = [0, 0, 1, 0, 1, 0]
        self._used = {}
        # al.alDistanceModel(al.AL_LINEAR_DISTANCE_CLAMPED)
        # al.alDistanceModel(al.AL_LINEAR_DISTANCE)
        # al.alDistanceModel(al.AL_INVERSE_DISTANCE_CLAMPED)
        al.alDistanceModel(al.AL_EXPONENT_DISTANCE)  # << realistic
        # al.alDistanceModel(al.AL_EXPONENT_DISTANCE_CLAMPED)

    def get_idExists(self, ID):
        return ID in self._sounds

    idExists = property(fget=get_idExists)

    def loadSound(self, bufferID, filename):
        if bufferID in self._sounds.keys():
            raise AttributeError("The ID exists already.")
        else:
            try:
                sb = loaders.load_file(filename)
            except Exception as ex:
                raise Exception(ex.message)

        self._buffers[bufferID] = sb

    def unloadSound(self, ID):
        """
        Destroy the sound buffer if it is not in use.
        @param ID: The buffer ID
        @type ID: str
        @return:
        @rtype: bool
        """
        sn = self._buffers.get(ID)
        if self._used.get(ID, False):
            logger.log('The sound buffer is in use. Remove first all sounds that use it.')
            return False
        if sn is not None:
            b = self._buffers.pop(ID)

        return True

    def removeSound(self, ID):
        sn = self._buffers.get(ID)
        if sn is not None:
            try:
                assert isinstance(sn, Sound)
                sn.stop()
            except Exception:
                pass
        self._sounds.pop(ID)

    def getSound(self, ID):
        """

            @rtype : Sound
            """
        if ID not in self._buffers.keys():
            raise KeyError("The ID does not exist.")
        else:
            buff = self._buffers.get(ID)
            if buff is not None:
                ns = Sound(buff, self.sink)
                self._used[ID] = True
                self._sounds[ID] = ns
                return ns
            else:
                return None

    def update(self, position, lookFixed, rotMat):
        looklist = list(lookFixed)
        if self._lastListenerPosition != vec3(position):
            self.sink.listener.position = list(position)
            self._lastListenerPosition = vec3(position)
        if self._lastListenerOrientation != looklist:
            # orien = list(lookFixed.normalize())
            orien = looklist
            # orien.extend([0, 1, 0])
            orien.extend(list(rotMat * vec3(0, 1, 0)))
            self.sink.listener.orientation = orien
            self._lastListenerOrientation = looklist
        self.sink.update()
        for sound in self._sounds.values():
            sound.update()

    def terminate(self):
        for s in self._sounds.values():
            s.terminate()

        self.sink.__del__()
