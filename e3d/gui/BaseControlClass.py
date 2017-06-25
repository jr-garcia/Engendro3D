from abc import ABCMeta, abstractmethod
from cycgkit.cgtypes import vec3, vec4, mat4

from ..Base3DObjectClass import Base3DObject
from ..model_management.MaterialClass import *
from .GuiManagerClass import DEFAULT2DSHADERID, GuiManager


class BaseControl(Base3DObject):
    """
        Abstract.
        Base type for all '2D' Gui objects.
       @rtype : BaseControl
    """

    @abstractmethod
    def __init__(self, position, size, parent, color=None, imgID=None, rotation=None, borderSize=0):
        """






        @param imgID:
        @type color: list
        @param color:
        @type pos: list
        @type sSize: list
        @rtype : BaseControl
        :param borderSize:
        :type borderSize:
        """
        if not rotation:
            rotation = [0, 0, 0]
        position = [position[0], position[1], 0]

        self._is2D = True
        super(BaseControl, self).__init__(position, rotation, 1, 1)
        self.ID = ''
        self._material = Material2D()
        self._material._shaderID = DEFAULT2DSHADERID
        if not hasattr(size, '__getitem__'):
            raise TypeError('size must be an object with 2 elements')
        if not all(size):
            raise ValueError('size of 0 not allowed: ' + str(size))
        self._setAbsoluteScale(size)
        self._borderSize = borderSize
        self._borderColor = vec4(0, 0, 0, 1)
        self._internalSize = self._scale
        self._guiMan = parent._guiMan
        assert isinstance(self._guiMan, GuiManager)

        self._material.shaderProperties.append(IntShaderProperty('borderSize', self._borderSize))
        self._material.shaderProperties.append(Vec4ShaderProperty('borderColor', self._borderColor))

        if color is not None:
            self._material.diffuseColor = color

        if imgID is not None:
            self._material.diffuseTextureID = imgID

        if parent is not None:
            self.attachTo(parent)

        self._set2d()

        self._realSize = vec3(1)
        self._realScale = vec3(1)
        self._inverseScale = vec3(1)
        self._material.shaderProperties.append(Vec3ShaderProperty('realSize', self._realSize))
        self._material.shaderProperties.append(Vec3ShaderProperty('internalSize', self._internalSize))
        self._material.shaderProperties.append(Vec3ShaderProperty('size', self._scale))
        self._material.shaderProperties.append(Vec3ShaderProperty('realScale', self._realScale))
        self._material.shaderProperties.append(Vec3ShaderProperty('inverseScale', self._inverseScale))
        self._material.shaderProperties.append(Vec3ShaderProperty('relativePosition', self._position))
        self._updateRealSize()

    def _getIs2D(self):
        """

        @rtype : bool
        """
        return self._is2D

    is2D = property(_getIs2D)

    def _getColor(self):
        return self._material.diffuseColor

    def _setColor(self, value):
        self._material.diffuseColor = value

    color = property(_getColor, _setColor)

    def _getOpacity(self):
        return self._material.diffuseColor

    def _setOpacity(self, value):
        self._material.opacity = value

    opacity = property(_getOpacity, _setOpacity)

    def _getImg(self):
        return self._material.diffuseTextureID

    def _setImg(self, value):
        self._material.diffuseTextureID = value
        self._material.useDiffuseTexture = (value != '')

    backgroundImageID = property(_getImg, _setImg)

    def _getUSDTex(self):
        return self._material.upSideDownTextures

    def _setUSDTex(self, value):
        self._material.upSideDownTextures = value

    upSideDownTextures = property(_getUSDTex, _setUSDTex)

    def _getBorder(self):
        return self._borderSize

    def _setBorder(self, val):
        self._borderSize = val
        self._material.shaderProperties['borderSize'] = val
        self._internalSize = self._scale - (ewDiv(self._scale, self._realSize) * (self._borderSize * 2))
        self._internalSize.z = 1
        self._dirty = True

    borderSize = property(_getBorder, _setBorder)

    def _getBorderColor(self):
        return self._borderColor

    def _setBorderColor(self, val):
        self._material.shaderProperties['borderColor'] = val
        self._borderColor = val

    borderColor = property(_getBorderColor, _setBorderColor)

    def _set2d(self):
        if self._parent is not None:
            try:
                self._is2D = self._parent._is2D
            except AttributeError:
                self._is2D = False

    def _getAbsoluteScale(self):
        """

        @rtype : vec3
        """
        v2 = vec3(self._scale)
        return v2

    def _setAbsoluteScale(self, value):
        """

        @type value: list
        """
        if isinstance(value, vec3):
            v2 = value
        elif hasattr(value, '__getitem__'):
            if len(value) == 2:
                v2 = list(value)
                v2.append(1)
            elif len(value) > 2:
                v2 = [1 if v == 0 else v for v in value][0:3]
            elif len(value) == 1:
                v2 = [value[0]] * 3
        else:
            v2 = [value] * 3

        self._scale = vec3(v2)
        self._dirty = True
        try:
            self._material.shaderProperties['size'] = self._scale
        except KeyError:
            pass

    size = property(fget=_getAbsoluteScale, fset=_setAbsoluteScale,
                    doc='Size of control in percentage of parent\'s size')

    def getSize(self):
        return self._getAbsoluteScale()

    def _getAbsolutePosition(self):
        npos = vec3(self._position)
        # if self._is2D:
        #     npos.y = (1.0 - npos.y)

        return npos

    def _setAbsolutePosition(self, value):
        npos = value
        # if self._is2D:
        #     npos.y = (1.0 - npos.y - self._scale.y)
        self._position = vec3(npos)
        self._material.shaderProperties['relativePosition'] = self._position

    position = property(fget=_getAbsolutePosition, fset=_setAbsolutePosition)

    def _update(self):
        # Todo: implement calbacks
        # self._updateRealSize()
        if self._dirty:
            self._updateTransformation()
            self._dirty = False
            for c in self._children:
                c._update()
            return True
        else:
            return False

    def _updateTransformation(self):
        self._updateRotationMatrix()
        npos = vec3(self._position)
        if self._is2D:
            npos.y = (1.0 - npos.y - self._scale.y)
        self._positionMatrix = mat4.translation(npos)
        self._scaleMatrix = mat4.scaling(self._scale)
        self._transformation = self._positionMatrix * self._rotationMatrix * self._scaleMatrix

    def _updateRealSize(self):
        # if not guiMan._isResized:
        #     return
        if self.parent is None:
            x, y = self._guiMan._window.size
            baseSize = vec3(x, y, 1)
            baseScale = vec3(1)
        else:
            baseSize = self.parent.realSize
            baseScale = self.parent.realScale

        self._realSize = ewMul(baseSize, self._scale)
        self._realScale = ewMul(baseScale, self._scale)
        self._internalSize = self._scale - (ewDiv(self._scale, self._realSize) * (self._borderSize * 2))
        self._internalSize.z = 1

        self._inverseScale = ewDiv(self.parent._inverseScale, self._scale)

        self._material.shaderProperties['realSize'] = self._realSize
        self._material.shaderProperties['internalSize'] = self._internalSize
        self._material.shaderProperties['realScale'] = self._realScale
        self._material.shaderProperties['inverseScale'] = self._inverseScale

    def _getInverseScale(self):
        return self._inverseScale

    inverseScale = property(_getInverseScale, doc='Scale needed to pass from local to window scale.')

    def _getRealSize(self):
        return self._realSize

    realSize = property(_getRealSize, doc='Size of control in pixels.')

    def _getRealScale(self):
        return self._realScale

    realScale = property(_getRealScale, doc='Size of control in window percentage.')

    def _getTransformationMinusBorder(self):
        npos = vec3(self._position)
        if self._is2D:
            npos.y = (1.0 - npos.y - self._internalSize.y)

        npos.x += (self._scale.x - self._internalSize.x) / 2.0
        npos.y -= (self._scale.y - self._internalSize.y) / 2.0
        alteredPositionMatrix = mat4.translation(npos)
        alteredScaleMatrix = mat4.scaling(self._internalSize)
        alteredTransformation = alteredPositionMatrix * self._rotationMatrix * alteredScaleMatrix
        return alteredTransformation

    transformationMinusBorder = property(_getTransformationMinusBorder)

    def _resizeCallback(self):
        self._updateRealSize()
        for c in reversed(self._children):
            c._resizeCallback()


def ewMul(a, b):
    return vec3(a.x * b.x, a.y * b.y, a.z * b.z)


def ewDiv(a, b):
    return vec3(a.x / b.x, a.y / b.y, a.z / b.z)


class Material2D(Material):
    def __init__(self):
        Material.__init__(self)
        self.diffuseColor = vec4(0)
        self.emissiveColor = vec4(0)
        self.specularColor = vec4(0)

    def _checkColor(self, value):
        if isinstance(value, vec4):
            nvalue = value
        elif isinstance(value, list):
            if not len(value) == 4:
                raise RuntimeError('wrong number of elements for color assignment. '
                                   'Required 3, got {}'.format(len(value)))
            nvalue = value
        elif isinstance(value, (int, float)):
            nvalue = [value] * 4
        else:
            raise TypeError(
                'type {} not supported for color assigment. Use list of len=4, vec4 or single number.'.format(
                    str(type(value))))

        return vec4(nvalue)
