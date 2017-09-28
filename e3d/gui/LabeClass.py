from .BaseControlClass import BaseControl
from .SingleCharClass import *
from .FontRendering.MSDFAtlasRenderer import AtlasInfo, CharData

DEFAULTSPACING = 10

CHAR_SEPARATION = .05


class Label(BaseControl):
    """
        Text container.

       @rtype : Label
    """

    def __init__(self, left, top, width, height, text, parent, pinning=PinningEnum.TopLeft, fontID='default', fontBorder=.0, fontBorderColor=vec4(0, 0, 0, 1),
                 fontColor=vec4(1, 1, 1, 1), fontWeight=.5, color=None, ID=None, imgID=None, rotation=None,
                 borderSize=1, gradientType=GradientTypesEnum.noGradient):
        """
        :param borderSize:
        :type borderSize:

        """
        self._chars = []
        self._text = text
        self._fontWeight = fontWeight
        self._fontColor = fontColor
        self._fontBorderColor = fontBorderColor
        self._fontBorder = fontBorder
        self._fontID = fontID
        super(Label, self).__init__(left, top, width, height, parent, pinning, color, ID, imgID, rotation, borderSize,
                                    gradientType)
        self._isBuilt = False
        self._dirtyProperties = True

        self._updateRealSizePosition()
        self._updateText()

    def _getText(self):
        return self._text

    def _setText(self, val):
        self._text = val
        self._isBuilt = False

    text = property(_getText, _setText)

    def _updateText(self):
        self._isBuilt = True
        self._dirtyProperties = False
        try:
            self._children.clear()
        except AttributeError:
            self._children = []
        for c in self._text:
            newChar = SingleChar(0, 0, 1, 1, c, self, PinningEnum.TopLeft, self._fontID, self._fontBorder,
                                 self._fontBorderColor, self._fontColor, self._fontWeight)
            self._chars.append(newChar)
        self._setCharsRatio()

    def _setCharsRatio(self):
        self._dirty = True
        if len(self._chars) == 0:
            return
        advanceX = 0
        internalSpacing = self._scale - (ewDiv(self._scale, self._realSize) * (2 * 2))
        internalSpacing.z = 1
        ratioScaleH = self._realSize[1] / self._realSize[0]
        correctedScale = ratioScaleH * self._inverseScale[0]
        guiMan = self._guiMan
        assert isinstance(guiMan, GuiManager)
        fontInfo = guiMan.fontInfos[self.fontID]
        assert isinstance(fontInfo, AtlasInfo)
        posX = 0
        preoffset = 0
        for c in self._chars:
            c._dirty = True
            assert isinstance(c, SingleChar)
            cdata = fontInfo.charDataDict[c._charCode]
            assert isinstance(cdata, CharData)
            maxSize = max(cdata.height, cdata.width)
            charHeight = maxSize
            charWidth = maxSize
            posX += advanceX - ((charWidth + fontInfo.border - cdata.width) / 2) - preoffset
            preoffset = ((charWidth + fontInfo.border - cdata.width) / 2)
            advanceX = charWidth + CHAR_SEPARATION
            if c.char == ' ':
                posY = 0
            else:
                originY = fontInfo.lineHeight - cdata.above - fontInfo.baseline - fontInfo.border
                posY = originY - ((charHeight - cdata.height) / 2)

            c.size = vec3(charWidth * correctedScale, charHeight, 1)
            c.position = vec3(posX * correctedScale, posY, 0)

            if c._position.x >= 1 or c._position.y >= 1:
                c.visible = False
            else:
                c.visible = True

    def _update(self):
        if not self._isBuilt:
            self._updateText()
        if self._dirtyProperties:
            self._updateProperties()
        super(Label, self)._update()

    def _updateProperties(self):
        for c in self._chars:
            c.fontID = self._fontID
            c.fontBorder = self._fontBorder
            c.fontBorderColor = self._fontBorderColor
            c.fontColor = self._fontColor
            c.fontWeight = self._fontWeight
            c.color = self.color

    def _getFontBorder(self):
        return self._fontBorder

    def _setFontBorder(self, val):
        self._fontBorder = val
        self._dirtyProperties = True

    fontBorder = property(_getFontBorder, _setFontBorder)

    def _getFontBorderColor(self):
        return self._fontBorderColor

    def _setFontBorderColor(self, val):
        self._fontBorderColor = val
        self._dirtyProperties = True

    fontBorderColor = property(_getFontBorderColor, _setFontBorderColor)

    def _getFontColor(self):
        return self._fontColor

    def _setFontColor(self, val):
        self._fontColor = val
        self._dirtyProperties = True

    fontColor = property(_getFontColor, _setFontColor)

    def _getfontWeight(self):
        return self._fontWeight

    def _setfontWeight(self, val):
        self._fontWeight = val
        self._dirtyProperties = True

    fontWeight = property(_getfontWeight, _setfontWeight)

    def _setFont(self, fontID):
        self._fontID = fontID
        self._dirtyProperties = True
        self._isBuilt = False

    def _getFont(self):
        return self._fontID

    fontID = property(_getFont, _setFont)

    def __repr__(self):
        return self._text

    def _updateRealSizePosition(self):
        super(Label, self)._updateRealSizePosition()
        self._setCharsRatio()

    def _setColor(self, value):
        self._dirtyProperties = True
        super(Label, self)._setColor(value)

        # color = property(BaseControl._getColor, _setColor)
