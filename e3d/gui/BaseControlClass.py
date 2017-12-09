from abc import abstractmethod

from cycgkit.cgtypes import vec3

from ..commonValues import ewDiv, ewMul
from .GuiManagerClass import DEFAULT2DSHADERID, GuiManager
from ..Base3DObjectClass import Base3DObject
from ..commonValues import ewMul
from ..model_management.MaterialClass import *
from .LayerClass import ResponsiveControl
from ..events_processing.eventClasses import MouseEventNames


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


class Align2DEnum(object):
    Center = 'Center'
    Top = 'Top'
    Left = 'Left'
    Right = 'Right'
    Bottom = 'Bottom'


class ClippingRect(object):
    def __init__(self, windowSize):
        self._top = None
        self._left = None
        self._bottom = None
        self._right = None
        self._windowSize = windowSize

    def __repr__(self):
        return str(self.toVec4())

    @property
    def top(self):
        return self._top

    @top.setter
    def top(self, value):
        if value > self._top or self._top is None:
            self._top = value

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, value):
        if value > self._left or self._left is None:
            self._left = value

    @property
    def bottom(self):
        return self._bottom

    @bottom.setter
    def bottom(self, value):
        if value < self._bottom or self._bottom is None:
            self._bottom = value

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, value):
        if value < self._right or self._right is None:
            self._right = value

    def isFull(self):
        return all((v is not None for v in (self._left, self._top, self._right, self._bottom)))

    def toVec4(self):
        w, h = self._windowSize
        return vec4(self._left or 0, self._top or 0, self._right or w, self._bottom or h)


