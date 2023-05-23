from collections import OrderedDict, defaultdict
from abc import ABCMeta

from cycgkit.cgtypes import vec3, vec4

from e3d.model_management.MaterialClass import ShaderProperty


class CompilationError(RuntimeError):
    pass


class BaseBackend(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._shaders = None
        self._textures = None
        self._poliCount = 0
        self._culling = False
        self._size = None

    def renderMeshes(self, drawingData):
        pass

    def resize(self, size):
        pass

    def drawAll(self, drawingData):
        pass

    def drawSkybox(self, sky):
        pass

    def switchMultiSample(self, value):
        pass

    def terminate(self):
        pass

    def getShadersManager(self):
        pass

    @staticmethod
    def getRenderTarget():
        pass

    def _getPoliCount(self):
        return self._poliCount

    poligonsDrawnThisUpdate = property(_getPoliCount)

    @staticmethod
    def _getMaxColorAttachments():
        pass

    def setContextState(self):
        pass

    @property
    def culling(self):
        return self._culling

    @culling.setter
    def culling(self, value):
        pass

    @staticmethod
    def create2DTexture(ID, mipmapsNumber, pix, w, h, repeat):
        pass

    def update2DTexture(self, ID, data, fromTuple, toTuple):
        pass

    def getBackBufferContent(self, w, h, destBuffer):
        pass


class ShaderStruct(OrderedDict):
    def __init__(self, *args, **kwds):
        super(ShaderStruct, self).__init__(*args, **kwds)

    def __len__(self):
        res = super(ShaderStruct, self).__len__()
        for it in self.values():
            if isinstance(it, list):
                res += it.__len__() - 2
        return res

    def append(self, key, pyob):
        if key in self.keys():
            self.pop(key)
        self[key] = pyob

    def updateValue(self, key, value):
        self[key] = value


class InstanceData:
    def __init__(self, meshMaterial, defaultParams, transformations=None, modelID=None):
        self._stuff = [meshMaterial, defaultParams, transformations, modelID]

    def __getitem__(self, item):
        return self._stuff[item]

    def __setitem__(self, key, value):
        self._stuff[key] = value

    def __len__(self):
        return len(self._stuff)


class _appendableInstanceData(list):
    def __init__(self):
        super(_appendableInstanceData, self).__init__()

    def append(self, object):
        if not isinstance(object, InstanceData) and not issubclass(type(object), InstanceData):
            raise TypeError('only "InstanceData" type can be appended. got {}'.format(type(object)))
        super(_appendableInstanceData, self).append(object)


class DrawingData:
    def __init__(self):
        self.meshes = set()
        self.modelBoneDirs = {}
        self.instances = defaultdict(_appendableInstanceData)
        self.clearColor = vec3(0.1, .3, .4)
        self.sky = None
        self.defaultSceneParams = None

    def extend(self, otherData):
        assert isinstance(otherData, DrawingData)
        self.instances.update(otherData.instances)
        self.meshes.update(otherData.meshes)


MAXLIGHTS = 8


def setMaterialValues(textures, shader, mat):
    def setText(samplerName, textureID):
        value = textures.getTexture(textureID)
        shader.setTexture(samplerName, value)

    setUnif = shader.setUniformValue
    # setText = shader.setTexture
    setUnif("Opacity", float(mat.opacity))
    setUnif("UseDiffuseTexture", mat.useDiffuseTexture)
    setUnif("UpSideDownTextures", mat.upSideDownTextures)
    setUnif('TextureRepeat', mat._textureRepeatAsVec3)
    if mat.useDiffuseTexture:
        setText("DiffuseTexture", mat.diffuseTextureID)
    # else:
    setUnif("DiffuseColor", mat.diffuseColor)
    setUnif("UseEmissiveMapTexture", mat.useEmissiveMapTexture)
    setUnif("EmissiveColor", mat.emissiveColor)
    if mat.useEmissiveMapTexture:
        setText("EmissiveMapTexture", mat.emissiveMapTextureID)
    setUnif("UseSpecularMapTexture", mat.useSpecularMapTexture)
    # if mat.useSpecularMapTexture:
    setText("SpecularMapTexture", mat.specularMapTextureID)
    # else:
    setUnif("SpecularColor", mat.specularColor)
    setUnif("SpecularPower", max(1.0, float(mat.specularPower)))
    setUnif("UseLightMapTexture", mat.useLightMapTexture)
    if mat.useLightMapTexture:
        setText("LightMapTexture", mat.lightMapTextureID)
    setUnif("UseNormalMapTexture", mat.useNormalMapTexture)
    if mat.useNormalMapTexture:
        setText("NormalMapTexture", mat.normalMapTextureID)

    setUnif('IsLightAffected', mat.isLightAffected)

    setUnif('uvOffset', vec4(mat.uvOffset))
    try:
        setUnif('isText', int(mat._isText))
    except AttributeError:
        pass

    _setMaterialShaderProperties(shader, mat.shaderProperties)


def _setSceneUniforms(shader, params):
    """

    @type shader: Shader
    """
    paramsList = []
    ori = shader._reportInactive
    shader._reportInactive = False

    shader.setTexture('DefaultTexture', params.defaultTexture)
    paramsList.append(('View', params.view))
    paramsList.append(('Projection', params.projection))
    paramsList.append(('ViewProjection', params.ViewProjection))
    paramsList.append(('AmbientColor', params.ambientColor))
    paramsList.append(('zNear', float(params.zNear)))
    paramsList.append(('zFar', float(params.zFar)))
    paramsList.append(('CamPos', params.cameraPosition))
    paramsList.append(('WindowSize', params.windowSize))
    paramsList.append(('fogType', params.fogType))
    paramsList.append(('fogColor', params.fogColor))
    paramsList.append(('fogStart', params.fogStart))
    paramsList.append(('fogEnd', params.fogEnd))
    LightCount = 0

    activeLights = [False] * MAXLIGHTS
    for l in params.lights.values():
        if l.enabled:
            st = l._getShaderStruct(params.view)
            shader.setStruct('Lights[{}]'.format(str(LightCount)), st)
            activeLights[LightCount] = True
            LightCount += 1

    paramsList.append(('activeLights[0]', activeLights))
    shader.setUniformsList(paramsList)

    shader._reportInactive = ori


def _setObjectUniforms(shader, params):
    """

    @type shader: Shader
    """
    paramsList = []
    ori = shader._reportInactive
    shader._reportInactive = False

    paramsList.append(("Model", params.model))
    paramsList.append(("ModelView", params.ModelView))
    paramsList.append(("ModelViewProjection", params.ModelViewProjection))
    paramsList.append(("ModelProjection", params.ModelProjection))
    paramsList.append(("ModelInverse", params.ModelInverse))
    paramsList.append(("ModelInverseTranspose", params.ModelInverseTranspose))
    paramsList.append(("ModelViewInverse", params.ModelViewInverse))
    paramsList.append(("ModelViewInverseTranspose", params.ModelViewInverseTranspose))
    paramsList.append(("NormalMatrix", params.NormalMatrix))
    paramsList.append(("HasBones", params.hasBones))

    shader.setUniformsList(paramsList)
    shader._reportInactive = ori


def _setMaterialShaderProperties(shader, props):
    paramsList = []
    for p in props:
        assert isinstance(p, ShaderProperty)
        paramsList.append((p.nameInShader, p.getVal()))

    shader.setUniformsList(paramsList)


def _setBoneTransformationsForMesh(shader, transformations, moelboneDir):
    shader.setBoneTransformations(transformations, moelboneDir)
