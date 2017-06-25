from .BaseControlClass import *


class Panel(BaseControl):
    """
        Flat container for Gui objects.

       @rtype : Panel
    """

    def __init__(self, position, size, parent, color=None, imgID=None, rotation=None, borderSize=0.0):
        super(Panel, self).__init__(position, size, parent, color, imgID, rotation)
