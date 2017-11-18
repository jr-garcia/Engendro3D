from ...Colors import *
from ..BaseControlClass import GradientTypesEnum

from json import dump, load


class StyleHintsEnum(object):
    Flat = 'Flat'
    Raised = 'Raised'
    Sunken = 'Sunken'
    Hover = 'Hover'
    Image = 'Image'
    # Custom = 'Custom'


class DefaultStyle(object):
    def __init__(self, baseColor=None):
        if baseColor is None:
            baseColor = RGBA255(28, 30, 33, 255)
        self.name = 'Default'
        self.backgroundColor = baseColor
        self.fontColor = WHITE
        self.fontOutlineColor = BLUE
        self.fontSize = 10
        self.backgroundColor = baseColor
        self.borderColor = (BLACK + baseColor) / 2.0
        self.borderSize = 2
        self.gradientType = GradientTypesEnum.noGradient
        self.raisedGradientColor0 = WHITE
        self.raisedGradientColor1 = BLACK
        self.sunkenGradientColor0 = BLACK
        self.sunkenGradientColor1 = WHITE
        self.pressedGradientColor0 = BLACK
        self.pressedGradientColor1 = WHITE
        self.hoverGradientColor0 = WHITE
        self.hoverGradientColor1 = BLACK
        self.focusColor = ORANGE
        self.hoverColor = baseColor * 2.0
        self.pressedColor = baseColor / 2.5
        self.buttonStyleHint = StyleHintsEnum.Raised
        self.controlStyleHint = StyleHintsEnum.Raised

        self._buildradients(baseColor)

    def _buildradients(self, baseColor):
        color0 = baseColor * 2.0
        color1 = baseColor / 2.0
        color1.w = 1
        color2 = baseColor * 1.5
        color3 = baseColor / 2.5
        color3.w = 1
        color4 = baseColor * 2.5
        color5 = baseColor / 1.5
        color5.w = 1

        self.raisedGradientColor0 = color0
        self.raisedGradientColor1 = color1
        self.sunkenGradientColor0 = color1
        self.sunkenGradientColor1 = color0
        self.pressedGradientColor0 = color2
        self.pressedGradientColor1 = color3
        self.hoverGradientColor0 = color4
        self.hoverGradientColor1 = color5

    def __repr__(self):
        return str(self.name)

    def saveToFile(self, path):
        vals = {}
        with open(path, 'w') as file:
            attribs = dir(self)
            for att in attribs:
                if not att.startswith('_'):
                    vals[att] = getattr(self, att)
            dump(vals, file, indent=4)

    @staticmethod
    def readFromFile(path):
        style = DefaultStyle()
        with open(path) as file:
            vals = load(file)
            for att in vals.keys:
                setattr(style, att, vals[att])

        return style
