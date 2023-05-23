from ..Base3DObjectClass import DefaultObjectParameters
from ..update_management.pickleableMethods import updateLightTransformation, updateModelTransformation
from ..update_management.renderingListCreation import getOrderedModelInstances
from .LightClass import light, lightTypesEnum
from .SkyboxClass import Skybox
from ..backends.base_backend import DrawingData, InstanceData
from ..cameras.SimpleCameraClass import SimpleCamera
from ..commonValues import *
from ..model_management.ModelInstanceClass import ModelInstance
from ..model_management.AnimationModule import Animation
from ..physics_management.physicsModule import bodyShapesEnum, ScenePhysics
from ..model_management.MaterialClass import Material

from cycgkit.cgtypes import mat4

from bullet.bullet import ACTIVE_TAG, WANTS_DEACTIVATION


class Scene(object):
    def get_ID(self):
        return self._iID

    ID = property(fget=get_ID)

    def __init__(self, ID, engine, gravity, resolution):
        self._models = {}
        self._lights = {}
        self._defaultCamera = SimpleCamera([0, 0, 0], [0, 0, 0], ID='defaultcam')
        self.currentCamera = self._defaultCamera
        self.__models = engine.models
        self.sounds = engine.sounds
        self._engine = engine
        self._iID = ID
        self._lastUpdate = 0
        self.__skipped = 0
        self.__frames = 0
        self.beforeUpdateCallback = None
        self._sky = None
        self._instancesOrderedByModel = []
        self._DebugColors = [[1, 0, 0], [0, 1, .3], [0, 0, 1], [1, 1, 0], [0, 1, 1], [1, 0, 1], [.0, .5, 0], [1, .5, 0]]
        self.__currentDebugColor = 0
        self.bottom = -500

        self._material = Material()
        self._material.diffuseColor = vec3(0.23, 0.34, 0.65)
        self.ambientColor = [v / 3.0 for v in self._material.diffuseColor]

        self._fogType = 0
        self._fogColor = self._material.diffuseColor
        self._fogStart = 300.0
        self._fogEnd = 500.0

        self.physics = ScenePhysics(gravity, resolution)
        self._currentTransformations = None
        self._currentModel = None

    def _getBGColor(self):
        return self._material.diffuseColor

    def _setBGColor(self, val):
        self._material.diffuseColor = val
        self._fogColor = self._material.diffuseColor

    bgColor = property(_getBGColor, _setBGColor)

    def __repr__(self):
        return self.ID

    def hasModel(self, ID):
        return ID in self._models

    def addModel(self, modelID, IDInScene, position, rotation, uniformScale, animationQuality=1,
                 shape=bodyShapesEnum.auto, mass=None, isDynamic=False, materialsList=None):
        """



        @param animationQuality: The quality for the steps of the animations. The higher,
          more frames will be fetched from the animations. If animations are incomplete or
          show jumps, raise this value. Must be equal or higher than 0. Default 1.
        @param modelID: The ID of a model previously loaded with engine.models.loadModel.
        @param IDInScene: The ID that this instance will have in the scene.
        @param shape: One of bodyShapesEnum
        @type animationQuality: int
        @rtype : ModelInstance
        @type IDInScene: str
        @type modelID: str
        @type shape: bodyShapesEnum
        """
        if self.hasModel(IDInScene):
            raise NameError("An object with the same ID already exists in the scene:\n" + IDInScene)
        model = self.__models._getModel(modelID)
        if model:
            if shape == bodyShapesEnum.auto:
                shape = model._preShape
            materials = model.materials if materialsList is None else materialsList
            modelIns = ModelInstance(materials, modelID, self._engine, IDInScene, animationQuality, position, rotation,
                                     uniformScale, shape, mass, isDynamic)
            self.__currentDebugColor += 1
            if self.__currentDebugColor > len(self._DebugColors) - 1:
                self.__currentDebugColor = 0
            modelIns.debugColor = list(self._DebugColors[self.__currentDebugColor])
            self._models[IDInScene] = modelIns
            self._instancesOrderedByModel = getOrderedModelInstances(self)
            self.physics.addRigidObject(modelIns.physicsBody)
            if not modelIns.physicsBody.isDynamic:
                modelIns.physicsBody._reBuildMass(0.0)
            return modelIns
        else:
            raise KeyError(
                    "Error adding model. The specified ID ('" + modelID + "') does not exist.\nTry loading the model before calling addModel.")

    def addLight(self, ltype=lightTypesEnum.directional, position=None, rotation=None, ID=''):
        """
        Insert a light into the scene.
        If no ID is given, a default will be created.
        @rtype : Engendro3D.LightClass.light
        @type ID: str
        """
        if ID == '':
            lid = 0
            ID = 'light{}'.format(lid)
            while ID in self._lights:
                lid += 1
                ID = 'light{}'.format(lid)
        elif ID in self._lights:
            raise KeyError('The ID for the light exists.')
        l = light(ltype, position, rotation, ID)
        self._lights[ID] = l
        return l

    def removeModel(self, sceneID):
        """

        @type sceneID: str
        """
        self._models.pop(sceneID)
        self._instancesOrderedByModel = getOrderedModelInstances(self)

    def removeLight(self, ID):
        """

        @type ID: str
        """
        self._lights.pop(ID)

    def flush(self):
        """
        Removes all objects from the scene.

        """
        self._models.clear()
        self._lights.clear()

    def _modelsUpdate(self):
        # Todo: implement per model calbacks
        for m in self._models.values():
            if m.physicsBody.isDynamic and not m.physicsBody._beyondBoundary:
                transform = m.physicsBody._motion.getWorldTransform()
                pos = vec3(bulletVectorToList(transform.getOrigin() - Vector3(m._pOffset[0], m._pOffset[1], m._pOffset[2])))
                rot = vec3(bulletQuatToRotList(transform.getRotation()))
                m._position = pos
                m._rotation = rot
                m._dirty = True

            m._update()  # todo: reimplement threaded update with stronger method
            
            if m._position[1] <= self.bottom and not m.physicsBody._beyondBoundary:
                self.physics.removeRigidObject(m.physicsBody)
                m.physicsBody._phyUpdWait = 0
                m.visible = False
                m.physicsBody._beyondBoundary = True
            else:
                for Sn in m._attachedSounds.values():
                    Sn.soundSource.position = list(m._position)

    def _UpdateLights(self):
        # Todo: implement per model callbacks
        for m in self._lights.values():
            assert isinstance(m, light)
            if m._dirty:
                m._update()
                if m._position[1] <= self.bottom and not m.physicsBody._beyondBoundary:
                    self.physics.removeRigidObject(m.physicsBody)
                    m.physicsBody._phyUpdWait = 0
                    m.visible = False

    def setDefaultSkyBox(self):
        self._sky = Skybox('default', self._engine)
        self._sky.loadDefault()

    def _getSky(self):
        return self._sky

    def _setSky(self, value):
        if value is not None and not isinstance(value, Skybox):
            raise TypeError('sky object must be of type \'Skybox\'')
        self._sky = value

    sky = property(_getSky, _setSky)

    @property
    def fogType(self):
        return self._fogType

    @fogType.setter
    def fogType(self, value):
        self._fogType = value

    def update(self, netTime, windowSize):
        if self._lastUpdate == 0:
            frameTime = 0
        else:
            frameTime = netTime - self._lastUpdate
        if self.beforeUpdateCallback is not None:
            self.beforeUpdateCallback([frameTime, netTime])

        self.physics.update(frameTime / 1000.0)
        self._modelsUpdate()
        self._UpdateLights()

        if self._sky is not None:
            self._sky._update()
        self._lastUpdate = netTime

        currentModelID = ''
        currentModel = None

        newDrawingData = DrawingData()
        newDrawingData.clearColor = self.bgColor
        newDrawingData.sky = self.sky

        if self.currentCamera is None:
            self.currentCamera = self._defaultCamera
        if not self.currentCamera.projectionMatrix:
            self.currentCamera.updateFOV(windowSize[0], windowSize[1])

        current_view = self.currentCamera._update()
        current_projection = self.currentCamera.projectionMatrix
        current_zNear = self.currentCamera._p_zNear
        current_zFar = self.currentCamera._p_zFar
        defaultSceneParams = DefaultSceneParameters()
        defaultSceneParams.defaultTexture = self._engine.textures.getDefaultTexture()
        defaultSceneParams.zNear = current_zNear
        defaultSceneParams.zFar = current_zFar
        defaultSceneParams.ambientColor = self.ambientColor
        defaultSceneParams.fogType = self._fogType
        defaultSceneParams.fogColor = self._fogColor
        defaultSceneParams.fogStart = self._fogStart
        defaultSceneParams.fogEnd = self._fogEnd
        defaultSceneParams.lights = self._lights
        defaultSceneParams.cameraPosition = self.currentCamera._position
        defaultSceneParams.view = current_view
        defaultSceneParams.projection = current_projection
        defaultSceneParams.windowSize = vec3(windowSize[0], windowSize[1], 1)
        defaultSceneParams.construct()

        newDrawingData.defaultSceneParams = defaultSceneParams

        for currentModelInstance in self._instancesOrderedByModel:
            if currentModelInstance.visible:
                if currentModelInstance._baseModelID != currentModelID:
                    currentModelID = currentModelInstance._baseModelID
                    currentModel = self._engine.models._getModel(currentModelID)

                defaultObjectParams = DefaultObjectParameters()
                defaultObjectParams.model = currentModelInstance._transformation
                defaultObjectParams.view = current_view
                defaultObjectParams.projection = current_projection
                defaultObjectParams.hasBones = currentModel.hasBones
                defaultObjectParams.construct()

                self._currentModel = currentModel

                if currentModel.hasBones:
                    newDrawingData.modelBoneDirs[currentModelID] = currentModel.boneDict
                    time = -1
                    if currentModelInstance._animationID != '':
                        time = Scene.calculateInstanceAnimationTime(netTime, currentModelInstance, currentModel)
                else:
                    time = None
                Scene.extractRenderInfo(currentModelInstance, defaultObjectParams, currentModel.rootNode,
                                        newDrawingData, time, self)

        return newDrawingData

    @staticmethod
    def extractRenderInfo(currentModelInstance, defaultParams, node, newDrawingData, time, scene):
        for mesh in node._meshes:
            meshid = mesh.ID
            transformations = None
            if time is not None:
                # todo: implement currentModel.hasBones debug bounding box
                transformations = scene.getInstanceAnimationTransformations(currentModelInstance, time, mesh)
                # self._currentAnimatedBBox.clear()
            newDrawingData.meshes.add(mesh)
            meshMat = currentModelInstance._materials[mesh._materialIndex]
            newDrawingData.instances[meshid].append(
                InstanceData(meshMat, defaultParams, transformations, currentModelInstance._baseModelID))
        for cnode in node._childNodes:
            Scene.extractRenderInfo(currentModelInstance, defaultParams, cnode, newDrawingData, time, scene)

    @staticmethod
    def calculateInstanceAnimationTime(netTime, currentModelInstance, currentModel):
        assert isinstance(currentModelInstance, ModelInstance)
        model = currentModelInstance
        if model.animState == ModelInstance.animationState.playing:
            if model._animationStartupTime == -1:
                model._animationStartupTime = netTime

            if model._animLastPauseStartup != -1:
                model._animationPausedTime += netTime - model._animLastPauseStartup
                model._animLastPauseStartup = -1

            anim = currentModel.animations[currentModelInstance._animationID]
            assert isinstance(anim, Animation)
            btime = (((netTime - model._animationStartupTime) - model._animationPausedTime) / 1000.0) * anim.ticks

            time = btime
            while time > anim.duration:
                time -= anim.duration
                if time < 0:
                    time += 1.0
            adjustedTime = round(time, model.animationQuality)
            model._animationLastPlayedFrame = adjustedTime
            return adjustedTime

        elif model.animState == ModelInstance.animationState.paused:
            if model._animationPausedTime == -1:
                model._animationPausedTime = netTime
            return model._animationLastPlayedFrame
        else:
            model._animationStartupTime = -1
            model._animationPausedTime = -1

    def getInstanceAnimationTransformations(self, currentModelInstance, time, mesh):
        if time < 0:
            ID = list(currentModelInstance.getAnimationsList())[0]
            anim = self._currentModel.animations[ID]
            currentTransformations = self._currentModel.skeleton.getBindPose(anim, mesh)
        else:
            anim = self._currentModel.animations[currentModelInstance._animationID]
            currentTransformations = self._currentModel.skeleton.getAnimationTranformations(anim, time, mesh)

            # for b in mesh.boneMinMax.items():
            # flatm = currentTransformations[b[0]]
            # pointa = flatm * b[1][0]
            # self._currentAnimatedBBox.addPoint(pointa)
            # pointb = flatm * b[1][1]
            # self._currentAnimatedBBox.addPoint(pointb)

        return currentTransformations

    def terminate(self):
        self.physics.terminate()


class DefaultSceneParameters(object):
    def __init__(self):
        self.zFar = 5000
        self.zNear = 1
        self.fogType = 0
        self.fogColor = vec3(0.23, 0.34, 0.65)
        self.fogStart = 300.0
        self.fogEnd = 500.0
        self.defaultTexture = None
        self.ambientColor = [1, 1, 1, 1]
        self.lights = {}
        self.cameraPosition = None
        self.view = None
        self.projection = None
        self.ViewProjection = None
        self.windowSize = vec3(0)

    def construct(self):
        self.ViewProjection = self.projection * self.view
