from time import time
import os

from e3d.LoggerClass import logger, logLevelsEnum
from e3d.events_processing.EventsListenerClass import EventsListener
from e3d.events_processing.EventsManagerClass import EventsManager
from e3d.gui.GuiManagerClass import GuiManager
from e3d.update_management.updateMethods import updateAll


class Window_Base(object):
    def __init__(self, engine, title, gameName, sizeAsList, FullScreenSize, fullscreen, vSynch, iconPath):
        """









            @type vSynch: bool
            @type sizeAsList: list
            @type title: str
            @type FullScreenSize: list
            @type fullscreen: bool
            @param title: The window title
            @param sizeAsList: The size (as list) of the window
            @param FullScreenSize: The size (as list) to display when in fullscreen mode
            @param fullscreen: start in fullscreen
            @param vSynch: enable vsynch
            @type gameName: str
            @param parent: native handler to embed the engine into another window
            @param gameName: Used fro automatic functions, like Screenshot saving
            @type parent: long
            """
        self.engine = engine
        self.firstRunCallback = None
        self.renderBeginCallback = None
        self.renderEndCallback = None
        self.FPS_UpdatedCallback = None
        self.gui = GuiManager()
        self._frames = 0
        self._running = True
        self.useMultisample = False
        self._SDL_Window = None
        self._context = None
        self._isFocused = False
        self.mouseLock = False
        self.is1stRun = True
        self.events = EventsManager()
        self._defaultWindowEventListener = winEvents(self)
        self.events.addListener('default', self._defaultWindowEventListener)
        self._isFull = fullscreen
        self.is1stRun = True
        self.backend = None

        self._framesThisSecond = 0
        self._lastTime = 0
        self._netTime = 0
        self._debug_minFPS = 0
        self._debug_maxFPS = 0

        if gameName != '':
            self.gameName = gameName
        else:
            self.gameName = u'Game powered by Engendro3D\u2122'
        if title == '':
            title = self.gameName

        if sizeAsList is not None and len(sizeAsList) == 2:
            self._size = sizeAsList
        else:
            self._size = [640, 480]
        if FullScreenSize is not None and len(FullScreenSize) == 2:
            self._fullscreenSize = FullScreenSize
        else:
            self._fullscreenSize = self._size
        logger.log(u'Starting new window for: ' + self.gameName, 0)

        self._createInternalWindow(title, engine, fullscreen)

        self.vsynch = vSynch

        self.backend = engine.base_backend(engine, self)

        self.backend.resize((self._size[0], self._size[1]))

        if iconPath:
            self.setIcon(iconPath)
        else:
            self.setIcon(os.path.join(self.engine.path.defaults.textures, 'e3dlogo.png'))

        self.gui.initialize(self.engine, self.backend, self.engine.textures.getDefaultTexture(), self)

        self._startupTime = int(round(time() * float(1000)))

        logger.log('Window created for: ' + self.gameName, 0)

    def __repr__(self):
        return self.title

    def _createInternalWindow(self, title, engine, fullscreen):
        pass

    def setFullScreen(self, setfull):
        pass

    def isFullScreen(self):
        return self._isFull

    def update(self):
        try:
            self._pollEvents()

            sceneDrawingData, guiDrawingData = updateAll(self, self._netTime)
            if self.renderBeginCallback is not None:
                self.renderBeginCallback([self._netTime, self])

            self._makeContextCurrent()
            self.backend.drawAll(sceneDrawingData)

            self.backend.switchMultiSample(0)
            self.backend.renderMeshes(guiDrawingData)
            self.backend.switchMultiSample(1)

            if self.is1stRun:
                self.is1stRun = False
                if self.firstRunCallback is not None:
                    self.firstRunCallback([self])

            if self.renderEndCallback is not None:
                self.renderEndCallback([self._netTime, self])

            self._performSwap()
            self._netTime = int(round(time() * float(1000))) - self._startupTime
            lastFPSCalcElapsed = self._netTime - self._lastTime
            self._calculateFPS(lastFPSCalcElapsed)
        except KeyboardInterrupt:
            logger.log('KeyboardInterrupt.', logLevelsEnum.info)
            self.close()

    def _performSwap(self):
        pass

    def _makeContextCurrent(self):
        pass

    def _pollEvents(self):
        pass

    def _calculateFPS(self, lastCalcElapsed):
        self._framesThisSecond += 1
        if self._lastTime == 0:
            self._lastTime = self._netTime

        if lastCalcElapsed >= 1000:
            self._frameTime = round(float(float(lastCalcElapsed) / float(self._framesThisSecond)), 2)
            self._lastFPS = int((float(self._framesThisSecond) / float(lastCalcElapsed)) * 1000.0)
            if self.FPS_UpdatedCallback is not None:
                self.FPS_UpdatedCallback([self._lastFPS, self._frameTime])

            if self._debug_minFPS == 0:
                self._debug_minFPS = self._lastFPS
            if self._lastFPS > self._debug_maxFPS:
                self._debug_maxFPS = self._lastFPS
            if self._lastFPS < self._debug_minFPS:
                self._debug_minFPS = self._lastFPS

            self._framesThisSecond = 0
            self._lastTime = self._netTime

    def _sizeChanged(self, w, h):
        """Reshape the OpenGL viewport based on the dimensions of the window."""
        self.engine.scenes.currentScene.currentCamera.updateFOV(w, h)
        self._makeContextCurrent()
        self.backend.resize((w, h))

    def close(self):
        # TODO: add 'closed' callback
        self._running = False
        self.setFullScreen(False)
        self.backend.terminate()

        logger.log(u'Window for {} closed.'.format(self.gameName))

    def hasFocus(self):
        return self._isFocused

    def setIcon(self, path):
        pass

    def getMultiSampleNumber(self):
        pass

    def onKeyEvent(self, event):
        pass

    def onMouseEvent(self, event):
        pass

    def onWindowEvent(self, event):
        pass

    @property
    def size(self):
        pass

    @size.setter
    def _setSize(self, val):
        pass

    @property
    def isRunning(self):
        return self._running

    @property
    def title(self):
        """

        @rtype : str
        """
        pass

    @title.setter
    def title(self, value):
        """

        @type value: str
        """
        pass

    @property
    def gamma(self):
        """
        Set int value for this window's gamma.
        @type vakue: int
        # SDL_SetWindowBrightness
        """
        pass

    @gamma.setter
    def gamma(self, value):
        pass

    @property
    def vsynch(self):
        pass

    @vsynch.setter
    def vsynch(self, val):
        pass


class winEvents(EventsListener):
    def onMouseEvent(self, event):
        self.window.onMouseEvent(event)

    def onWindowEvent(self, event):
        if event.eventName == 'focusGained':
            self.window._isFocused = True
        elif event.eventName == 'focusLost':
            self.window._isFocused = False
        self.window.onWindowEvent(event)

    def onKeyEvent(self, event):
        self.window.onKeyEvent(event)

    def __init__(self, window):
        super(winEvents, self).__init__()
        self.window = window