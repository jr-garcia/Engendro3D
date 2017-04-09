from copy import copy
from cycgkit.cgtypes import *


class Material(object):
    def __init__(self):
        self._ID = ""
        self._difCol = vec4(.5, .5, .5, 1.0)
        self.emissiveColor = vec4(0.0, 0.0, 0.0, 1.0)
        self.specularColor = vec4(1.0, 1.0, 1.0, 1.0)
        self.specularPower = 40.0
        self._shaderID = "default"
        self.textureRepeat = 1.0
        self.diffuseTextureID = ""
        self.specularMapTextureID = ""
        self.emissiveMapTextureID = ""
        self.lightMapTextureID = ""
        self.normalMapTextureID = ""
        self.opacity = 1
        self.useDiffuseTexture = False
        self.useNormalMapTexture = False
        self.upSideDownTextures = False
        self.useSpecularMapTexture = False
        self.useEmissiveMapTexture = False
        self.useLightMapTexture = False
        self.isLightAffected = True
        self.uvOffset = (0, 0)

        self._shaderProps = ShaderPropertiesList()

    def _getShaderProps(self):
        return self._shaderProps

    shaderProperties = property(_getShaderProps)

    def _setDiffCol(self, value):
        """

        @type value: vec4
        """
        if isinstance(value, vec4):
            nvalue = value
        elif isinstance(value, list):
            nvalue = list(value)
            while len(nvalue) != 4:
                nvalue.append(value[0])
        elif isinstance(value, (int, float)):
            nvalue = [value] * 4
        else:
            raise TypeError('type {} not supported for color assigment'.format(str(type(value))))

        self._difCol = nvalue

    def _getDiffCol(self):
        return self._difCol

    diffuseColor = property(_getDiffCol, _setDiffCol, doc='Diffuse Color passed to the shader')

    @staticmethod
    def _fromMaterial(baseMat):
        """
        Receives another Material as base
        @param baseMat:
        @type baseMat: Material
        """
        return copy(baseMat)

    def _getShaderID(self):
        return self._shaderID

    def _setShaderID(self, value):
        if value == "":
            value = "default"
        self._shaderID = value

    shaderID = property(fget=_getShaderID, fset=_setShaderID)

    def _getID(self):
        return self._ID

    ID = property(_getID)

    def __repr__(self):
        return self._ID


class ShaderProperty:
    def __init__(self, shaderName, val):
        self.shaderName = shaderName
        self._val = val

    def getVal(self):
        pass


class FloatShaderProperty(ShaderProperty):
    def getVal(self):
        return float(self._val)


class IntShaderProperty(ShaderProperty):
    def getVal(self):
        return int(self._val)


class Vec3ShaderProperty(ShaderProperty):
    def getVal(self):
        return vec3(self._val)


class Vec4ShaderProperty(ShaderProperty):
    def getVal(self):
        return vec4(self._val)


class Mat4ShaderProperty(ShaderProperty):
    def getVal(self):
        return mat4(self._val)


class BoolShaderProperty(IntShaderProperty):
    pass


class ShaderPropertiesList:
    def __init__(self):
        self.pdict = {}

    def append(self, val):
        if not isinstance(val, ShaderProperty) and not issubclass(ShaderProperty, val):
            raise TypeError('ShaderPropertiesList accepts only ShaderProperty types, got ' + type(val))
        self.pdict[val.shaderName] = val

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError('ShaderPropertiesList index must be string, not ' + type(key))
        self.pdict[key]._val = value

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.pdict[key]
        else:
            return list(self.pdict.values())[key]
