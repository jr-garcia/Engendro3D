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
        self.backgroundColor = vec4(baseColor)
        self.fontColor = WHITE
        self.fontOutlineColor = BLUE
        self.fontSize = 10
        self.borderSize = 1
        self.borderColor = fromRGB1_A(baseColor / 4.0, 1)
        self.focusBorderColor = ORANGE
        self.hoverBorderColor = GREEN
        self.gradientType = GradientTypesEnum.noGradient
        self.raisedGradientColor0 = WHITE
        self.raisedGradientColor1 = BLACK
        self.sunkenGradientColor0 = BLACK
        self.sunkenGradientColor1 = WHITE
        self.pressedGradientColor0 = BLACK
        self.pressedGradientColor1 = WHITE
        self.hoverGradientColor0 = WHITE
        self.hoverGradientColor1 = BLACK
        self.autoRaiseGradientColor0 = WHITE
        self.autoRaiseGradientColor1 = BLACK
        self.hoverColor = fromRGB1_A((baseColor + (WHITE / 10.0)), 1)
        self.pressedColor = fromRGB1_A(baseColor / 1.5, 1)
        self.buttonStyleHint = StyleHintsEnum.Raised
        self.controlStyleHint = StyleHintsEnum.Raised

        self._buildradients(baseColor)

    def _buildradients(self, baseColor):
        color0 = (baseColor + WHITE / 2.0) / 2.0
        color0.w = 1
        color1 = baseColor / 4.0
        color1.w = 1
        color2 = (baseColor + WHITE / 3.0) / 2.0
        color2.w = 1
        color3 = baseColor / 6.0
        color3.w = 1
        color4 = (baseColor + WHITE / 4.0) / 2.0
        color4.w = 1
        color5 = baseColor / 8.0
        color5.w = 1
        color6 = (baseColor + WHITE / 1.8) / 2.0
        color6.w = 1
        color7 = baseColor / 1.4
        color7.w = 1

        self.raisedGradientColor0 = color2
        self.raisedGradientColor1 = color3
        self.sunkenGradientColor0 = color3
        self.sunkenGradientColor1 = color2
        self.pressedGradientColor0 = color4
        self.pressedGradientColor1 = color5
        self.hoverGradientColor0 = color0
        self.hoverGradientColor1 = color1
        self.autoRaiseGradientColor0 = color6
        self.autoRaiseGradientColor1 = color7

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
