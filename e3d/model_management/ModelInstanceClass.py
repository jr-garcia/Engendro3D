from .MaterialClass import Material
# from ..SoundClass import Sound
from ..Base3DObjectClass import Base3DObject
from ..physics_management.physicsModule import bodyShapesEnum


class ModelInstance(Base3DObject):
    def __init__(self, baseMats, modelID, manfred, ID, animationQuality, position, rotation, uniformScale,
                 shape=bodyShapesEnum.box, mass=None, isDynamic=False):
        """
       This object is returned by Scene.AddModel and represents one transformable instance
       of a non-transformable mesh loaded previously.
        @type animationQuality: int
        @type baseMats: list
        @rtype : ModelInstance
        @param baseMats: List of materials to copy
        @param modelID: ID of this instance for the scene
        @type manfred: ManagersReferenceHolder
        """
        mod = manfred.models._getModel(modelID)
        if not mod:
            raise KeyError('Model \'{}\' not found. Try loading it first.')
        mins, maxs = mod.boundingBox.getBounds()
        size = [0, 0, 0]
        size[0] = (abs(maxs[0]) / 2.0) + (abs(mins[0]) / 2.0)
        size[1] = (abs(maxs[1]) / 2.0) + (abs(mins[1]) / 2.0)
        size[2] = (abs(maxs[2]) / 2.0) + (abs(mins[2]) / 2.0)
        offset = mod.boundingBox.center()
        super(ModelInstance, self).__init__(position, rotation, uniformScale, size, shape, mass, isDynamic, ID, offset)
        self._materials = []
        self._attachedSounds = {}
        for m in baseMats:
            self._materials.append(Material._fromMaterial(m))
        self._sounds = manfred.sounds
        self._models = manfred.models
        self._baseModelID = modelID
        self.animationQuality = animationQuality

    def getAnimationsList(self):
        return list(self._models._getModel(self._baseModelID).animations.keys())

    def attachSound(self, bufferID, onObjectID):
        """

        @rtype : SoundClass.Sound
        """
        sound = self._sounds.getSound(bufferID)
        if sound.channelCount > 1:
            raise AttributeError("Only monoaural sounds can be attached.\n"
                                 "Sound with bufferID '{0}' is not monoaural.".format(bufferID))
        sound.position = self.position
        self._attachedSounds[onObjectID] = sound
        return sound

    def removeAttachedSound(self, ID):
        if ID in self._attachedSounds:
            try:
                self._attachedSounds.pop(ID)
            except Exception:
                pass

    def getAttachedSound(self, ID):
        """

        @rtype : Sound
        """
        if ID in self._attachedSounds.keys():
            return self._attachedSounds.get(ID)
        else:
            raise KeyError("The ID was not found")

    def getMaterialById(self, ID):
        """

         @rtype : Material
         """
        for tm in self._materials:
            if Material(tm).ID == ID:
                return tm
        raise KeyError("The ID was not found")

    def getMaterialByIndex(self, index):
        """

        @rtype : Material
        """
        return self._materials[index]

    def _update(self):
        if super(ModelInstance, self)._update():
            for Sn in self._attachedSounds.values():
                Sn.soundSource.position = list(self._position)

