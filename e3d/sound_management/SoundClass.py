from hissing import Sound as HS

from ..Base3DObjectClass import Attachable


class Sound(HS, Attachable):
    def __init__(self, parent, manager, filePath, isStream, bufferSize, maxBufferNumber):
        """

        @type buffer: audio.SoundData
        """
        HS.__init__(self, manager, filePath, isStream, bufferSize, maxBufferNumber)
        Attachable.__init__(self, parent)

    # looped = property(fget=_get_looped, fset=_set_looped)

    # channelCount = property(fget=_get_ChannelCount)

    # minDistance = property(_getMinDistance, _setMinDistance)

    # maxDistance = property(_getMaxDistance, _setMaxDistance)

