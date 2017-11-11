import os
from json import dump, load
from collections import OrderedDict, defaultdict
import numpy as np
from cycgkit.cgtypes import mat4, vec3
from freetype import Face

from ..Base3DObjectClass import DefaultObjectParameters
from .LayerClass import Layer
from .FontRendering import CharRangesEnum
from .FontRendering.MSDFAtlasRenderer import NAMEFORMATSTRING, render, AtlasInfo, CharData
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
        self.fontSizes = defaultdict(dict)
        self.fontFilePaths = {}
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
        self.eventsListener = EventsListener()
        eventsListener = self.eventsListener
        eventsListener.onWindowEvent = self._onWindowEventCallback
        eventsListener.onMouseEvent = self._onMouseEventCallback

        from .._engine import PathPiece
        self.fontsCache = PathPiece((os.path.dirname(__file__), 'cache'))
        if not os.path.exists(self.fontsCache):
            os.mkdir(self.fontsCache)

        vertices = np.array([[-.5, .5, 0], [-.5, -.5, 0], [.5, -.5, 0], [.5, .5, 0]], dtype=np.float32)
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

        self.resizeProjection()
        self._window.events.addListener('_winreslistgui', self.eventsListener)

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
            layer = Layer(ID, self, visible)
            if order == -1 or len(self._layers) < order + 1:
                self._layersOrder.append(layer)
            else:
                self._layersOrder.insert(order + 1, layer)

            self._layers[ID] = layer
            return layer

    def moveLayerTo(self, ID, position):
        """
        Move layer 'ID' from its place to 'position'


        @type ID: str
        @type position: : int
        """
        layer = self._layers[ID]
        order = self._layersOrder
        order.remove(layer)
        order.insert(position, layer)

    def deleteLayer(self, ID):
        """


        @type ID: str
        """
        # fixme!
        raise NotImplementedError('Delete layer in GuiManager. Please report it.')

    def hasLayerID(self, ID):
        return ID in self._layers

    def getLayerOrder(self, layerID):
        return self._layersOrder.__getitem__(self._layers[layerID])

    @staticmethod
    def orderInstances(instances):
        orderedPerShader = defaultdict(list)
        for key, appendable in instances.items():
            for i in appendable:
                orderedPerShader[i._stuff[0]._shaderID].append(i)

            finals = []
            for val in orderedPerShader.values():
                finals.extend(val)

            instances.clear()
            instances[key].extend(finals)

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

        for layer in reversed(self._layersOrder):
            if layer.visible:
                layer._update()
                for child in reversed(layer._children):
                    if child.visible and not child.isOutBounds():
                        self._buildLayerDrawingData(child, newDrawingData)

        # GuiManager.orderInstances(newDrawingData.instances)  # todo: implement GUI z-ordering to enable this
        return newDrawingData

    def _buildLayerDrawingData(self, currentControl, layerDrawingData):
        defaultObjectParams = DefaultObjectParameters()
        defaultObjectParams.view = self.view
        defaultObjectParams.projection = self.projectionMatrix
        defaultObjectParams.hasBones = False

        defaultObjectParams.model = currentControl.transformation
        defaultObjectParams.construct()

        meshid = self.quadmesh.ID
        meshMat = currentControl._material
        layerDrawingData.instances[meshid].append(InstanceData(meshMat, defaultObjectParams))

        for child in reversed(currentControl._children):
            if child.visible and not child.isOutBounds():
                self._buildLayerDrawingData(child, layerDrawingData)

    @staticmethod
    def convertCharData(data):
        d = OrderedDict()
        for e, v in data.items():
            f = dict()
            u = dir(v)
            for l in u:
                if not l.startswith('_'):
                    val = getattr(v, l)
                    f[l] = val
            d[int(e)] = f
        return d

    @staticmethod
    def convertToJsonable(rangeInfo):
        f = dir(rangeInfo)
        dictio = dict()
        for l in f:
            if not l.startswith('_'):
                if l == 'charDataDict':
                    dictio['finalLocations'] = GuiManager.convertCharData(getattr(rangeInfo, l))
                else:
                    dictio[l] = getattr(rangeInfo, l)

        dictio['size'] = (dictio['width'], dictio['height'])
        dictio['lineMargins'] = (rangeInfo.upperMargin, rangeInfo.lowerMargin)
        return dictio

    @staticmethod
    def convertFromJsoned(rangeInfoDict):
        rangeInfo = AtlasInfo(**rangeInfoDict)
        newCharData = OrderedDict()
        for n, val in rangeInfo.charDataDict.items():
            newCharData[int(n)] = CharData()
            for k in val.keys():
                setattr(newCharData[int(n)], k, val[k])
        rangeInfo.charDataDict = newCharData
        return rangeInfo

    def loadFont(self, ID, fontPath, baseSize=32, maxAtlasWidth=1024, charRange=CharRangesEnum.latin, force=False):
        destinationFolder = self.fontsCache
        fontName = os.path.splitext(os.path.basename(fontPath))[0]
        fullDestPath = os.path.abspath(destinationFolder)
        finalPath = os.path.join(fullDestPath,
                                 NAMEFORMATSTRING.format(fontName=fontName, rangeName=charRange[0], format=SAVEFORMAT))
        infoPath = os.path.splitext(finalPath)[0]
        finalInfoPath = INFOFORMATSTRING.format(fontPath=infoPath)
        if not os.path.exists(finalPath) or force:
            fontRangeInfo = render(fontPath, baseSize, maxAtlasWidth, destinationFolder, SAVEFORMAT, charRange)
            try:
                with open(finalInfoPath, 'w') as dest:
                    dump(fontRangeInfo, dest, default=GuiManager.convertToJsonable)
            except Exception:
                os.remove(finalInfoPath)
                os.remove(finalPath)
                raise
        else:
            with open(finalInfoPath, 'r') as dest:
                fontRangeInfo = GuiManager.convertFromJsoned(load(dest))

        fontTextureName = FONTTEXTUREIDSTRING.format(ID)
        self.engine.textures.loadTexture(finalPath, fontTextureName, mipmapsNumber=0, repeat=False, force=True)
        self.fontInfos[ID] = fontRangeInfo
        self.fontTextureNames[ID] = fontTextureName
        self.fontFilePaths[ID] = fontPath

    def _onWindowEventCallback(self, e):
        if e.eventName == 'resized':
            self.resizeProjection()
            self._resizeLayers()

    def _onMouseEventCallback(self, event):
        activeLayer = None
        for layer in self._layersOrder:
            if layer.visible:
                activeLayer = layer
                break
        if activeLayer is not None:
            activeLayer._handleMouseEvent(event)

    def resizeProjection(self):
        width, height = self._window.size
        self.projectionMatrix = mat4.orthographic(0, width, height, 0, 0, -1)

    def _resizeLayers(self):
        for layer in self._layersOrder:
            if layer.visible:
                layer._resizeCallback()

    def getFontSizeInPixels(self, sizeInPoints, fontID):
        size = self.fontSizes[sizeInPoints].get(fontID)
        if size is None:
            path = self.fontFilePaths[fontID]
            if path is None:
                raise RuntimeError('font info not found. Is the font loaded?')
            face = Face(path)
            hdpi, vdpi = self._window.getCurrentDPIs()
            face.set_char_size(0, sizeInPoints * 64, hdpi, vdpi)
            size = face.size.height / 64
            self.fontSizes[sizeInPoints][fontID] = size
        return size
