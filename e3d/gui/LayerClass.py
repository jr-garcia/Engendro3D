from ..Base3DObjectClass import Attachable, ResponsiveObject
from ..events_processing.eventClasses import MouseEventNames, MouseEvent

from cycgkit.cgtypes import *


class ResponsiveControl(ResponsiveObject):
    def __init__(self, watchLastControl=True, passEventDown=False):
        super(ResponsiveControl, self).__init__(passEventDown)
        self._watchLastControl = watchLastControl
        self._watchedControl = None
        self._lastControlOver = None

    def _handleMouseEvent(self, event):
        super(ResponsiveControl, self)._handleMouseEvent(event)
        if not self._passEventDown:
            return
        eventX = event.x
        eventY = event.y

        activeControl = self._findForegroundControl(eventX, eventY)

        if event.eventName == MouseEventNames.buttonDown:
            if self._watchLastControl:
                self._watchedControl = activeControl
        elif event.eventName == MouseEventNames.motion:
            if activeControl != self._lastControlOver:
                if self._lastControlOver is not None:
                    leaveEvent = event._copy()
                    leaveEvent.eventName = MouseEventNames.leave
                    self._lastControlOver._handleMouseEvent(leaveEvent)
                if activeControl is not None:
                    enterEvent = event._copy()
                    enterEvent.eventName = MouseEventNames.enter
                    activeControl._handleMouseEvent(enterEvent)
                self._lastControlOver = activeControl
        else:
            if self._watchLastControl and self._watchedControl is not None:
                activeControl = self._watchedControl

        if activeControl is not None and event.eventName != MouseEventNames.click:
            activeControl._handleMouseEvent(event)

        if event.eventName == MouseEventNames.buttonUp:
            activeControl = self._findForegroundControl(eventX, eventY)
            if activeControl == self._watchedControl and self._watchedControl is not None:
                clickEvent = event._copy()
                clickEvent.eventName = MouseEventNames.click
                activeControl._handleMouseEvent(clickEvent)
            if self._watchLastControl:
                self._watchedControl = None

    def _findForegroundControl(self, eventX, eventY):
        activeControl = None
        for control in self._children:
            position = control.windowPosition
            size = control.size
            positionX = position.x
            positionY = position.y
            if positionX <= eventX and positionY <= eventY and positionX + size.x >= eventX and positionY + size.y >=\
                    eventY:
                activeControl = control
                break
        return activeControl


class Layer(Attachable, ResponsiveControl):
    """
    Virtual top level container for gui objects.
    Only objects attached to this will be drawn 'above' the scene, in 2D mode.
    """

    def __init__(self, ID, guiMan, visible=True):
        """


            @rtype : Layer
            @type visible: bool
            """
        Attachable.__init__(self, None)
        ResponsiveControl.__init__(self, passEventDown=True)
        self.ID = ID
        self.visible = visible
        self._pixelSize = vec3(1)
        self._guiMan = guiMan
        self._previousSize = self.pixelSize
        self._onInit = True

        self._rotationMatrix = mat4(1)
        self._positionMatrix = mat4(1)

        self._updatePixelSize()

    @property
    def position(self):
        return vec3(0)

    @property
    def left(self):
        return 0

    @property
    def top(self):
        return 0

    @property
    def windowPosition(self):
        return self.position

    @property
    def borderSize(self):
        return 0

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
        if self._onInit:
            self._previousSize = self._pixelSize
            self._onInit = False

    def getPixelSize(self):
        return self._pixelSize

    pixelSize = property(getPixelSize)

    @property
    def size(self):
        return self._pixelSize

    def _resizeCallback(self):
        self._updatePixelSize()
        for c in reversed(self._children):
            c._resizeCallback()
