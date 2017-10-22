from abc import abstractmethod

from cycgkit.cgtypes import vec3

from e3d.commonValues import ewDiv, ewMul
from .GuiManagerClass import DEFAULT2DSHADERID, GuiManager
from ..Base3DObjectClass import Base3DObject
from ..model_management.MaterialClass import *


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
    NoPinning = 'NoPinning'
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
    def __init__(self, left, top, width, height, parent, pinning, color, ID, imgID, rotation, borderSize, gradientType):
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
        self._parent = parent
        self._pinning = []
        self.pinning = pinning
        if not rotation:
            rotation = [0, 0, 0]

        self._is2D = True

        self._top = top
        self._left = left
        self._width = width
        self._height = height
        # self._inverseScale = vec3(1)
        self.__offset = vec3(0.5, 0.5, 0)

        position = vec3(left, top, 0)

        if ID is None:
            ID = str(id(self))
        super(BaseControl, self).__init__(position, rotation, 1, 1, ID=ID, parent=parent)

        self._updateLastPositions()

        self._material = Material2D()
        material = self._material
        material._shaderID = DEFAULT2DSHADERID

        if not all((width, height)):
            raise ValueError('size of 0 not allowed: ' + str((width, height)))
        # if not all((int(i) == i for i in size)):
        #     raise ValueError('only integer size allowed: ' + str(size))

        size = vec3(width, height, 1)
        self._pixelSize = size
        self._previousSize = self.pixelSize
        self._setAbsoluteScale(size)
        self._borderSize = borderSize
        self._borderColor = vec4(0, 0, 0, 1)
        self._setInnerSize()
        # assert isinstance(self._guiMan, GuiManager)

        material.shaderProperties.append(IntShaderProperty('borderSize', self._borderSize))
        material.shaderProperties.append(Vec4ShaderProperty('borderColor', self._borderColor))
        self.borderSize = borderSize
        self.borderColor = vec4(0, 0, 0, 1)
        if color is not None:
            material.diffuseColor = color

        if imgID is not None:
            self.backgroundImageID = imgID

        self._set2d()

        material.shaderProperties.append(Vec3ShaderProperty('pixelSize', self._pixelSize))
        material.shaderProperties.append(Vec3ShaderProperty('internalSize', self._innerSize))
        material.shaderProperties.append(Vec3ShaderProperty('size', self._scale))
        material.shaderProperties.append(Vec3ShaderProperty('realScale', self._scale))
        # material.shaderProperties.append(Vec3ShaderProperty('inverseScale', self._inverseScale))
        material.shaderProperties.append(Vec3ShaderProperty('relativePosition', self._position))
        self._gradientType = gradientType  # todo:fix this double assigning
        material.shaderProperties.append(IntShaderProperty('GradientType', self._gradientType))
        self.gradientType = gradientType

        self._setLastDifferences()
        self._updateSizeProperties()

    def _updateLastPositions(self):
        pw, ph = self._guiMan._window.size
        left = self.position.x
        top = self.position.y
        self._right = pw - (left + self._width)
        self._bottom = ph - (top + self._height)
        self._lastDifferences = left, top, self._bottom, self._right

    @property
    def _offset(self):
        return self.__offset

    def _setLastDifferences(self):
        self._lastDifferences = (self._left, self._top, self._bottom, self._right)

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
        if len(value) == 1 or isinstance(value, str) and value != PinningEnum.NoPinning:
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
        material = self._material
        material.diffuseTextureID = value
        material.useDiffuseTexture = (value != '')

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
        v2 = self._scale
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
                v2 = (1 if v == 0 else v for v in value)[0:3]
            else:
                v2 = (value[0]) * 3
        else:
            v2 = (value, value, value)

        self._previousSize = vec3(self._pixelSize)
        self._pixelSize = v2
        try:
            self._material.shaderProperties['pixelSize'] = v2
        except KeyError:
            pass
        self._scale = v2
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

        return npos

    def _setAbsolutePosition(self, value):
        npos = value
        self._position = vec3(npos)
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

    def _convertPixelToParent(self, vec3Val):
        x, y, _ = self.parent.size
        if not all((x, y)):
            return vec3(0)
        sx, sy, sz = vec3Val
        return vec3(sx / x, sy / y, sz)

    def _convertParentToPixel(self, vec3Val):
        x, y, _ = self.parent.size
        sx, sy, sz = vec3Val
        return vec3(x * sx, y * sy, sz)

    def _updateRotationMatrix(self):
        super(BaseControl, self)._updateRotationMatrix()
        angle = self.rotation.z
        angle = abs(angle)
        amount = 0
        if angle < 0:
            if angle > 180:
                angle = angle / 2
            if angle <= 90:
                amount = angle / 90
            elif angle > 90:
                amount = (180 - angle) / 90

        self.rotationAmount = amount * 100

    def _updateTransformation(self):
        self._updateRotationMatrix()
        parent = self._parent
        parentCenter = (parent.size / 2)
        parentCenter.z = 0
        position = vec3(self._position)
        rotation = self._rotationMatrix

        scaledOffset = ewMul(self._offset, self._scale)
        position += scaledOffset
        # parentCenter -= scaledOffset
        parentTrans = mat4.translation(parent._position)
        pCTrans = mat4.translation(parentCenter)
        self._positionMatrix = mat4.translation(position)
        self._scaleMatrix = mat4.scaling(self._scale)
        self._transformation = parentTrans * pCTrans * parent._rotationMatrix * pCTrans.inversed() * \
                               self._positionMatrix * rotation * self._scaleMatrix

    # def _getTransformationMinusBorder(self):
    #     npos = vec3(self._position)
    #
    #     npos.x += (self._scale.x - self._innerSize.x) / 2.0
    #     npos.y -= (self._scale.y - self._innerSize.y) / 2.0
    #     npos += ewMul(self._offset, self.scale)
    #     alteredPositionMatrix = mat4.translation(npos)
    #     alteredScaleMatrix = mat4.scaling(self._innerSize)
    #     alteredTransformation = alteredPositionMatrix * alteredScaleMatrix * self._rotationMatrix
    #     return alteredTransformation
    #
    # transformationMinusBorder = property(_getTransformationMinusBorder)

    def _updateSizeProperties(self):
        # self._inverseScale = ewDiv(self.parent._inverseScale, self._scale)

        material = self._material
        material.shaderProperties['pixelSize'] = self._pixelSize
        material.shaderProperties['internalSize'] = self._innerSize
        material.shaderProperties['realScale'] = self._scale
        # material.shaderProperties['inverseScale'] = self._inverseScale

    def _setInnerSize(self):
        self._innerSize = self.size - vec3(self._borderSize * 2)
        self._innerSize.z = 1

    def _setPinning(self):
        l, t, b, r = self._lastDifferences
        w, h = self._guiMan._window.size
        ow, oh = self._guiMan._window._previousSize

        pinning = self._pinning
        if PinningEnum.NoPinning in pinning:
            return
        else:
            if PinningEnum.Top in pinning:
                nt = t
            else:
                nt = t - (oh - h)

            if PinningEnum.Left in pinning:
                nl = l
            else:
                nl = l - (ow - w)

            if PinningEnum.Bottom in pinning:
                nb = b
            else:
                nb = b - (oh - h)
            if PinningEnum.Right in pinning:
                nr = r
            else:
                nr = r - (ow - w)

        self._top = nt
        self._left = nl
        self._bottom = nb
        self._right = nr
        self._setLastDifferences()
        self._position = vec3(nl, nt, 0)
        self.size = vec3(max(w - nl - nr, 1), max(h - nt - nb, 1), 1)
        self._setInnerSize()

    def _getInverseScale(self):
        return self._inverseScale

    inverseScale = property(_getInverseScale, doc='Scale needed to pass from local to window scale.')

    def _getpixelSize(self):
        return self._pixelSize

    pixelSize = property(_getpixelSize, doc='Size of control in pixels.')

    def _getRealScale(self):
        return self._scale

    realScale = property(_getRealScale, doc='Size of control in window percentage.')

    def _resizeCallback(self):
        self._setPinning()
        self._updateSizeProperties()
        for c in reversed(self._children):
            c._resizeCallback()

    def rotateX(self, angle):
        if self.is2D:
            raise RuntimeError('2d objects can only be rotated using \'rotate2D\'')

    def rotateY(self, angle):
        if self.is2D:
            raise RuntimeError('2d objects can only be rotated using \'rotate2D\'')

    def rotateZ(self, angle):
        if self.is2D:
            raise RuntimeError('2d objects can only be rotated using \'rotate2D\'')

    def rotate2D(self, angle):
        super(BaseControl, self).rotateZ(angle)

    def moveForward(self, amount):
        if self.is2D:
            raise RuntimeError('2d objects can not move Forward')

    def moveBackward(self, amount):
        if self.is2D:
            raise RuntimeError('2d objects can not move Backward')

    def addMove(self, vector):
        super(BaseControl, self).addMove(vector)
        self._updateLastPositions()


class Material2D(Material):
    def __init__(self):
        Material.__init__(self)
        self.diffuseColor = vec4(0)
        self.emissiveColor = vec4(0)
        self.specularColor = vec4(0)
        self._isText = False

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
