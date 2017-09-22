from .BaseControlClass import *


class Panel(BaseControl):
    """
        Flat container for Gui objects.

       @rtype : Panel
    """

    def __init__(self, position, width, height, parent, color=None, imgID=None, rotation=None, borderSize=1,
                 gradientType=GradientTypesEnum.noGradient):
        super(Panel, self).__init__(position, width, height, parent, color, imgID, rotation, borderSize, gradientType)
