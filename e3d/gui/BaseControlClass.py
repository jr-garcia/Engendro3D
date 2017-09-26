from abc import ABCMeta, abstractmethod
from cycgkit.cgtypes import vec3, vec4, mat4

from ..Base3DObjectClass import Base3DObject
from ..model_management.MaterialClass import *
from .GuiManagerClass import DEFAULT2DSHADERID, GuiManager


class GradientTypesEnum(object):
    noGradient = -1
    Vertical = 0
    Horizontal = 1
    RightCorner = 2
    LeftCorner = 3
    CenterVertical = 4
    CenterHorizontal = 5
    Diagonal1 = 6
    Diagonal2 = 7
    Radial = 8


class PinningEnum(object):
    Top = 'Top'
    Left = 'Left'
    Right = 'Right'
    Bottom = 'Bottom'
    TopLeft = (Top, Left)
    TopRight = (Top, Right)
    BottomLeft = (Bottom, Left)
    BottomRight = (Bottom, Right)
    BottomLeftRight = (Bottom, Left, Right)
    TopLeftRight = (Top, Left, Right)
    TopLeftBottom = (Top, Left, Bottom)
    TopRightBottom = (Top, Right, Bottom)
    all = (Top, Bottom, Left, Right)


class BaseControl(Base3DObject):
    """
        Abstract.
        Base type for all '2D' Gui objects.
       @rtype : BaseControl
    """

    @abstractmethod
    def __init__(self, top, left, width, height, parent, pinning, color, ID, imgID, rotation, borderSize, gradientType):
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
        self._guiMan = parent._guiMan
        self._pinning = []
        self.pinning = pinning
        if not rotation:
            rotation = [0, 0, 0]

        self._top = top
        self._left = left
        self._width = width or 1
        self._height = height or 1

        sw, sh = self._guiMan._window.size
        self._right = sw - (self._left + self._width)
        self._bottom = sh - (self._top + self._height)

        position = vec3(left, top, 0)
        self._realPosition = position
        position = self._convertPixelToWindow(position)

        self._is2D = True
        if ID is None:
            ID = str(id(self))
        super(BaseControl, self).__init__(position, rotation, 1, 1, ID=ID)

        self._material = Material2D()
        self._material._shaderID = DEFAULT2DSHADERID
        size = (width, height)

        if not hasattr(size, '__getitem__'):
            raise TypeError('size must be an object with 2 elements')
        if not all(size):
            raise ValueError('size of 0 not allowed: ' + str(size))
        if not all([int(i) == i for i in size]):
            raise ValueError('only integer size allowed: ' + str(size))

        size = vec3(width, height, 1)
        self._realSize = size
        self._setAbsoluteScale(size)
        self._borderSize = borderSize
        self._borderColor = vec4(0, 0, 0, 1)
        self._setInnerSize()
        assert isinstance(self._guiMan, GuiManager)

        self._material.shaderProperties.append(IntShaderProperty('borderSize', self._borderSize))
        self._material.shaderProperties.append(Vec4ShaderProperty('borderColor', self._borderColor))
        self.borderSize = borderSize
        self.borderColor = vec4(0, 0, 0, 1)
        if color is not None:
            self._material.diffuseColor = color

        if imgID is not None:
            self.backgroundImageID = imgID

        if parent is not None:
            self.attachTo(parent)

        self._set2d()

        self._realScale = vec3(1)
        self._inverseScale = vec3(1)
        self._material.shaderProperties.append(Vec3ShaderProperty('realSize', self._realSize))
        self._material.shaderProperties.append(Vec3ShaderProperty('internalSize', self._innerSize))
        self._material.shaderProperties.append(Vec3ShaderProperty('size', self._scale))
        self._material.shaderProperties.append(Vec3ShaderProperty('realScale', self._realScale))
        self._material.shaderProperties.append(Vec3ShaderProperty('inverseScale', self._inverseScale))
        self._material.shaderProperties.append(Vec3ShaderProperty('relativePosition', self._position))
        self._gradientType = gradientType  # todo:fix this double assigning
        self._material.shaderProperties.append(IntShaderProperty('GradientType', self._gradientType))
        self.gradientType = gradientType

        self._setLastDifferences()
        self._updateRealSizePosition()

    def _setLastDifferences(self):
        self._lastDifferences = (self._top, self._left, self._bottom, self._right)

    @property
    def gradientType(self):
        return self._gradientType

    @gradientType.setter
    def gradientType(self, value):
        self._gradientType = value
        self._material.shaderProperties['GradientType'] = value

    @property
    def pinning(self):
        return self._pinning

    @pinning.setter
    def pinning(self, value):
        if len(value) == 1 or isinstance(value, str):
                raise AttributeError('single value \'{}\' not allowed.'.format(value))
        if isinstance(value, list):
            self._pinning = value
        elif isinstance(value, tuple):
            self._pinning = [v for v in value]
        else:
            pinningVals = (getattr(PinningEnum, n) for n in dir(PinningEnum) if not n.startswith('_'))
            if value not in pinningVals:
                raise AttributeError('pinning value \'{}\' not in PinningEnum'.format(value))
            self._pinning = [value]

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
        self._setInnerSize()
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
        v2 = self._convertWindowToPixel(vec3(self._scale))
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

        self._realSize = v2
        self._scale = self._convertPixelToWindow(v2)
        self._dirty = True
        try:
            self._material.shaderProperties['size'] = self._scale
        except KeyError:
            pass

    size = property(fget=_getAbsoluteScale, fset=_setAbsoluteScale,
                    doc='Size of control in percentage of parent\'s size')

    def getSize(self):
        return self._convertWindowToPixel(self._getAbsoluteScale())

    def _getAbsolutePosition(self):
        npos = self._convertWindowToPixel(vec3(self._position))

        return npos

    def _setAbsolutePosition(self, value):
        npos = value
        self._position = self._convertPixelToWindow(vec3(npos))
        self._material.shaderProperties['relativePosition'] = self._position

    position = property(fget=_getAbsolutePosition, fset=_setAbsolutePosition)

    def _convertPixelToWindow(self, vec3Val):
        x, y = self._guiMan._window.size
        if not all((x, y)):
            return vec3(0)
        sx, sy, sz = vec3Val
        return vec3(sx / x, sy / y, sz)

    def _convertWindowToPixel(self, vec3Val):
        x, y = self._guiMan._window.size
        sx, sy, sz = vec3Val
        return vec3(x * sx, y * sy, sz)

    def _update(self):
        # Todo: implement calbacks
        # self._updateRealSizePosition()
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

    def _updateRealSizePosition(self):
        # if not guiMan._isResized:
        #     return
        parent = self.parent
        if parent is None:
            # x, y = self._guiMan._window.size
            # baseSize = vec3(x, y, 1)
            baseScale = vec3(1)
        else:
            # baseSize = self.parent.realSize
            baseScale = parent.realScale

        realSize = self._realSize
        self._setAbsoluteScale(realSize)
        self._position = self._convertPixelToWindow(self._realPosition)
        self._realScale = ewMul(baseScale, self._scale)
        self._setInnerSize()

        self._inverseScale = ewDiv(parent._inverseScale, self._scale)

        # width, height = self._guiMan._window.size

        self._setPinning()
        self._setLastDifferences()

        self._material.shaderProperties['realSize'] = realSize
        self._material.shaderProperties['internalSize'] = self._innerSize
        self._material.shaderProperties['realScale'] = self._realScale
        self._material.shaderProperties['inverseScale'] = self._inverseScale

    def _setInnerSize(self):
        self._innerSize = self._scale - (ewDiv(self._scale, self._realSize) * (self._borderSize * 2))
        self._innerSize.z = 1

    def _setPinning(self):
        t, l, b, r = self._lastDifferences
        w, h = self._guiMan._window.size
        ow, oh = self._guiMan._window._previousSize

        if PinningEnum.Top in self._pinning:
            nt = t
        else:
            nt = t - (oh - h)

        if PinningEnum.Left in self._pinning:
            nl = l
        else:
            nl = l - (ow - w)

        if PinningEnum.Bottom in self._pinning:
            nb = b
        else:
            nb = b - (oh - h)
        if PinningEnum.Right in self._pinning:
            nr = r
        else:
            nr = r - (ow - w)

        self._top = nt
        self._left = nl
        self._bottom = nb
        self._right = nr
        self._setLastDifferences()
        self._position = self._convertPixelToWindow(vec3(nl, nt, 0))
        self.size = vec3(w - self._left - self._right, h - self._top - self._bottom, 1)
        self._setInnerSize()

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
        # if self._is2D:
        #     npos.y = (1.0 - npos.y - self._innerSize.y)

        npos.x += (self._scale.x - self._innerSize.x) / 2.0
        npos.y -= (self._scale.y - self._innerSize.y) / 2.0
        alteredPositionMatrix = mat4.translation(npos)
        alteredScaleMatrix = mat4.scaling(self._innerSize)
        alteredTransformation = alteredPositionMatrix * self._rotationMatrix * alteredScaleMatrix
        return alteredTransformation

    transformationMinusBorder = property(_getTransformationMinusBorder)

    def _resizeCallback(self):
        self._updateRealSizePosition()
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
            raise TypeError('{} not supported for color assigment. Use list of len=4, vec4 or single number.'.format(
                    str(type(value))))

        return vec4(nvalue)
