from ..Base3DObjectClass import Attachable

from cycgkit.cgtypes import *


class Layer(Attachable):
    """
    Virtual top level container for gui objects.
    Only objects attached to this will be drawn 'above' the scene, in 2D mode.
    """

    def __init__(self, ID, guiMan, visible=True):
        """


            @rtype : Layer
            @type visible: bool
            """
        super(Layer, self).__init__()
        self.ID = ID
        self.visible = visible
        self._realSize = vec3(1)
        self._realScale = vec3(1)
        self._inverseScale = vec3(1)
        self._guiMan = guiMan
        self._updateRealSize()

    def _getis2D(self):
        return True

    _is2D = property(_getis2D)

    def __repr__(self):
        return self.ID

    def attachTo(self, parent):
        raise ValueError('layers can only contain 2D controls. Can not be attached.')

    def _update(self):
        if self.visible:
            for c in reversed(self._children):
                c._update()

    def _updateRealSize(self):
        x, y = self._guiMan._window.size
        baseSize = vec3(x, y, 1)
        self._realSize = baseSize

    def getRealSize(self):
        return self._realSize

    realSize = property(getRealSize)

    def _getRealScale(self):
        return self._realScale

    realScale = property(_getRealScale)

    def _getInverseScale(self):
        return self._inverseScale

    inverseScale = property(_getInverseScale, doc='Scale needed to pass from local to window scale.')

    def _resizeCallback(self):
        self._updateRealSize()
        for c in reversed(self._children):
            c._resizeCallback()