class BaseControl(Base3DObject, ResponsiveControl):
    """
        Abstract.
        Base type for all '2D' Gui objects.
       @rtype : BaseControl
    """

    @abstractmethod
    def __init__(self, left, top, width, height, parent, pinning, color, ID, imgID, rotation, style):
        self._hTextAlign = Align2DEnum.Center
        self._vTextAlign = Align2DEnum.Left
        self._guiMan = parent._guiMan
        self._parent = parent
        self._clippingRect = self._mixSizePosition(parent)
        self._pinning = []
        self.pinning = pinning
        if not rotation:
            rotation = [0, 0, 0]

        self._is2D = True

        self._top = top
        self._left = left
        self._width = width
        self._height = height
        self.__offset = vec3(0.5, 0.5, 0)
        self._checkStyleType(style)
        self._style = style

        position = vec3(left, top, 0)

        if ID is None:
            ID = str(id(self))

        self._guiMan._addControl(ID)
        Base3DObject.__init__(self, position, rotation, 1, 1, ID=ID, parent=parent)
        ResponsiveControl.__init__(self)

        self._material = Material2D()
        material = self._material
        material._shaderID = DEFAULT2DSHADERID

        # if not all((width, height)):
        #     raise ValueError('size of 0 not allowed: ' + str((width, height)))

        self._innerSize = vec3(1)
        material.shaderProperties.append(Vec3ShaderProperty('relativePosition', self._position))
        material.shaderProperties.append(Vec3ShaderProperty('pixelSize', self._scale))
        material.shaderProperties.append(Vec3ShaderProperty('internalSize', self._innerSize))
        material.shaderProperties.append(Vec4ShaderProperty('parentSizePosition', vec4(0)))
        material.shaderProperties.append(Vec4ShaderProperty('clippingRect', vec4(0)))
        material.shaderProperties.append(Vec3ShaderProperty('windowPosition', self.windowPosition))
        
        self._borderSize = style.borderSize
        size = vec3(width, height, 1)
        self._previousSize = self._scale
        self.size = size
        self._borderColor = style.borderColor
        self._gradientType = style.gradientType
        self._gradientColor0 = style.raisedGradientColor0
        self._gradientColor1 = style.raisedGradientColor1
        self._setInnerSize()

        material.shaderProperties.append(IntShaderProperty('borderSize', self._borderSize))
        material.shaderProperties.append(Vec4ShaderProperty('borderColor', self._borderColor))
        self.borderSize = style.borderSize
        self.borderColor = style.borderColor
        if color is not None:
            material.diffuseColor = color

        if imgID is not None:
            self.backgroundImageID = imgID

        self._set2d()

        material.shaderProperties.append(IntShaderProperty('GradientType', self._gradientType))
        material.shaderProperties.append(Vec4ShaderProperty('GradientColor0', self._gradientColor0))
        material.shaderProperties.append(Vec4ShaderProperty('GradientColor1', self._gradientColor1))

        self._updateSizeProperties()

    def _reStyle(self):
        style = self.style
        self.borderSize = style.borderSize
        self.borderColor = style.borderColor
        self.gradientType = style.gradientType

    def _updateLastPositions(self):
        pw, ph, _ = self.parent.size
        left = self.position.x
        top = self.position.y
        self._right = pw - (left + self._width)
        self._bottom = ph - (top + self._height)
        self._left = left
        self._top = top
        self._lastDifferences = left, top, self._bottom, self._right
        self._updateSizeProperties()
        # self._buildClippingRect()

    @property
    def _offset(self):
        return self.__offset

    def _fillLastDifferences(self):
        self._lastDifferences = (self._left, self._top, self._bottom, self._right)

    @property
    def gradientType(self):
        return self._gradientType

    @gradientType.setter
    def gradientType(self, value):
        self._gradientType = value
        self._material.shaderProperties['GradientType'] = value

    @property
    def gradientColor0(self):
        return self._gradientColor0

    @gradientColor0.setter
    def gradientColor0(self, value):
        self._material.shaderProperties['GradientColor0'] = value
        self._gradientColor0 = value

    @property
    def gradientColor1(self):
        return self._gradientColor1

    @gradientColor1.setter
    def gradientColor1(self, value):
        self._material.shaderProperties['GradientColor1'] = value
        self._gradientColor1 = value

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
        material.useDiffuseTexture = value is not None

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
        self._buildClippingRect()
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

    @property
    def size(self):
        return self._scale

    @size.setter
    def size(self, value):
        """
        Size of control in pixels.
        :param value:
        :type value: vec3
        """
        if not isinstance(value, vec3):
            raise TypeError('size must be a vec3, not \'{}\''.format(type(value)))

        self._previousSize = vec3(self._scale)
        self._scale = value
        self._dirty = True
        self._width, self._height, d = value
        self._updateLastPositions()
        try:
            self._material.shaderProperties['pixelSize'] = value
        except KeyError:
            pass

    def getSize(self):
        return self._scale

    def _getAbsolutePosition(self):
        return self._position

    def _setAbsolutePosition(self, value):
        self._dirty = True
        x, y, z = value
        self._position = vec3(x, y, self._position.z)
        self._updateLastPositions()
        self._material.shaderProperties['relativePosition'] = self._position

    position = property(fget=_getAbsolutePosition, fset=_setAbsolutePosition)

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
        
    @property
    def windowPosition(self):
        return self.parent.windowPosition + self.position

    def _updateTransformation(self):
        self._updateRotationMatrix()
        parent = self._parent
        parentCenter = (parent.size / 2.0)
        parentCenter.z = 0
        position = vec3(self._position)
        rotation = self._rotationMatrix

        scaledOffset = ewMul(self._offset, self._scale)
        position += scaledOffset
        # parentCenter -= scaledOffset
        parentTrans = mat4.translation(parent.windowPosition)
        pCTrans = mat4.translation(parentCenter)
        self._positionMatrix = mat4.translation(position)
        self._scaleMatrix = mat4.scaling(self._scale)
        self._transformation = parentTrans * pCTrans * parent._rotationMatrix * pCTrans.inversed() * \
                               self._positionMatrix * rotation * self._scaleMatrix

    def _updateSizeProperties(self):
        material = self._material
        material.shaderProperties['pixelSize'] = self._scale
        material.shaderProperties['internalSize'] = self._innerSize
        material.shaderProperties['relativePosition'] = self._position
        material.shaderProperties['windowPosition'] = self.windowPosition
        self._buildClippingRect()
        self.updateParentProperties()

    def _update(self):
        res = super(BaseControl, self)._update()
        if res:
            self._buildClippingRect()
            self._updateSizeProperties()
            for child in self._children:
                child.updateParentProperties()
        return res

    def updateParentProperties(self):
        material = self._material
        parent = self.parent
        material.shaderProperties['parentSizePosition'] = self._mixSizePosition(parent)
        material.shaderProperties['clippingRect'] = self._clippingRect

    @staticmethod
    def _mixSizePosition(parentObject):
        border = parentObject.borderSize
        offset = vec3(border, border, 0)
        w, h, d = parentObject.size - (offset * 2)
        t, l, z = parentObject.windowPosition + offset
        return vec4(w, h, t, l)

    def _setInnerSize(self):
        self._innerSize = self.size - vec3(self._borderSize * 2)
        self._innerSize.z = 1

    @property
    def vTextAlign(self):
        return self._vTextAlignGet()

    def _vTextAlignGet(self):
        return self._vTextAlign

    @vTextAlign.setter
    def vTextAlign(self, value):
        BaseControl._checkAlignArgs(value)
        self._vTextAlignSet(value)

    def _vTextAlignSet(self, value):
        self._vTextAlign = value

    @property
    def hTextAlign(self):
        return self._hTextAlignGet()

    def _hTextAlignGet(self):
        return self._hTextAlign

    @hTextAlign.setter
    def hTextAlign(self, value):
        BaseControl._checkAlignArgs(value)
        self._hTextAlignSet(value)

    def _hTextAlignSet(self, value):
        self._hTextAlign = value

    def _setPinning(self):
        pinning = self._pinning
        if PinningEnum.NoPinning in pinning:
            return
        else:
            l, t, b, r = self._lastDifferences
            parent = self.parent
            w, h, _ = parent.size
            ow, oh, _ = parent._previousSize
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
        self._fillLastDifferences()
        self._previousSize = vec3(self._scale)
        self._scale = vec3(max(w - nl - nr, 0), max(h - nt - nb, 0), 1)
        self._position = vec3(nl, nt, 0)
        self._setInnerSize()
        self._dirty = True

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

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, value):
        l, t, z = self._position
        self.position = vec3(value, t, z)

    @property
    def top(self):
        return self._top

    @top.setter
    def top(self, value):
        l, t, z = self._position
        self.position = vec3(l, value, z)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        w, h, d = self.size
        self.size = vec3(value, h, d)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        w, h, d = self.size
        self.size = vec3(w, value, d)

    def isOutBounds(self):
        parent = self.parent
        size = self.size
        pos = self.windowPosition
        posX = pos.x
        posY = pos.y
        borderX = posX + size.x
        borderY = posY + size.y
        while parent is not None:
            parentSize = parent.size
            parentPosition = parent.windowPosition
            parentBorderX = parentPosition.x + parentSize.x
            parentBorderY = parentPosition.y + parentSize.y

            res = posX >= parentBorderX or posY >= parentBorderY or \
                  borderX <= parentPosition.x or borderY <= parentPosition.y
            if res:
                return True
            parent = parent.parent
        return False

    def _buildClippingRect(self):
        parent = self.parent
        size = self.size
        pos = self.windowPosition
        left = pos.x
        top = pos.y
        right = left + size.x
        bottom = top + size.y
        rect = ClippingRect(self._guiMan._window.size)
        while parent is not None:
            border = parent.borderSize
            parentSize = parent.size
            parentPosition = parent.windowPosition
            parentLeft = parentPosition.x
            parentRight = parentLeft + parentSize.x
            parentTop = parentPosition.y
            parentBottom = parentTop + parentSize.y

            if right >= parentRight:
                rect.right = parentRight - border
            if bottom >= parentBottom:
                rect.bottom = parentBottom - border
            if left <= parentLeft:
                rect.left = parentLeft + border
            if top <= parentTop:
                rect.top = parentTop + border
            if rect.isFull():
                break
            parent = parent.parent
        self._clippingRect = rect.toVec4()

    @staticmethod
    def _getVAlignPosition(objectSize, parentSize, parentBorderSize, align):
        left, top, _ = BaseControl.getAlignedPosition(objectSize, parentSize, parentBorderSize, align)
        return left

    @staticmethod
    def _getHAlignPosition(objectSize, parentSize, parentBorderSize, align):
        left, top, _ = BaseControl.getAlignedPosition(objectSize, parentSize, parentBorderSize, align)
        return top

    @staticmethod
    def _checkAlignArgs(align):
        Align2DEnumDir = [val for val in dir(Align2DEnum) if not val.startswith('_')]
        if align not in Align2DEnumDir:
            raise TypeError('align must be in Align2DEnum')

    @staticmethod
    def getAlignedPosition(objectSize, parentSize, parentBorderSize, vAlign=Align2DEnum.Center, hAlign=Align2DEnum.Center):
        def distribute(oV, pV, border):
            return pushOpposite(oV, pV, border) / 2.0

        def pushOpposite(oV, pV, border):
            return pV - oV - border

        BaseControl._checkAlignArgs(vAlign)
        BaseControl._checkAlignArgs(hAlign)

        if vAlign == Align2DEnum.Left:
            left = parentBorderSize
        elif vAlign == Align2DEnum.Right:
            left = pushOpposite(objectSize.x, parentSize.x, parentBorderSize)
        elif vAlign == Align2DEnum.Center:
            left = distribute(objectSize.x, parentSize.x, parentBorderSize)
        else:
            raise ValueError('\'{}\' vAlign value not suitable'.format(vAlign))

        if hAlign == Align2DEnum.Top:
            top = parentBorderSize
        elif hAlign == Align2DEnum.Bottom:
            top = pushOpposite(objectSize.y, parentSize.y, parentBorderSize)
        elif hAlign == Align2DEnum.Center:
            top = distribute(objectSize.y, parentSize.y, parentBorderSize)
        else:
            raise ValueError('\'{}\' hAlign value not suitable'.format(hAlign))

        return vec3(left, top, 1)

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        """

        :rtype: Style
        """
        self._checkStyleType(value)
        self._style = value
        self._reStyle()

    @staticmethod
    def _checkStyleType(value):
        from .Styling import DefaultStyle
        if not isinstance(value, DefaultStyle) and not issubclass(value, DefaultStyle):
            raise TypeError('style must be of type \'DefaultStyle\' or inherith from it.\n'
                            'It is of type \'{}\''.format(type(value)))


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
