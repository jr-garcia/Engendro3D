from hissing import Manager
from cycgkit.cgtypes import vec3

from .SoundClass import Sound


class SoundsManager(Manager):
    def __init__(self):
        """
        Keeps references to sounds in use.
        @rtype : SoundsManager
        """
        super(SoundsManager, self).__init__()
        self._soundIDs = {}
        self._lastListenerPosition = vec3(0)
        self._lastListenerOrientation = [0, 0, 1, 0, 1, 0]
        self._used = {}
        # al.alDistanceModel(al.AL_LINEAR_DISTANCE_CLAMPED)
        # al.alDistanceModel(al.AL_LINEAR_DISTANCE)
        # al.alDistanceModel(al.AL_INVERSE_DISTANCE_CLAMPED)
        # al.alDistanceModel(al.AL_EXPONENT_DISTANCE)  # << realistic
        # al.alDistanceModel(al.AL_EXPONENT_DISTANCE_CLAMPED)

    def idExists(self, ID):
        return ID in self._soundIDs

    def load(self, ID, filePath, parent=None, isStream=False, bufferSize=48000, maxBufferNumber=3):
        if self.idExists(ID):
            raise RuntimeError('the ID is in use.')
        sound = Sound(parent, self, filePath, isStream, bufferSize, maxBufferNumber)
        self._soundIDs[ID] = sound
        return sound

    def getSound(self, ID):
        """

            @rtype : Sound
            """
        if ID not in self._buffers.keys():
            raise KeyError("The ID does not exist.")
        else:
            return self._soundIDs[ID]

    def update(self, position, lookFixed, rotMat):
        looklist = list(lookFixed)
        if self._lastListenerPosition != vec3(position):
            self.listener.position = list(position)
            self._lastListenerPosition = vec3(position)
        if self._lastListenerOrientation != looklist:
            # orien = list(lookFixed.normalize())
            orien = looklist
            # orien.extend([0, 1, 0])
            orien.extend(list(rotMat * vec3(0, 1, 0)))
            self.listener.orientation = orien
            self._lastListenerOrientation = looklist
