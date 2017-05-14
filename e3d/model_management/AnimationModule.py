class Animation(object):
    def __init__(self, anim):
        """

        @type anim:
        """
        self.transforms = {}
        self.name = anim.mName
        self.duration = anim.mDuration
        self.ticks = anim.mTicksPerSecond
        if self.ticks == 0 or self.ticks is None:
            self.ticks = 25.0
        self.boneKeys = {}
        for ch in anim.mChannels:
            boneID = ch.mNodeName
            keyframes = {}
            for pk in ch.mPositionKeys:
                self.checkKeyFrameExist(keyframes, pk.mTime)
                keyframes[pk.mTime].position = pk.mValue.tolist()

            for pk in ch.mScalingKeys:
                self.checkKeyFrameExist(keyframes, pk.mTime)
                keyframes[pk.mTime].scale = pk.mValue.tolist()

            for pk in ch.mRotationKeys:
                self.checkKeyFrameExist(keyframes, pk.mTime)
                keyframes[pk.mTime].rotation = pk.mValue.tolist()

            self.boneKeys[boneID] = keyframes

    def __repr__(self):
        return '{}: {} ticks, {} bones'.format(self.name, self.ticks,
                                               len(self.boneKeys))

    @staticmethod
    def checkKeyFrameExist(keysDict, time):
        if time not in keysDict.keys():
            keysDict[time] = transformationValues()

    def printIt(self):
        print('Animation Name   : {}\n'
              'Duration seconds : {}\n'
              'Bone count       : {}'.format(self.name, round(float(self.duration) / self.ticks, 2),
                                             len(self.boneKeys))
              )


class transformationValues(object):
    def __init__(self):
        self.position = None
        self.scale = None
        self.rotation = None
