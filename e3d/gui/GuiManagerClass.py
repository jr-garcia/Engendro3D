import os
from pickle import dump, load
import numpy as np
from cycgkit.cgtypes import mat4, vec3

from ..Base3DObjectClass import DefaultObjectParameters
from .LayerClass import Layer
from .FontRendering import CharRangesEnum
from .FontRendering.MSDFAtlasRenderer import NAMEFORMATSTRING, render
from ..backends.base_backend import DrawingData, InstanceData
from ..model_management.MeshClass import Mesh, NormalsCalculationTypeEnum, UVCalculationTypeEnum
from ..scene_management.SceneClass import DefaultSceneParameters
from ..events_processing.EventsListenerClass import EventsListener

SAVEFORMAT = 'png'
DEFAULT2DSHADERID = 'default2D'
DEFAULT2DTEXTSHADERID = 'default2Dtext'
INFOFORMATSTRING = '{fontPath}.info'
FONTTEXTUREIDSTRING = '{}_fonttex'


class GuiManager:
    def __init__(self):
        self.fontTextureNames = {}
        self.engine = None
        self.backend = None
        self._currentMat = None
        self._layers = {}
        self._layersOrder = []
        self._objects = {}
        self.view = mat4.identity()
        self.defaultTexture = None
        self.fontInfos = {}
        self._window = None
        self.resizeListener = EventsListener()
        self.resizeListener.onWindowEvent = self._onWindowEventCallback

        from ..engine import PathPiece
        self.fontsCache = PathPiece((os.path.dirname(__file__), 'cache'))
        if not os.path.exists(self.fontsCache):
            os.mkdir(self.fontsCache)

        vertices = np.array([[0, 1, 0], [0, 0, 0], [1, 0, 0], [1, 1, 0]], dtype=np.float32)
        faces = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
        self.quadmesh = Mesh.fromObjectInfo(vertices, faces, ([0, 0, 0], [1, 1, 1]), UVCalculationTypeEnum.planar,
                                            NormalsCalculationTypeEnum.hard, materialIndex=1)

        '''
        orthographic:

        GLdouble  left,
        GLdouble  right,
        GLdouble  bottom,
        GLdouble  top,
        GLdouble  nearVal,
        GLdouble  farVal
        '''
        self.projectionMatrix = mat4.orthographic(0, 1, 0, 1, 0, -1)

    def initialize(self, engine, backend, defaultTexture, window):
        self.engine = engine
        shadersDefaultPath = engine.path.defaults.shaders
        self.backend = backend
        self._window = window
        # load default 2d shader
        p = os.path.join(shadersDefaultPath, 'default_2D_')
        vsp = p + 'VS.glsl'
        fsp = p + 'FS.glsl'
        backend.shaders.loadShader(vsp, fsp, DEFAULT2DSHADERID)

        # store ref to default texture
        self.defaultTexture = defaultTexture

        # load default font
        self.loadFont('default', os.path.join(self.engine.path.defaults.fonts, 'code', 'Code200365k.ttf'))

        # load default 2d text shader
        p = os.path.join(shadersDefaultPath, 'default_2D_text_')
        vsp = p + 'VS.glsl'
        fsp = p + 'FS.glsl'
        backend.shaders.loadShader(vsp, fsp, DEFAULT2DTEXTSHADERID)
        self._window.events.addListener('_winreslistgui', self.resizeListener)

    def addLayer(self, ID, order=-1, visible=True):
        """


        @rtype : e3d.gui.LayerClass.Layer
        @type order: int
        @type ID: str
        @param visible:
        @type visible:
        """
        if ID in self._layers:
            raise KeyError('ID already exist.')
        else:
            l = Layer(ID, self, visible)
            if order == -1 or len(self._layers) < order + 1:
                self._layersOrder.append(l)
            else:
                self._layersOrder.insert(order + 1, l)

            self._layers[ID] = l
            return l

    def moveLayer(self, ID, order=-1):
        """



        @type order: int
        @type ID: str
        """
        pass

    def deleteLayer(self, ID):
        """


        @type ID: str
        """
        # fixme!
        raise NotImplementedError('Delete layer in GuiManager. Please report it.')

    def getLayerOrder(self, layerID):
        return self._layersOrder.__getitem__(self._layers[layerID])

    def updateGui(self, windowSize):
        newDrawingData = DrawingData()

        defaultSceneParams = DefaultSceneParameters()
        defaultSceneParams.defaultTexture = self.defaultTexture
        defaultSceneParams.view = self.view
        defaultSceneParams.projection = self.projectionMatrix
        defaultSceneParams.windowSize = vec3(windowSize[0], windowSize[1], 1)
        defaultSceneParams.construct()
        newDrawingData.defaultSceneParams = defaultSceneParams

        newDrawingData.meshes.add(self.quadmesh)

        for layer in self._layersOrder:
            if layer.visible:
                layer._update()
                for child in layer._children:
                    if child.visible:
                        self._buildLayerDrawingData(child, None, newDrawingData)

        return newDrawingData

    def _buildLayerDrawingData(self, child, trans, layerDrawingData):
        defaultObjectParams = DefaultObjectParameters()
        defaultObjectParams.view = self.view
        defaultObjectParams.projection = self.projectionMatrix
        defaultObjectParams.hasBones = False

        defaultObjectParams.model = child._transformation
        downTrans = child.transformationMinusBorder
        if trans is not None:
            defaultObjectParams.model = trans * defaultObjectParams.model
            downTrans = trans * child.transformationMinusBorder

        defaultObjectParams.construct()

        meshid = self.quadmesh.ID

        meshMat = child._material
        layerDrawingData.instances[meshid].append(InstanceData(meshMat, defaultObjectParams))

        for c in child._children:
            if c.visible:
                self._buildLayerDrawingData(c, downTrans, layerDrawingData)

    def loadFont(self, ID, fontPath, baseSize=34, maxAtlasWidth=1024, charRange=CharRangesEnum.latin, force=False):
        destinationFolder = self.fontsCache
        fontName = os.path.splitext(os.path.basename(fontPath))[0]
        fullDestPath = os.path.abspath(destinationFolder)
        finalPath = os.path.join(fullDestPath,
                                 NAMEFORMATSTRING.format(fontName=fontName, rangeName=charRange[0], format=SAVEFORMAT))
        infoPath = os.path.splitext(finalPath)[0]
        if not os.path.exists(finalPath) or force:
            fontRangeInfo = render(fontPath, baseSize, maxAtlasWidth, destinationFolder, SAVEFORMAT, charRange)
            with open(INFOFORMATSTRING.format(fontPath=infoPath), 'wb') as dest:
                dump(fontRangeInfo, dest, protocol=2)
        else:
            with open(INFOFORMATSTRING.format(fontPath=infoPath), 'rb') as dest:
                try:
                    fontRangeInfo = load(dest, encoding='bytes')
                except TypeError:
                    fontRangeInfo = load(dest)

        fontTextureName = FONTTEXTUREIDSTRING.format(ID)
        self.engine.textures.loadTexture(finalPath, fontTextureName, repeat=False, force=True)
        self.fontInfos[ID] = fontRangeInfo
        self.fontTextureNames[ID] = fontTextureName

    def _onWindowEventCallback(self, e):
        if e.eventName == 'resized':
            self._resizeOcurred()

    def _resizeOcurred(self):
        for layer in self._layersOrder:
            if layer.visible:
                layer._resizeCallback()
