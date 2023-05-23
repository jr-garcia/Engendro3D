from __future__ import print_function
from .SceneClass import Scene
from ..backends.base_backend import DrawingData


class ScenesManager(object):
    def __init__(self):
        self._scenes = {}
        self._models = None
        self.sounds = None
        self._engine = None
        self.currentSceneID = ""

        self._defaultScene = Scene

    def initialize(self, engine):
        self._models = engine.models
        self.sounds = engine.sounds
        self._engine = engine
        self._defaultScene = Scene('DefaultScene', engine, resolution=160, gravity=-9.8)
        self._scenes[self._defaultScene.ID] = self._defaultScene

    def _get_idExists(self, ID):
        return ID in self._scenes.keys()

    idExists = property(fget=_get_idExists)

    def addScene(self, ID, resolution=160, gravity=-9.8):
        if ID in self._scenes.keys():
            raise KeyError("The ID exists already.")
        else:
            ns = Scene(ID, self._engine, gravity, resolution)
            self._scenes[ID] = ns
            return ns

    def removeScene(self, id):
        if self.currentSceneID == id:
            self.currentSceneID = ""
        self._scenes.pop(id)

    def getScene(self, id):
        """

        @rtype : Scene
        """
        return self._scenes.get(id, self._defaultScene)

    def setCurrentSceneID(self, ID):
        if ID not in self._scenes.keys():
            raise KeyError("The ID does not exist")
        else:
            self.currentSceneID = ID

    def setCurrentScene(self, scene):
        if not scene:
            scene = self._defaultScene
        self.currentSceneID = scene.ID

    def getCurrentScene(self):
        """

        @rtype : Scene
        """
        return self.getScene(self.currentSceneID)

    currentScene = property(getCurrentScene, setCurrentScene)

    def update(self, netElapsedTime, windowSize):
        currentScene = self.currentScene
        if currentScene:
            return currentScene.update(netElapsedTime, windowSize)
        else:
            self.currentScene = self._defaultScene
            return DrawingData()
            
    def terminate(self):
        for sceneName in self._scenes:
            scene = self.getScene(sceneName)
            scene.terminate()
