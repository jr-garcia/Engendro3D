import sfml as sf
from time import time

from .backends.base_backend import BaseBackend
from .events_processing.EventsManagerClass import EventsManager
from e3d.events_processing.EventsListenerClass import EventsListener
from .LoggerClass import logger, logLevelsEnum
from .update_management.updateMethods import updateAll


class Window(object):
    """
    Class for starting (and embedding) an Engendro3D Window.

    """

    # @property
    # def title(self):

    # @title.getter
    def _getTitle(self):
        """

        @rtype : str
        """
        t = SDL_GetWindowTitle(self._Window)
        return t

    # @title.setter
    def _setTitle(self, value):
        """

        @type value: str
        """
        SDL_SetWindowTitle(self._Window, value)

    title = property(fget=_getTitle, fset=_setTitle)

    def _getIsRunning(self):
        return self._running

    isRunning = property(fget=_getIsRunning)

    def __init__(self, engine, title, gameName, size, FullScreenSize, parent, fullscreen, vSynch,
                 iconPath):
        """









            @type vSynch: bool
            @type size: list
            @type title: str
            @type FullScreenSize: list
            @type fullscreen: bool
            @param title: The window title
            @param size: The size (as list) of the window
            @param FullScreenSize: The size (as list) to display when in fullscreen mode
            @param fullscreen: start in fullscreen
            @param vSynch: enable vsynch
            @type gameName: str
            @param parent: native handler to embed the engine into another window
            @param gameName: Used fro automatic functions, like Screenshot saving
            @type parent: long
            """
        self.firstRunCallback = None
        self.renderBeginCallback = None
        self.renderEndCallback = None
        self.engine = engine
        # self.gui = GuiManager()
        self._frames = 0
        self._running = True
        self.useMultisample = False
        self._context = None
        self._isFocused = False
        self.mouseLock = False
        self.is1stRun = True
        self.events = EventsManager()
        self._defaultEventListener = winEvents(self)
        self.events.addListener('default', self._defaultEventListener)
        self._size = size

        self.__isFull = fullscreen
        if gameName != '':
            self.gameName = gameName
        else:
            self.gameName = u'Game powered by Engendro3D\u2122'
        if title == '':
            title = self.gameName
        if size is not None and len(size) == 2:
            self._size = size
        else:
            self._size = [640, 480]
        if FullScreenSize is not None and len(FullScreenSize) == 2:
            self._fullscreenSize = FullScreenSize
        else:
            self._fullscreenSize = self._size
        logger.log(u'Starting new window for: ' + self.gameName, 0)

        settings = sf.ContextSettings()
        settings.depth_bits = 24
        settings.stencil_bits = 8
        settings.antialiasing_level = 16
        settings.major_version = engine.maxContext[0]
        settings.minor_version = engine.maxContext[1]

        self._window = sf.Window(sf.VideoMode(size[0], size[1]), title, sf.Style.DEFAULT, settings)
        if not self._window:
            msg = u'Error creating window for \'{}\': {}'.format(self.gameName, sdlerr)
            logger.log(msg)
            raise Exception(msg)
        if iconPath:
            self.setIcon(iconPath)
        self._window.vertical_synchronization = vSynch
        self.backend = engine.base_backend(engine)
        assert isinstance(self.backend, BaseBackend)
        self.backend.resize((self._size[0], self._size[1]))

        if fullscreen:
            self.setFullScreen(True)

        # self.gui.initialize(manfred)
        self._startupTime = 0
        logger.log('Window created for: ' + self.gameName, 0)

    def setFullScreen(self, setfull):
        print('window.setfullscreen not implemented')
        # if setfull:
        #     f = SDL_WINDOW_FULLSCREEN
        # else:
        #     f = 0
        # # todo: resize if sizeaslist != fullscreensize
        #
        # SDL_SetWindowFullscreen(self._Window, f)
        # self.__isFull = setfull

    def isFullScreen(self):
        return self.__isFull

    def update(self):
        is1stRun = True
        self._startupTime = int(round(time() * float(1000)))

        try:
            while self._running:
                for event in self._window.events:
                    self.events._announce(event)
                    eventtype = type(event)
                    if eventtype == sf.ResizeEvent:
                        self._sizeChanged(self._window.size.x, self._window.size.y)
                    elif eventtype is sf.CloseEvent:
                        self.close()

                netElapsedTime = int(round(time() * float(1000))) - self._startupTime

                sceneDrawingData, guiDrawingData = updateAll(self, netElapsedTime)
                if self.renderBeginCallback is not None:
                    self.renderBeginCallback([netElapsedTime, self])

                self.backend.drawAll(sceneDrawingData)

                if is1stRun:
                    try:
                        is1stRun = False
                        if self.firstRunCallback is not None:
                            self.firstRunCallback([self])
                    except TypeError as ex:
                        if "object is not callable" in ex.message.lower():
                            pass
                        else:
                            raise

                if self.renderEndCallback is not None:
                    self.renderEndCallback([netElapsedTime, self])

                self._window.display()
        except KeyboardInterrupt:
            logger.log('KeyboardInterrupt.', logLevelsEnum.info)
            self.close()

    def updateLoop(self):
        while self._window.is_open:
            self.update()

    def _getSize(self):
        return [self._window.size.x, self._window.size.y]

    def _setSize(self, val):
        # w, h = val
        # self._size = val
        # if not self.__isFull:
        #     self._window.
        #     self._size = [w, h]
        # else:
        #     SDL_SetWindowDisplayMode(_SDL_Window, SDL_DisplayMode(w, h))
        #     self._fullscreenSize = [w, h]
        # self._sizeChanged(w, h)
        print('size not implemented')

    size = property(_getSize, _setSize, doc="""@type val: list""")

    def _sizeChanged(self, w, h):
        """Reshape the OpenGL viewport based on the dimensions of the window."""
        self.engine.scenes.currentScene.currentCamera.updateFOV(w, h)
        self.backend.resize((w, h))

    def close(self):
        # TODO: add 'closed' callback
        self.setFullScreen(False)
        self._running = False
        self.backend.terminate()
        self._window.close()
        logger.log(u'Window for {} closed.'.format(self.gameName))

    def hasFocus(self):
        return self._isFocused

    def _getMouseMode(self):
        print('Not implemented mouseLock')
        return False

    def _setMouseMode(self, value):
        print('Not implemented mouseLock')

    mouseLock = property(_getMouseMode, _setMouseMode)

    def setIcon(self, path):
        try:
            from PIL import Image
            im = Image.open(path)
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
            SDL_SetWindowIcon(self._Window, surface)
            SDL_FreeSurface(surface)

        except Exception as ex:
            logger.log('Window.setIcon error: ' + str(ex), logLevelsEnum.debug)

    def _setGamma(self, value):
        """
        Set int value for this window's gamma.
        @type vakue: int
        # SDL_SetWindowBrightness
        """
        if (not isinstance(value, int) and not isinstance(value, float)) or value <= 0:
            raise ValueError('Gamma value must be a float > 0.')
        if SDL_SetWindowBrightness(self._Window, value) != 0:
            raise Exception('Error setting Gamma: ' + SDL_GetError())

    def _getGamma(self):
        return SDL_GetWindowBrightness(self._Window)

    gamma = property(_getGamma, _setGamma)

    def _get_vSynch(self):
        si = self._window.vertical_synchronization
        return bool(si)

    def _set_vSynch(self, val):
        self._window.vertical_synchronization = val

    vSynch = property(_get_vSynch, _set_vSynch)

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
        if event.name == 'focusGained':
            self.window._isFocused = True
        elif event.name == 'focusLost':
            self.window._isFocused = False
        self.window.onWindowEvent(event)

    def onKeyEvent(self, event):
        self.window.onKeyEvent(event)

    def __init__(self, window):
        super(winEvents, self).__init__()
        self.window = window

