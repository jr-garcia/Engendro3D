from .BaseControlClass import *
from .Styling import DefaultStyle


class Panel(BaseControl):
    """
        Flat container for Gui objects.

       @rtype : Panel
    """

    def __init__(self, left, top, width, height, parent, pinning=PinningEnum.TopLeft, color=None, ID=None,
                 imgID=None, rotation=None, style=None):
        style = style or DefaultStyle(color)
        if color is None:
            color = style.backgroundColor
        super(Panel, self).__init__(left, top, width, height, parent, pinning, color, ID, imgID, rotation,
                                    style)
        self._passEventDown = True
