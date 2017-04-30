from __future__ import print_function
import os

from ..LoggerClass import logger, logLevelsEnum
from .ModelClass import Model
from .geomModelsModule import geomTypeEnum

# from ThreadedSystemClass import ThreadedSystem


class ModelsManager(object):
    def __init__(self):
        super(ModelsManager, self).__init__()
        self._modelsCache = {}
        self.textures = None
        self._context = None
        self._shaders = None
        self._lastUVs = []
        self._lastChannel = -1
        self._uvsFilled = False
        self._engine = None

    def initialize(self, engine):
        """
        Models manager Class
        @param engine:
        @type engine:
        """
        from glaze.GL import glGetError
        print(glGetError(), "models")
        self._engine = engine
        self.textures = engine.textures
        self._shaders = engine.shaders

    def loadModel(self, filename, ID, useChannel0AsUVChannel=-1, forceStatic=False, preCalculateFrames=1):
        """
        Load a 3d model from disk.

        If useChannel0AsUVChannel > 0
        this model's UV channel 0 will replace previous loaded model's
        UV channel with this number.

        To use  the loaded model, add a model to a scene,
        using the ID given here.

        Raises error on failure.

        @type forceStatic: bool
        @type preCalculateFrames: int
        @rtype : None
        @type filename: str
        @type ID: str
        @type useChannel0AsUVChannel: int
        @param filename: The path to the model.
        @param ID: The model's ID for later retrieval.
        @param useChannel0AsUVChannel: Use this model's uv's as the next loaded model's uv channel
         equal to this parameter.
        @param forceStatic: Load the model as static (no bones, no animations) regardless of it's real condition.
        @param preCalculateFrames: For animated meshes, precalculate frames of all the animations using this quality.
          If set to -1, disable precalculations. If bigger that -1, will increase loading time exponentially, but will
           increase performance since the start of the animations. Recomended to set to -1 only when debugging.
        """

        logger.meassure('starts load model')

        if useChannel0AsUVChannel > 0:
            try:
                _ = Model(filename, self._engine, self._context, preCalculateFrames,
                          useChannel0AsUVChannel, self._lastUVs, False, forceStatic)
                self._lastChannel = useChannel0AsUVChannel
                self._uvsFilled = True
            except Exception as ex:
                raise Exception("Error loading UV channel:" + ex.message)
        else:
            if ID not in self._modelsCache.keys():
                try:
                    if len(self._lastUVs) > 0:
                        useChannel0AsUVChannel = self._lastChannel
                    mod = Model.fromFile(filename, self._engine, preCalculateFrames,
                                         useChannel0AsUVChannel, self._lastUVs, self._uvsFilled, forceStatic)
                    self._modelsCache[ID] = mod
                    self._lastUVs = []
                    self._lastChannel = -1
                except Exception:
                    raise

    def loadSphere(self, ID, segmentsU=16, segmentsV=None, radius=4.0):
        try:
            if ID in self._modelsCache.keys():
                raise KeyError('The ID already exist.')
            if segmentsV is None:
                segmentsV = segmentsU
            dictInfo = {'radius': radius, 'segmentsU': segmentsU, 'segmentsV': segmentsV}
            mod = Model.fromGeometryModel(self._engine, ID, geomTypeEnum.sphere, dictInfo)
            self._modelsCache[ID] = mod
            self._lastUVs = []
            self._lastChannel = -1
        except:
            raise

    def loadBox(self, ID, size, segmentsX=1, segmentsY=None, segmentsZ=None):
        try:
            ssize = None
            if ID in self._modelsCache.keys():
                raise KeyError('The ID already exist.')
            if isinstance(size, (int, float)):
                ssize = [size] * 3
            elif isinstance(size, list) and len(size) in [1, 3]:
                if len(size) == 3:
                    ssize = size
                elif len(size) == 1:
                    ssize = [size[0], size[0], size[0]]
                else:
                    raise TypeError('Size should be a 3 element list of numbers, or a single number.')

            segmentsY = segmentsY or segmentsX
            segmentsZ = segmentsZ or segmentsX

            dictInfo = {'size': ssize, 'segmentsX': segmentsX, 'segmentsY': segmentsY, 'segmentsZ': segmentsZ}
            mod = Model.fromGeometryModel(self._engine, ID, geomTypeEnum.box, dictInfo)
            self._modelsCache[ID] = mod
            self._lastUVs = []
            self._lastChannel = -1
        except:
            raise

    def loadPlane(self, ID, size, segmentsX=1, segmentsY=None):
        try:
            ssize = None
            if ID in self._modelsCache.keys():
                raise KeyError('The ID already exist.')
            if type(size) in [int, float]:
                ssize = [size] * 2
            elif isinstance(size, list):
                if len(size) == 2:
                    ssize = size
                else:
                    ssize = [size[0]] * 2
            dictInfo = {'size': ssize, 'segmentsX': segmentsX, 'segmentsY': segmentsY}
            mod = Model.fromGeometryModel(self._engine, ID, geomTypeEnum.plane, dictInfo)
            self._modelsCache[ID] = mod
            self._lastUVs = []
            self._lastChannel = -1
        except Exception as ex:
            raise

    def loadCapsule(self, ID, radius, height):
        raise NotImplementedError('Please report.')

    def exists(self, filename):
        """


        @param filename:
        @rtype: bool
        """
        return filename in self._modelsCache.keys()

    def _getModel(self, ID):
        """

        @rtype : Model
        """
        return self._modelsCache.get(ID)
