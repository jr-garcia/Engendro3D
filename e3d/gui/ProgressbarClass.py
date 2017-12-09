from .LabelClass import *
from .TextEnums import FontWeightEnum
from ..Colors import *
from .Styling import *
from .PanelClass import Panel
from ..commonValues import scaleNumber


class ProgressBar(BaseControl):
    """
        Simple ProgressBar

       @rtype : ProgressBar
    """

    def __init__(self, left, top, width, height, parent, pinning=PinningEnum.TopLeft, color=None, barColor=None,
                 value=50, ID=None, rotation=None, style=None):
        """
        :param borderSize:
        :type borderSize:

        """
        self._minimum = 0.0
        self._maximum = 100.0
        self._decimals = 0
        self._showPercent = True
        self._buttonImageIDs = [None] * 2
        self._value = value
        style = style or DefaultStyle(color)
        self._barColor = barColor or style.activeColor
        styleHint = style.buttonStyleHint
        if color is None:
            color = style.backgroundColor

        super(ProgressBar, self).__init__(left, top, width, height, parent, pinning, color, ID, None, rotation, style)

        if styleHint in (StyleHintsEnum.Raised, StyleHintsEnum.Sunken):
            self.gradientType = GradientTypesEnum.Horizontal
        else:
            self.gradientType = GradientTypesEnum.noGradient

        self.borderColor = style.borderColor
        borderSize = style.borderSize
        self._label = Label(borderSize, borderSize, width - (borderSize * 2), str(value), self,
                            pinning=PinningEnum.TopLeftRight, ID=self.ID + '_label',
                            outlineLength=OutlineLenghtEnum.NoOutline)
        label = self._label
        label.borderSize = 0
        label.color = vec4(0)
        x, y, z = self.getAlignedPosition(label.size, self.size, self.borderSize, hAlign=self._hTextAlign)
        label.top = y
        label.vTextAlign = Align2DEnum.Center

        self._styleHint = styleHint
        barStyle = style._copy()
        barStyle.baseColor = self._barColor
        self._backgroundSize = 0
        bsize = self._backgroundSize
        dbsize = bsize * 2
        self._pbar = Panel(bsize, bsize, (self.width - dbsize) * (value / 100.0), self.height - dbsize, self,
                           PinningEnum.all, self._barColor, self.ID + '_bar', style=barStyle)
        self._pbar.gradientType = self.gradientType
        self._pbar.borderSize = 0
        self._PbarImage = Panel(bsize, bsize, (self.width - dbsize), self.height - dbsize, self._pbar, PinningEnum.all,
                                TRANSPARENT, self.ID + '_barImage', style=barStyle)
        self._PbarImage.borderSize = 0
        self._buildColors()
        if styleHint == StyleHintsEnum.Image:
            self.backgroundImageID = ''
            self._PbarImage.backgroundImageID = ''
            self._PbarImage.visible = True
        else:
            self._PbarImage.visible = False

        self._buildValues()

    @property
    def backgroundSize(self):
        return self._backgroundSize

    @backgroundSize.setter
    def backgroundSize(self, value):
        self._backgroundSize = value
        self._placeBar()

    @property
    def progressImageID(self):
        return self._PbarImage.backgroundImageID

    @progressImageID.setter
    def progressImageID(self, value):
        self._PbarImage.backgroundImageID = value
        if value is not None:
            self._pbar.color = TRANSPARENT
            self._PbarImage.visible = True
        else:
            self._pbar.color = self.barColor
            self._PbarImage.visible = False

    def _hTextAlignGet(self):
        return self._label.hTextAlign

    def _hTextAlignSet(self, value):
        self._label.hTextAlign = value

    @property
    def styleHint(self):
        return self._styleHint

    @styleHint.setter
    def styleHint(self, value):
        self._styleHint = value
        self.style.buttonStyleHint = value
        if value in (StyleHintsEnum.Raised, StyleHintsEnum.Sunken):
            self.gradientType = GradientTypesEnum.Horizontal
        else:
            self.gradientType = GradientTypesEnum.noGradient
        self._material.useDiffuseTexture = value == StyleHintsEnum.Image
        if value == StyleHintsEnum.Image:
            normalImageID = self._buttonImageIDs[0]
            self.backgroundImageID = normalImageID
        self._pbar.gradientType = self.gradientType
        self._buildColors()

    @property
    def color(self):
        return super(ProgressBar, self)._getColor()

    @color.setter
    def color(self, val):
        super(ProgressBar, self)._setColor(val)
        self.style.baseColor = val
        self._buildColors()

    @property
    def barColor(self):
        return self._pbar.color

    @barColor.setter
    def barColor(self, val):
        self._pbar.color = val
        self._barColor = val
        self._pbar.style.baseColor = val
        self._buildColors()

    def _buildColors(self):
        style = self.style
        barStyle = self._pbar.style
        self.borderColor = style.borderColor
        if self.gradientType != GradientTypesEnum.noGradient:
            if style.buttonStyleHint == StyleHintsEnum.Raised:
                self.gradientColor0 = style.raisedGradientColor0
                self.gradientColor1 = style.raisedGradientColor1
            else:
                self.gradientColor0 = style.sunkenGradientColor0
                self.gradientColor1 = style.sunkenGradientColor1
            if barStyle.controlStyleHint == StyleHintsEnum.Raised:
                self._pbar.gradientColor0 = barStyle.raisedGradientColor0
                self._pbar.gradientColor1 = barStyle.raisedGradientColor1
            else:
                self._pbar.gradientColor0 = barStyle.sunkenGradientColor0
                self._pbar.gradientColor1 = barStyle.sunkenGradientColor1
        else:
            super(ProgressBar, self)._setColor(style.baseColor)
            self._pbar.color = self._barColor

    def _getFontColor(self):
        return self._label.fontColor

    def _setFontColor(self, val):
        label = self._label
        label.fontColor = val
        label.outlineColor = val

    fontColor = property(_getFontColor, _setFontColor)

    def _getfontWeight(self):
        return self._label.fontWeight

    def _setfontWeight(self, val):
        self._label.fontWeight = val

    fontWeight = property(_getfontWeight, _setfontWeight)

    def _setFont(self, fontID):
        self._label.fontID = fontID

    def _getFont(self):
        return self._label.fontID

    fontID = property(_getFont, _setFont)

    def _reStyle(self):
        super(ProgressBar, self)._reStyle()
        barStyle = self.style._copy()
        self._pbar.style = barStyle
        self._pbar.borderSize = 0
        self._buildColors()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._dirty = True
        self._value = val
        self._buildValues()

    def _getPercentage(self):
        maximum = self.maximum
        minimum = self.minimum
        value = self._clampValue()
        value = scaleNumber(value, (minimum, maximum), (0, 100))
        return value

    def _clampValue(self):
        maximum = self.maximum
        minimum = self.minimum
        value = min(max(self._value, minimum), maximum)
        return value

    def _buildValues(self):
        showPercent = self.showPercent
        if showPercent:
            value = self._getPercentage()
        else:
            value = self._clampValue()
        decimals = self._decimals
        if decimals <= 0:
            labelVal = int(value)
        else:
            labelVal = round(value, decimals)
        self._label.text = str(labelVal) + ('%' if showPercent else '')
        self._placeBar()

    def _placeBar(self):
        bsize = self._backgroundSize
        dbsize = bsize * 2
        pbar = self._pbar
        value = self._getPercentage()
        pbar.width = (self.width - dbsize) * (value / 100.0)
        pbar.height = self.height - dbsize
        pbar.top = bsize
        pbar.left = bsize

    @property
    def decimals(self):
        return self._decimals

    @decimals.setter
    def decimals(self, value):
        self._decimals = value

    @property
    def maximum(self):
        return self._maximum

    @maximum.setter
    def maximum(self, value):
        if value == self.minimum:
            self.minimum = value - 1
        self._maximum = float(value)
        self._buildValues()

    @property
    def minimum(self):
        return self._minimum

    @minimum.setter
    def minimum(self, value):
        if value == self.maximum:
            self.maximum = value + 1
        self._minimum = float(value)
        self._buildValues()
        
    @property
    def showPercent(self):
        return self._showPercent
    
    @showPercent.setter
    def showPercent(self, value):
        self._showPercent = value
