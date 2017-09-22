from .BaseControlClass import *


class Panel(BaseControl):
    """
        Flat container for Gui objects.

       @rtype : Panel
    """

    def __init__(self, position, width, height, parent, color=None, imgID=None, rotation=None, borderSize=0.0):
        super(Panel, self).__init__(position, width, height, parent, color, imgID, rotation)
