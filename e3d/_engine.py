from os import path

from sdl2 import *
from ctypes import ArgumentError
from glaze.GL import loadGL, glGetIntegerv, glGetStringi, glGetString, GL_NUM_SHADING_LANGUAGE_VERSIONS, \
    GL_SHADING_LANGUAGE_VERSION, \
    GL_VERSION, GL_NUM_EXTENSIONS, GL_EXTENSIONS, glEnable, GL_MULTISAMPLE

from .Logging import _Logger, logLevelsEnum
from .backends.base_backend import BaseBackend
from .events_processing.EventsManagerClass import Event, EventsManager
from .scene_management.ScenesManagerClass import ScenesManager
from .texture_management.TextureManagerClass import TexturesManager
from .windowing.sdl_window import Window
from .ThreadingManagerClass import ThreadingManager
from .plugin_management.PluginsManagerClass import PluginsManager
# from .video import VideoManager


class globalsStruct:
    oglversionraw = None
    oglmajor = None
    oglminor = None
    glslmajor = None
    glslminor = None
    dummyContext = None
    dummyWindow = None
    glslall = None
    multisample = False


class Engine:
    def __init__(self, backend, multiSampleLevel=0, maxContext=(2, 1), useQT=False):
        self._logger = _Logger()
        if not useQT:
            # Init SDL>>>>>>>>>>>>>>>>>>>>>>>>>
            if SDL_Init(SDL_INIT_EVERYTHING) != 0:
                sdlerr = self.getSDLError()
                self.log('Error on SDL init: ' + sdlerr, logLevelsEnum.error)
                raise Exception('Error on SDL init: ' + sdlerr)

        self.maxContext = maxContext
        assert issubclass(backend, BaseBackend)
        self.backend = backend
        self.path = EngineRoot((path.dirname(__file__),))

        self.events = EventsManager()
        self.textures = TexturesManager()
        self.scenes = ScenesManager()
        # self.videos = VideoManager()
        self.threading = ThreadingManager()
        self.plugins = PluginsManager()
        self.globals = globalsStruct()
        self.models = None
        self.shaders = None
        self.sounds = None
        self.io = None
        self.localqueue = None
        self._running = False
        self._windows = {}
        self._useQT = useQT
        self._isInitialized = False

        if not useQT:
            self.__setAttribs(multiSampleLevel, maxContext)

    def initialize(self, maxThreads=2):
        self._createDummyWindowAndContext()
        loadGL()
        self._fillGLInfo()
        self.backend = self.backend(self)
        self._initializeManagers(maxThreads)
        self._isInitialized = True

    def _initializeManagers(self, maxThreads):
        # self.localqueue = Queue()

        self.log('Initializing systems...', logLevelsEnum.debug)

        self.log('\t Shaders...', logLevelsEnum.debug)
        self.shaders = self.backend.getShadersManager()

        self.log('\t Textures...', logLevelsEnum.debug)
        self.textures.initialize(self)

        self.log('\t Models...', logLevelsEnum.debug)
        from .model_management.ModelsManagerClass import ModelsManager
        self.models = ModelsManager()
        self.models.initialize(self)

        self.log('\t Sounds...', logLevelsEnum.debug)
        from .sound_management.SoundsManagerClass import SoundsManager
        self.sounds = SoundsManager()

        # self.log('\t IOHelper...', logLevelsEnum.debug)
        # from .IOHelperClass import IOHelper
        # self.io = IOHelper()

        self.log('\t Threading...', logLevelsEnum.debug)
        self.threading.initialize(maxThreads)

        self.log('\t Scenes...', logLevelsEnum.debug)
        self.scenes.initialize(self)

        self.log('\t Plugins...', logLevelsEnum.debug)
        self.plugins.initialize(self)

        # self.log('\t Videos...', logLevelsEnum.debug)
        # self.videos.initialize(self)

    def __setAttribs(self, multiSampleLevel, restrictContextTo):
        SDL_GL_SetAttribute(SDL_GL_RED_SIZE, 8)
        SDL_GL_SetAttribute(SDL_GL_GREEN_SIZE, 8)
        SDL_GL_SetAttribute(SDL_GL_BLUE_SIZE, 8)
        SDL_GL_SetAttribute(SDL_GL_ALPHA_SIZE, 8)
        SDL_GL_SetAttribute(SDL_GL_BUFFER_SIZE, 24)

        for depth in [24, 16]:
            if SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, depth) == 0:
                break
            else:
                if depth == 16:
                    error = 'Error setting depth size: ' + self.getSDLError()
                    self.log(error)
                    raise RuntimeError(error)

        if restrictContextTo:
            # Todo: add context fallback
            SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, restrictContextTo[0])
            SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, restrictContextTo[1])

        # SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG)
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)

        if SDL_GL_SetAttribute(SDL_GL_SHARE_WITH_CURRENT_CONTEXT, 1) != 0:
            error = 'Error setting SDL shared context flag: ' + self.getSDLError()
            self.log(error)
            raise RuntimeError(error)

        isDOubleBuffered = not SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1)

        if not isDOubleBuffered:
            self.log('Error setting SDL double buffer flag: ' + self.getSDLError(), logLevelsEnum.info)

        if multiSampleLevel is not None and multiSampleLevel > 0:
            self._multisampleFallback(multiSampleLevel, SDL_WINDOW_OPENGL | SDL_WINDOW_HIDDEN)

        # Next causes multisample to fail.
        # if SDL_GL_SetAttribute(SDL_GL_ACCELERATED_VISUAL, 1) != 0:
        #     error = 'Error setting SDL hw acceleration flag: ' + self.getSDLError()
        #     self.log(error)
        #     raise RuntimeError(error)

    def updateLoop(self):
        self._running = True
        while self._running:
            activeWindows = {}
            while len(self._windows) > 0:
                winID, win = self._windows.popitem()
                if win._running:
                    win.update()
                    activeWindows[winID] = win
            if len(activeWindows) > 0:
                self._windows = activeWindows.copy()
            else:
                self._running = False

        for win in self._windows.values():
            try:
                win.close()
            except:
                pass

    def _terminateManagers(self):
        if self._isInitialized:
            self.log('Terminating systems...', logLevelsEnum.debug)
            self.textures.terminate()
            self.shaders.terminate()
            self.sounds.terminate()
            self.scenes.terminate()
            self.threading.terminate()
            self.plugins.terminate()
            # self.videos.terminate()

            # self.localqueue.close()

    def postEvent(self, event):
        if not issubclass(type(event), Event) or not isinstance(event, Event):
            raise TypeError('"event" object must be of type "Event" or inherith from it.\n'
                            'It is of type: ' + str(type(event)))

        self.events._announce(event)

    def createWindow(self, title='', gameName='', size=None, FullScreenSize=None, fullscreen=False,
                     vSynch=True, iconPath=None):
        """

        :rtype: Window
        """
        if not self._isInitialized:
            raise RuntimeError('engine is not initialized')
        win = Window(self, title, gameName, size, FullScreenSize, fullscreen, vSynch, iconPath)
        self._windows[id(win)] = win
        return win

    def createQTWidget(self, title='', gameName='', size=None, FullScreenSize=None, fullscreen=False,
                       vSynch=True, iconPath=None):
        """

        :rtype: e3DGLWidget
        """

        if not self._isInitialized:
            raise RuntimeError('engine is not initialized')
        from .windowing.qt_window import e3DGLWidget
        win = e3DGLWidget(self, title, gameName, size, FullScreenSize, fullscreen, vSynch, iconPath)
        return win

    def _fillGLInfo(self):
        self.globals.oglversionraw = glGetString(GL_VERSION)
        ss = self.globals.oglversionraw.split(' ')
        ss2 = ss[0].split('.')
        self.globals.oglmajor = int(ss2[0])
        self.globals.oglminor = int(ss2[1])
        ssb = glGetString(GL_SHADING_LANGUAGE_VERSION).split(' ')
        ss3 = ssb[0].split('.')
        self.globals.glslmajor = int(ss3[0])
        self.globals.glslminor = int(ss3[1])

        try:
            self._fillSuportedGLSLVersions()
        except:
            pass
        self.log('OpenGL version: ' + str(self.globals.oglversionraw), logLevelsEnum.info)
        self.log('GLSL version: {}.{}'.format(self.globals.glslmajor, self.globals.glslminor), logLevelsEnum.info)
        if len(self.globals.glslall) > 0:
            self.log('{} GLSL supported versions'.format(len(self.globals.glslall)), logLevelsEnum.debug)
            for ver in self.globals.glslall:
                self.log('{} GLSL supported'.format(ver))

    def _fillSuportedGLSLVersions(self):
        import numpy as np
        num = np.array([0], np.int32)
        glGetIntegerv(GL_NUM_SHADING_LANGUAGE_VERSIONS, num)
        vl = []
        for e in range(num[0]):
            vl.append(glGetStringi(GL_SHADING_LANGUAGE_VERSION, e))
        self.globals.glslall = vl

    def logSupportedExtensions(self):
        num = glGetIntegerv(GL_NUM_EXTENSIONS)
        for e in range(num):
            self.log(glGetStringi(GL_EXTENSIONS, e), logLevelsEnum.info)

    def _createDummyWindowAndContext(self):
        if not self._useQT:
            self._dummySDL()
        else:
            self._dummyQT()

    def _dummyQT(self):
        from PySide.QtOpenGL import QGLWidget, QGLFormat
        format = QGLFormat()
        format.setRedBufferSize(8)
        format.setGreenBufferSize(8)
        format.setBlueBufferSize(8)
        format.setDepthBufferSize(24)
        format.setAlphaBufferSize(8)
        format.setDoubleBuffer(True)
        format.setDirectRendering(True)
        format.setDepth(True)
        format.setAlpha(True)
        format.setVersion(2, 1)
        format.setProfile(QGLFormat.CoreProfile)

        self._format = format
        try:
            self.globals.dummyWindow = QGLWidget(format)
        except Exception as ex:
            error = 'Error creating dummy window: ' + str(ex)
            self.log(error, logLevelsEnum.error)
            raise RuntimeError(error)

        try:
            _, self.globals.dummyContext = self._getNewContext()
        except:
            raise
        self.globals.dummyWindow.makeCurrent()

    def _dummySDL(self):
        flags = SDL_WINDOW_OPENGL | SDL_WINDOW_HIDDEN

        try:
            self.globals.dummyWindow = SDL_CreateWindow('', -1, -1, 0, 0, flags)
        except ArgumentError:
            self.globals.dummyWindow = SDL_CreateWindow(b'', -1, -1, 0, 0, flags)
        sdlerr = self.getSDLError()
        if self.globals.dummyWindow is None or sdlerr != '':
            error = 'Error creating dummy window: ' + sdlerr
            self.log(error, logLevelsEnum.error)
            raise RuntimeError(error)

        try:
            _, self.globals.dummyContext = self._getNewContext()
        except:
            raise
        SDL_GL_MakeCurrent(self.globals.dummyWindow, self.globals.dummyContext)

    def _getNewContext(self, window=None):
        """

        @rtype : (SDL_Window, SDL_GLContext)
        """
        if window is None:
            window = self.globals.dummyWindow
        if not self._useQT:
            newContext = SDL_GL_CreateContext(window)
            if not newContext:
                sdlerr = self.getSDLError()
                error = 'Error creating context: ' + sdlerr
                self.log(error, logLevelsEnum.error)
                raise RuntimeError(error)
        else:
            newContext = self.globals.dummyWindow.context()

        return window, newContext

    def _multisampleFallback(self, multisampleLevel, flags):
        window = None
        ms = SDL_GL_SetAttribute(SDL_GL_MULTISAMPLEBUFFERS, 1)
        if ms < 0:
            self.log('Error setting multisample: ' + self.getSDLError(), logLevelsEnum.warning)
            self.globals.multisample = False
        else:
            self.globals.multisample = True
        level = multisampleLevel
        while level > 0:
            if SDL_GL_SetAttribute(SDL_GL_MULTISAMPLESAMPLES, level) == 0:
                try:
                    window = SDL_CreateWindow('', -1, -1, 0, 0, flags)
                except ArgumentError:
                    window = SDL_CreateWindow(b'', -1, -1, 0, 0, flags)
                cont = SDL_GL_CreateContext(window)
                if cont is not None:
                    SDL_GL_DeleteContext(cont)
                    break

            level -= 1
            if level > 0:
                self.log('Error setting multisample level {}. Trying {}'.format(level + 1, level), logLevelsEnum.info)

        if level == 0:
            self.log('Multisample disabled: ' + self.getSDLError() + ".")
            SDL_GL_SetAttribute(SDL_GL_MULTISAMPLEBUFFERS, 0)

        if window:
            SDL_DestroyWindow(window)

    @staticmethod
    def getSDLError():
        sderr = SDL_GetError()
        try:
            sderr = sderr.decode()
        except:
            pass
        return sderr

    def terminate(self):
        self._running = False
        try:
            self._terminateManagers()
        except Exception as ex:
            self.log('Error in \'Engine.terminate\': ' + str(ex), logLevelsEnum.error)
        if not self._useQT:
            if self._isInitialized:
                SDL_GL_DeleteContext(self.globals.dummyContext)
                SDL_DestroyWindow(self.globals.dummyWindow)
            SDL_Quit()
        else:
            if self._isInitialized:
                self.globals.dummyWindow.doneCurrent()
                self.globals.dummyWindow.deleteLater()
        self.log('Engine Terminated', logLevelsEnum.info)

    def log(self, message, messageType=logLevelsEnum.debug):
        self._logger.log(message, messageType)


class PathPiece(str):
    def __new__(cls, elements):
        basePath = path.join(*elements)
        base = path.abspath(basePath)
        obj = str.__new__(cls, base)
        obj.base = base
        return obj


class EngineRoot(PathPiece):
    def __init__(self, elements):
        super(EngineRoot, self).__init__()
        self.defaults = DefaultPath((self.base, 'defaults'))


class DefaultPath(PathPiece):
    def __init__(self, elements):
        super(DefaultPath, self).__init__()
        self.shaders = PathPiece((self.base, 'shaders'))
        self.textures = PathPiece((self.base, 'textures'))
        self.primitives = PathPiece((self.base, 'primitives'))
        self.fonts = PathPiece((self.base, 'fonts'))
        # self.sounds = PathPiece((self.base, 'sounds'))


