from .BaseControlClass import *


class Panel(BaseControl):
    """
        Flat container for Gui objects.

       @rtype : Panel
    """

    def __init__(self, left, top, width, height, parent, pinning=PinningEnum.TopLeft, color=vec4(1), ID=None,
                 imgID=None, rotation=None, borderSize=1, gradientType=GradientTypesEnum.noGradient):
        super(Panel, self).__init__(left, top, width, height, parent, pinning, color, ID, imgID, rotation,
                                    borderSize, gradientType)
        self._passEventDown = True
