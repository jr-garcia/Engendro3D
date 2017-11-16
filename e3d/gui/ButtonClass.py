from .LabelClass import *
from .TextEnums import FontWeightEnum
from .BaseControlClass import StyleHintsEnum
from ..Colors import *
from .Styling import *


class Button(BaseControl):
    """
        Clickable button

       @rtype : Button
    """

    def __init__(self, left, top, width, height, text, parent, pinning=PinningEnum.TopLeft, color=None, fontID='default',
                 styleHint=StyleHintsEnum.Raised, ID=None, rotation=None, style=None):
        """
        :param borderSize:
        :type borderSize:

        """
        style = style or RaisedStyle(color)
        if color is None:
            color = style.backgroundColor
        if styleHint == StyleHintsEnum.Image:
            image = bgImgID
        else:
            image = None

        super(Button, self).__init__(left, top, width, height, parent, pinning, color, ID,
                                     image, rotation, style)

        if styleHint in (StyleHintsEnum.Raised, StyleHintsEnum.Sunken):
            self.gradientType = GradientTypesEnum.Horizontal
        else:
            self.gradientType = GradientTypesEnum.noGradient

        self.borderColor = style.borderColor

        borderSize = style.borderSize
        self._label = Label(borderSize, borderSize, width - (borderSize * 2), text, self,
                            pinning=PinningEnum.TopLeftRight, fontID=fontID, ID=self.ID + '_label',
                            outlineLength=OutlineLenghtEnum.NoOutline)
        label = self._label
        label.outlineColor = style.fontColor
        label.borderSize = 0
        label.color = vec4(0)
        self._hTextAlign = Align2DEnum.HCenter
        x, y, z = self.getAlignedPosition(label.size, self.size, self.borderSize, hAlign=self._hTextAlign)
        label.top = y

        self._styleHint = styleHint
        self._buildColors()

    @property
    def styleHint(self):
        return self._styleHint

    @styleHint.setter
    def styleHint(self, value):
        self._styleHint = value
        self._buildColors()

    @property
    def color(self):
        return super(Button, self)._getColor()

    @color.setter
    def color(self, val):
        super(Button, self)._setColor(val)
        self._buildColors()

    def _buildColors(self):
        styleHint = self.styleHint
        if styleHint in (StyleHintsEnum.Raised, StyleHintsEnum.Sunken):
            style = self.style
            if styleHint == StyleHintsEnum.Raised:
                self.gradientColor0 = style.raisedGradientColor0
                self.gradientColor1 = style.raisedGradientColor1
            else:
                self.gradientColor0 = style.sunkenGradientColor0
                self.gradientColor1 = style.sunkenGradientColor1

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
        if self.gradientType == GradientTypesEnum.noGradient:
            return
        style = self.style
        if isOverMe:
            self.gradientColor0 = style.hoverGradientColor0
            self.gradientColor1 = style.hoverGradientColor1
        else:
            self.gradientColor0 = style.raisedGradientColor0
            self.gradientColor1 = style.raisedGradientColor1

    def _colorizeUpDown(self, isDown):
        if self.gradientType == GradientTypesEnum.noGradient:
            return
        style = self.style
        if isDown:
            self.gradientColor0 = style.pressedGradientColor0
            self.gradientColor1 = style.pressedGradientColor1
        else:
            self.gradientColor0 = style.raisedGradientColor0
            self.gradientColor1 = style.raisedGradientColor1

    def _handleMouseEnter(self, event):
        self._colorizeHover(True)

    def _handleMouseLeave(self, event):
        self._colorizeHover(False)

    def _handleMouseButtonDown(self, event):
        self.gradientColor0 = self.style.pressedGradientColor0
        self.gradientColor1 = self.style.pressedGradientColor1

    def _handleMouseButtonUp(self, event):
        if self.parent._findForegroundControl(event.x, event.y) == self:
            self._colorizeHover(True)
        else:
            self._colorizeHover(False)

    def _reStyle(self):
        super(Button, self)._reStyle()
        self._buildColors()
