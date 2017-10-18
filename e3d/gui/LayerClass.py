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
        super(Layer, self).__init__(None)
        self.ID = ID
        self.visible = visible
        self._pixelSize = vec3(1)
        self._realScale = vec3(1)
        self._inverseScale = vec3(1)
        self._guiMan = guiMan
        self._previousSize = self.pixelSize
        self._onInit = True

        self._rotationMatrix = mat4(1)
        self._position = vec3(0)

        self._updatePixelSize()

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

    def _updatePixelSize(self):
        self._previousSize = self._pixelSize
        x, y = self._guiMan._window.size
        baseSize = vec3(x, y, 1)
        self._pixelSize = baseSize
        self._scale = self.realScale
        if self._onInit:
            self._previousSize = self._pixelSize
            self._onInit = False

    def getPixelSize(self):
        return self._pixelSize

    pixelSize = property(getPixelSize)

    @property
    def size(self):
        return self._pixelSize

    def _getRealScale(self):
        return self._realScale

    realScale = property(_getRealScale)

    def _getInverseScale(self):
        return self._inverseScale

    inverseScale = property(_getInverseScale, doc='Scale needed to pass from local to window scale.')

    def _resizeCallback(self):
        self._updatePixelSize()
        for c in reversed(self._children):
            c._resizeCallback()

    @property
    def _offset(self):
        return vec3(0)
