from .SingleCharClass import *
from .Styling import DefaultStyle
from .TextEnums import *

DEFAULTSPACING = 1.0 / 10


class Label(BaseControl):
    """
        Text displayer.

       @rtype : Label
    """

    def __init__(self, left, top, width, text, parent, pinning=PinningEnum.TopLeft, fontSize=10, fontID='default',
                 color=None, ID=None, imgID=None,
                 rotation=None, outlineLength=OutlineLenghtEnum.NoOutline, style=None):

        """
        :param borderSize:
        :type borderSize:

        """
        style = style or DefaultStyle(color)
        if color is None:
            color = style.backgroundColor
        self._outlineLength = outlineLength
        self._fontSize = fontSize
        self._text = text
        self._fontWeight = FontWeightEnum.Normal
        self._fontColor = style.fontColor
        self._outlineColor = style.fontOutlineColor
        self._fontBorder = 0
        self._fontID = fontID
        self._oldOffset = 0
        height = self._presetHeightByFont(parent)

        super(Label, self).__init__(left, top, width, height + (self._spacing * 2), parent, pinning, color, ID,
                                    imgID, rotation, style)

        self.borderSize = 0
        self._isBuilt = False
        self._dirtyProperties = True

        self._updateSizeProperties()
        self._updateChars()

    @property
    def fontSize(self):
        return self._fontSize

    @fontSize.setter
    def fontSize(self, value):
        self._fontSize = value
        self.height = self._presetHeightByFont(self.parent)

    def _presetHeightByFont(self, parent):
        height = parent._guiMan.getFontSizeInPixels(self.fontSize, self.fontID)
        self._fontMaxHeight = height
        self._spacing = DEFAULTSPACING * height
        self._baseline = height - (height / 6.0)
        return height

    def _getText(self):
        return self._text

    def _setText(self, val):
        self._text = val
        self._isBuilt = False

    text = property(_getText, _setText)

    def _updateChars(self):
        self._isBuilt = True
        self._dirtyProperties = False
        try:
            self._children.clear()
        except AttributeError:
            self._children = []
        height = self._height
        left = 0
        for c in self._text:
            newChar = SingleChar(left, 0, height, c, self, PinningEnum.NoPinning, fontID=self._fontID,
                                 color=vec4(0, 0, 0, 0), borderSize=0, style=self.style)
            newChar.outlineLength = self._outlineLength
            newChar.outlineColor = self._outlineColor
            newChar.fontWeight = self._fontWeight
            newChar.fontColor = self._fontColor
            left += height
        self._setCharsRatio()
                                 
    def _setCharsRatio(self):
        self._dirty = True
        if len(self._children) == 0:
            return
        spacing = self._spacing
        advanceX = spacing
        maxHeight = float(self._fontMaxHeight)
        guiMan = self._guiMan
        assert isinstance(guiMan, GuiManager)
        fontInfo = guiMan.fontInfos[self.fontID]
        assert isinstance(fontInfo, AtlasInfo)
        baseline = self._baseline
        gotBroken = False

        for c in self._children:
            c._dirty = True
            assert isinstance(c, SingleChar)
            hasChar = c._charCode in fontInfo.charDataDict
            if not hasChar:
                raise NotImplementedError('char \'{}\' not included in font atlas.'.format(c.char))
            cdata = fontInfo.charDataDict[c._charCode]
            assert isinstance(cdata, CharData)
            if cdata.height > cdata.width:
                boxScale = maxHeight * cdata.height
            else:
                boxScale = cdata.width * maxHeight

            boxWidth = boxScale
            boxHeight = boxScale

            charHeight = cdata.height * maxHeight
            charWidth = cdata.width * maxHeight

            charBottom = (boxHeight - charHeight) / 2.0
            charLeft = (boxWidth - charWidth) / 2.0
            if c.char == ' ':
                posY = 0
            else:
                posY = baseline - (cdata.above * maxHeight) - charBottom

            lowerEdge = posY + boxHeight
            if lowerEdge > maxHeight:
                self._baseline -= lowerEdge - maxHeight
                self._setCharsRatio()
                gotBroken = True
                break

            c.size = vec3(boxWidth, boxHeight, 1)
            c.position = vec3(advanceX - charLeft, posY + spacing, 0)
            # advanceX += (cdata.advance[0] * maxHeight)  # This is the 'right way'
            # advanceX += charWidth  # This is a safe way
            advanceX += ((cdata.advance[0] * maxHeight) + charWidth) / 2.0  # This looks better
            self._totalLength = c.position.x + c.size.x

        if not gotBroken:
            self._alignText()

    def _alignText(self):
        size = vec3(self._totalLength, self.height - (self.borderSize * 2) + (self._spacing * 2), 1)
        x, y, z = self.getAlignedPosition(size, self.size, self.borderSize, self._vTextAlign, self._hTextAlign)
        oldOffset = self._oldOffset
        for c in self._children:
            c.left -= oldOffset
            c.left += x
        self._oldOffset = x

    def _hTextAlignSet(self, value):
        super(Label, self)._hTextAlignSet(value)
        self._dirty = True
        self._alignText()

    def _vTextAlignSet(self, value):
        super(Label, self)._vTextAlignSet(value)
        self._dirty = True
        self._alignText()

    def _update(self):
        if not self._isBuilt:
            self._updateChars()
        if self._dirtyProperties:
            self._updateCharacterProperties()
        super(Label, self)._update()

    def _updateCharacterProperties(self):
        for c in self._children:
            c.fontID = self._fontID
            c.fontBorder = self._fontBorder
            c.outlineColor = self._outlineColor
            c.fontColor = self._fontColor
            c.fontWeight = self._fontWeight

    def _getFontBorder(self):
        return self._fontBorder

    def _setFontBorder(self, val):
        self._fontBorder = val
        self._dirtyProperties = True

    fontBorder = property(_getFontBorder, _setFontBorder)

    @property
    def outlineColor(self):
        return self._outlineColor

    @outlineColor.setter
    def outlineColor(self, value):
        self._outlineColor = value
        self._dirtyProperties = True

    @property
    def outlineLength(self):
        return self._outlineLength

    @outlineLength.setter
    def outlineLength(self, value):
        self._outlineLength = value
        self._dirtyProperties = True

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
        w, h, z = self.size
        height = self._presetHeightByFont(self.parent)
        self.size = vec3(w, height + (self._spacing * 2), z)
        self._dirtyProperties = True
        self._isBuilt = False

    def _getFont(self):
        return self._fontID

    fontID = property(_getFont, _setFont)

    def __repr__(self):
        return self._text

    def _updateSizeProperties(self):
        super(Label, self)._updateSizeProperties()
        # self._setCharsRatio()

    @property
    def color(self):
        return super(Label, self)._getColor()

    @color.setter
    def color(self, value):
        self._dirtyProperties = True
        super(Label, self)._setColor(value)
