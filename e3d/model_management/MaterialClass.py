from copy import copy
from cycgkit.cgtypes import *


class Material(object):
    def __init__(self):
        self._ID = "[{}]".format(id(self))
        self._difCol = vec3(.5, .5, .5)
        self._emCol = vec3(0.0, 0.0, 0.0)
        self._specCol = vec3(1.0, 1.0, 1.0)
        self.specularPower = 40.0
        self._shaderID = "default"
        self._textureRepeat = (1.0, 1.0)
        self._textureRepeatAsVec3 = vec3(1.0, 1.0, 0)
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

    def setDefaultNormalMap(self):
        self.normalMapTextureID = '_defaultNM'
        self.useNormalMapTexture = True

    def _getShaderProps(self):
        return self._shaderProps

    shaderProperties = property(_getShaderProps)

    def _setDiffCol(self, value):
        self._difCol = self._checkColor(value)

    def _getDiffCol(self):
        return self._difCol

    diffuseColor = property(_getDiffCol, _setDiffCol, doc='Diffuse color passed to the shader')

    def _setEmCol(self, value):
        self._emCol = self._checkColor(value)

    def _getEmCol(self):
        return self._emCol

    emissiveColor = property(_getEmCol, _setEmCol, doc='Emissive color passed to the shader')

    def _setSpecCol(self, value):
        self._specCol = self._checkColor(value)

    def _getSpecCol(self):
        return self._specCol

    specularColor = property(_getSpecCol, _setSpecCol, doc='Specular color passed to the shader')

    def _checkColor(self, value):
        if isinstance(value, vec3):
            nvalue = value
        elif isinstance(value, list):
            if not len(value) == 3:
                raise RuntimeError('wrong number of elements for color assignment. '
                                   'Required 3, got {}'.format(len(value)))
            nvalue = value
        elif isinstance(value, (int, float)):
            nvalue = [value] * 3
        else:
            raise TypeError('type {} not supported for color assigment. Use list of len=3, vec3 or single number.'.format(str(type(value))))

        return vec3(nvalue)

    @property
    def textureRepeat(self):
        return self._textureRepeat

    @textureRepeat.setter
    def textureRepeat(self, value):
        if isinstance(value, (int, float)):
            value = (value, value)
        elif not hasattr(value, '__getitem__') or len(value) < 2:
            raise TypeError('repeat value must be a 2-tuple')

        self._textureRepeat = value
        self._textureRepeatAsVec3[0] = value[0]
        self._textureRepeatAsVec3[1] = value[1]

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
