from .LabelClass import *
from .TextEnums import FontWeightEnum
from ..Colors import *
from .Styling import *


class Button(BaseControl):
    """
        Clickable button

       @rtype : Button
    """

    def __init__(self, left, top, width, height, text, parent, pinning=PinningEnum.TopLeft, color=None,
                 fontID='default', ID=None, rotation=None, style=None, imageIDs=None):
        """
        :param borderSize:
        :type borderSize:

        """
        if imageIDs is None:
            imageIDs = [None] * 3
        if len(imageIDs) != 3:
            raise RuntimeError('imageIDs must have 3 elements, None or String ([Normal, Hover, Down])')
        self._buttonImageIDs = imageIDs
        style = style or DefaultStyle(color)
        styleHint = style.buttonStyleHint
        if color is None:
            color = style.backgroundColor

        super(Button, self).__init__(left, top, width, height, parent, pinning, color, ID,
                                     None, rotation, style)

        if styleHint in (StyleHintsEnum.Raised, StyleHintsEnum.Sunken):
            self.gradientType = GradientTypesEnum.Horizontal
        else:
            self.gradientType = GradientTypesEnum.noGradient

        if styleHint == StyleHintsEnum.Image:
            self.backgroundImageID = imageIDs[0]

        self.borderColor = style.borderColor
        borderSize = style.borderSize
        self._lastBorderSize = borderSize
        self._label = Label(borderSize, borderSize, width - (borderSize * 2), text, self,
                            pinning=PinningEnum.TopLeftRight, fontID=fontID, ID=self.ID + '_label',
                            outlineLength=OutlineLenghtEnum.NoOutline)
        label = self._label
        label.outlineColor = style.fontColor
        label.borderSize = 0
        label.color = vec4(0)
        x, y, z = self.getAlignedPosition(label.size, self.size, self.borderSize, hAlign=self._hTextAlign)
        label.top = y
        label.vTextAlign = Align2DEnum.Center

        self._styleHint = styleHint
        self._buildColors()
        
    @property
    def normalImageID(self):
        return self._buttonImageIDs[0]
    
    @normalImageID.setter
    def normalImageID(self, value):
        self._buttonImageIDs[0] = value
        self.backgroundImageID = value

    @property
    def hoverImageID(self):
        return self._buttonImageIDs[1]

    @hoverImageID.setter
    def hoverImageID(self, value):
        self._buttonImageIDs[1] = value

    @property
    def downImageID(self):
        return self._buttonImageIDs[2]

    @downImageID.setter
    def downImageID(self, value):
        self._buttonImageIDs[2] = value

    def _hTextAlignGet(self):
        return self._label.hTextAlign

    def _vTextAlignGet(self):
        return self._label.vTextAlign

    def _hTextAlignSet(self, value):
        self._label.hTextAlign = value

    def _vTextAlignSet(self, value):
        self._label.vTextAlign = value

    @property
    def styleHint(self):
        return self._styleHint

    @styleHint.setter
    def styleHint(self, value):
        self._styleHint = value
        self._lastBorderSize = self.style.borderSize
        if value in (StyleHintsEnum.Raised, StyleHintsEnum.Sunken):
            self.gradientType = GradientTypesEnum.Horizontal
        else:
            self.gradientType = GradientTypesEnum.noGradient
        self._material.useDiffuseTexture = value == StyleHintsEnum.Image
        if value == StyleHintsEnum.Image:
            normalImageID = self._buttonImageIDs[0]
            self.backgroundImageID = normalImageID
        self._buildColors()

    @property
    def color(self):
        return super(Button, self)._getColor()

    @color.setter
    def color(self, val):
        super(Button, self)._setColor(val)
        self._buildColors()

    def _buildColors(self):
        self.borderColor = self.style.borderColor
        self._colorizeHover(False)

    def _getText(self):
        return self._label.text

    def _setText(self, val):
        self._label.text = val

    text = property(_getText, _setText)

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

    def _colorizeHover(self, isOverMe):
        style = self.style
        hint = self.styleHint
        if isOverMe:
            if hint == StyleHintsEnum.Hover:
                if self._lastBorderSize == 0:
                    super(Button, self)._setBorder(style.borderSize)
                else:
                    super(Button, self)._setBorder(self._lastBorderSize)
                self.gradientType = GradientTypesEnum.Horizontal
                self.gradientColor0 = style.autoRaiseGradientColor0
                self.gradientColor1 = style.autoRaiseGradientColor1
            else:
                if hint == StyleHintsEnum.Image:
                    self.backgroundImageID = self.hoverImageID
                if self.gradientType == GradientTypesEnum.noGradient:
                    super(Button, self)._setColor(style.hoverColor)
                else:
                    self.gradientColor0 = style.hoverGradientColor0
                    self.gradientColor1 = style.hoverGradientColor1
        else:
            if hint == StyleHintsEnum.Hover:
                self.borderSize = self._lastBorderSize
                self.gradientType = GradientTypesEnum.noGradient
            elif hint == StyleHintsEnum.Image:
                self.backgroundImageID = self.normalImageID
            if self.gradientType == GradientTypesEnum.noGradient:
                super(Button, self)._setColor(style.backgroundColor)
            else:
                self.gradientColor0 = style.raisedGradientColor0
                self.gradientColor1 = style.raisedGradientColor1

    def _handleMouseEnter(self, event):
        self._lastBorderSize = self._borderSize
        self._colorizeHover(True)

    def _handleMouseLeave(self, event):
        self._colorizeHover(False)

    def _handleMouseButtonDown(self, event):
        style = self.style
        hint = self.styleHint
        if hint == StyleHintsEnum.Hover:
            if self._lastBorderSize == 0:
                super(Button, self)._setBorder(style.borderSize)
            else:
                super(Button, self)._setBorder(self._lastBorderSize)
        elif hint == StyleHintsEnum.Image:
            self.backgroundImageID = self.downImageID
        if self.gradientType == GradientTypesEnum.noGradient:
            super(Button, self)._setColor(style.pressedColor)
        else:
            self.gradientColor0 = style.pressedGradientColor0
            self.gradientColor1 = style.pressedGradientColor1

    def _handleMouseButtonUp(self, event):
        if self.parent._findForegroundControl(event.x, event.y) == self:
            self._colorizeHover(True)
        else:
            self._colorizeHover(False)

    def _reStyle(self):
        super(Button, self)._reStyle()
        self._lastBorderSize = self.style.borderSize
        self._buildColors()

    @property
    def borderSize(self):
        return super(Button, self).borderSize

    @borderSize.setter
    def borderSize(self, value):
        super(Button, self)._setBorder(value)
        self._lastBorderSize = value
