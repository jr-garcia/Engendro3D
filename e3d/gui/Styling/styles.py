from .StyleClass import DefaultStyle, GradientTypesEnum

from cycgkit.cgtypes import vec4


class RaisedStyle(DefaultStyle):
    def __init__(self, baseColor):
        super(RaisedStyle, self).__init__(baseColor)
        self.name = 'Raised'
        self.gradientType = GradientTypesEnum.Horizontal
