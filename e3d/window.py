from sdl2 import *
import ctypes as ct
from time import time
import os

from .backends.base_backend import BaseBackend
from .events_processing.EventsManagerClass import EventsManager
from e3d.events_processing.EventsListenerClass import EventsListener
from .LoggerClass import logger, logLevelsEnum
from .update_management.updateMethods import updateAll
from .gui.GuiManagerClass import GuiManager


class Window(object):
    """
    Class for starting (and embedding) an Engendro3D Window.

    """
    def __init__(self, engine, title, gameName, sizeAsList, FullScreenSize, parent, fullscreen, vSynch,
                 iconPath):
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

        try:
            title = title.encode()
        except:
            pass
        if sizeAsList is not None and len(sizeAsList) == 2:
            self._size = sizeAsList
        else:
            self._size = [640, 480]
        if FullScreenSize is not None and len(FullScreenSize) == 2:
            self._fullscreenSize = FullScreenSize
        else:
            self._fullscreenSize = self.size
        logger.log(u'Starting new window for: ' + self.gameName, 0)
        flags = SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE
        if fullscreen:
            flags = flags | SDL_WINDOW_FULLSCREEN

        if parent:
            parentAsVoid = ct.pointer(ct.c_void_p(parent))
            self._SDL_Window = SDL_CreateWindowFrom(parentAsVoid)
        else:
            self._SDL_Window = SDL_CreateWindow(title, SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, self._size[0],
                                                self._size[1], flags)
        if not self._SDL_Window:
            sdlerr = SDL_GetError()
            msg = u'Error creating window for \'{}\': {}'.format(self.gameName, sdlerr)
            logger.log(msg)
            raise Exception(msg)

        _, self._context = engine._getNewContext(self._SDL_Window)
        SDL_GL_MakeCurrent(self._SDL_Window, self._context)
        self._set_vsynch(vSynch)

        self.backend = engine.base_backend(engine, self)

        self.backend.resize((self._size[0], self._size[1]))

        if iconPath:
            self.setIcon(iconPath)
        else:
            self.setIcon(os.path.join(self.engine.path.defaults.textures, 'e3dlogo.png'))

        self.gui.initialize(self.engine, self.backend,
                            self.engine.textures.getDefaultTexture(), self)

        self._startupTime = int(round(time() * float(1000)))

        logger.log('Window created for: ' + self.gameName, 0)

    def setFullScreen(self, setfull):
        if setfull:
            f = SDL_WINDOW_FULLSCREEN
        else:
            f = 0
        # todo: resize if size != fullscreensize

        SDL_SetWindowFullscreen(self._SDL_Window, f)
        self._isFull = setfull

    def isFullScreen(self):
        return self._isFull

    def update(self):
        event = SDL_Event()
        try:
            while SDL_PollEvent(event):
                self.events._announce(event)
                if event.type == SDL_QUIT:
                    self.close()
                elif event.type == SDL_WINDOWEVENT:
                    winev = event.window.event
                    if winev == SDL_WINDOWEVENT_SIZE_CHANGED:
                        self._sizeChanged(event.window.data1, event.window.data2)
                    elif winev == SDL_WINDOWEVENT_CLOSE:
                        self.close()

            sceneDrawingData, guiDrawingData = updateAll(self, self._netTime)
            if self.renderBeginCallback is not None:
                self.renderBeginCallback([self._netTime, self])

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

            SDL_GL_SwapWindow(self._SDL_Window)
            self._netTime = int(round(time() * float(1000))) - self._startupTime
            lastFPSCalcElapsed = self._netTime - self._lastTime
            self._calculateFPS(lastFPSCalcElapsed)
        except KeyboardInterrupt:
            logger.log('KeyboardInterrupt.', logLevelsEnum.info)
            self.close()

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

    def _getTitle(self):
        """

        @rtype : str
        """
        t = SDL_GetWindowTitle(self._SDL_Window)
        return t

    def _setTitle(self, value):
        """

        @type value: str
        """
        try:
            value = value.encode()
        except:
            pass
        SDL_SetWindowTitle(self._SDL_Window, value)

    title = property(fget=_getTitle, fset=_setTitle)

    def _getIsRunning(self):
        return self._running

    isRunning = property(fget=_getIsRunning)

    def _get_vsynch(self):
        ret = SDL_GL_GetSwapInterval()
        if ret != 0:
            return True
        else:
            return False

    def _set_vsynch(self, val):
        if bool(val):
            if SDL_GL_SetSwapInterval(-1) == -1:
                SDL_GL_SetSwapInterval(1)
        else:
            SDL_GL_SetSwapInterval(0)

    vsynch = property(_get_vsynch, _set_vsynch)

    def _getSize(self):
        w = ct.pointer(ct.c_int(0))
        h = ct.pointer(ct.c_int(0))
        SDL_GetWindowSize(self._SDL_Window, w, h)

        return w.contents.value, h.contents.value

    def _setSize(self, val):
        w, h = val
        self._size = val
        if not self._isFull:
            SDL_SetWindowSize(self._SDL_Window, ct.c_long(w), ct.c_long(h))
            self._size = [w, h]
        else:
            SDL_SetWindowDisplayMode(_SDL_Window, SDL_DisplayMode(w, h))
            self._fullscreenSize = [w, h]
        self._sizeChanged(w, h)

    size = property(_getSize, _setSize, doc="""@type val: tuple""")

    def _sizeChanged(self, w, h):
        """Reshape the OpenGL viewport based on the dimensions of the window."""
        self.engine.scenes.currentScene.currentCamera.updateFOV(w, h)
        self.backend.resize((w, h))

    def close(self):
        # TODO: add 'closed' callback
        self._running = False
        self.setFullScreen(False)
        self.backend.terminate()
        SDL_GL_DeleteContext(self._context)
        SDL_DestroyWindow(self._SDL_Window)
        logger.log(u'Window for {} closed.'.format(self.gameName))

    def hasFocus(self):
        return self._isFocused

    def _getMouseMode(self):
        return SDL_GetRelativeMouseMode()

    def _setMouseMode(self, value):
        # todo: move cursor to window center before changing this
        SDL_SetRelativeMouseMode(value)

    mouseLock = property(_getMouseMode, _setMouseMode)

    def setIcon(self, path):
        aPath = os.path.abspath(path)
        if not os.path.exists(aPath):
            logger.log('Window.setIcon error: File {} not found. Skipping.'.format(aPath))
            return
        try:
            from PIL import Image
            im = Image.open(aPath)
            w, h = im.size[0], im.size[1]
            if im.mode == 'RGB':
                alphamask = 0
                depth = 24
            else:
                alphamask = 0xFF000000
                depth = 32
            try:
                pix = im.tobytes()
                im.close()
            except:
                raise

            surface = SDL_CreateRGBSurfaceFrom(pix, w, h, depth, w * 4, 0x000000FF, 0x0000FF00, 0x00FF0000, alphamask)
            SDL_SetWindowIcon(self._SDL_Window, surface)
            SDL_FreeSurface(surface)

        except Exception as ex:
            logger.log('Window.setIcon error: ' + str(ex), logLevelsEnum.debug)
            raise

    def _setGamma(self, value):
        """
        Set int value for this window's gamma.
        @type vakue: int
        # SDL_SetWindowBrightness
        """
        if (not isinstance(value, int) and not isinstance(value, float)) or value <= 0:
            raise ValueError('Gamma value must be a float > 0.')
        if SDL_SetWindowBrightness(self._SDL_Window, value) != 0:
            raise Exception('Error setting Gamma: ' + SDL_GetError())

    def _getGamma(self):
        return SDL_GetWindowBrightness(self._SDL_Window)

    gamma = property(_getGamma, _setGamma)

    def getMultiSampleNumber(self):
        # res = ct.pointer(ct.c_long(0))
        # if not SDL_GL_GetAttribute(SDL_GL_MULTISAMPLESAMPLES, res):
        #     return res.contents.value
        # else:
        #     return 0
        print('Not implemented.')
        return -1

    def onKeyEvent(self, event):
        pass

    def onMouseEvent(self, event):
        pass

    def onWindowEvent(self, event):
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
