import os
from json import dump, load
from collections import OrderedDict, defaultdict
import numpy as np
from cycgkit.cgtypes import mat4, vec3

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

        # GuiManager.orderInstances(newDrawingData.instances)  # todo: implement GUI z-ordering to enable this
        return newDrawingData

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
            except:
                os.remove(finalInfoPath)
                os.remove(finalPath)
                raise
        else:
            with open(finalInfoPath, 'r') as dest:
                fontRangeInfo = GuiManager.convertFromJsoned(load(dest))

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
