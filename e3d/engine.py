from os import path

from sdl2 import *
from ctypes import ArgumentError
from glaze.GL import loadGL, glGetIntegerv, glGetStringi, glGetString, GL_NUM_SHADING_LANGUAGE_VERSIONS, \
    GL_SHADING_LANGUAGE_VERSION, \
    GL_VERSION, GL_NUM_EXTENSIONS, GL_EXTENSIONS, glEnable, GL_MULTISAMPLE

from .LoggerClass import logger, logLevelsEnum
from .backends.base_backend import BaseBackend
from .events_processing.EventsManagerClass import Event, EventsManager
from .scene_management.ScenesManagerClass import ScenesManager
from .texture_management.TextureManagerClass import TexturesManager
from .window import Window


class globalsStruct:
    oglversionraw = None
    oglmajor = None
    oglminor = None
    glslmajor = None
    glslminor = None
    dummycontext = None
    dummywindow = None
    glslall = None
    multisample = False


class Engine:
    def __init__(self, backend, multiSampleLevel, maxContext=(2, 1), logLevel=logLevelsEnum.error):
        logger.logLevel = logLevel
        # Init SDL>>>>>>>>>>>>>>>>>>>>>>>>>
        if SDL_Init(SDL_INIT_EVERYTHING) != 0:
            sdlerr = self.getSDLError()
            logger.log('Error on SDL init: ' + sdlerr)
            raise Exception('Error on SDL init: ' + sdlerr)

        self.maxContext = maxContext
        assert issubclass(backend, BaseBackend)
        self.base_backend = backend
        self.path = EngineRoot((path.dirname(__file__),))

        self.models = None
        self.events = EventsManager()
        self.shaders = None
        self.textures = TexturesManager()
        self.scenes = ScenesManager()
        self.sounds = None
        self.io = None
        self.threading = None
        self.globals = globalsStruct()
        self.localqueue = None
        self._running = False
        self._windows = {}

        self.__setAttribs(multiSampleLevel, maxContext)

    def initialize(self):
        self.__createDummyWindowAndContext()
        loadGL()
        self._fillGLInfo()
        self._initializeManagers(0)

    def _initializeManagers(self, maxThreads=0):
        # self.localqueue = Queue()

        logger.log('Initializing systems...')

        print('\t Shaders...')
        self.shaders = self.base_backend.getShadersManager()()
        self.shaders.initialize(self)

        print('\t Textures...')
        self.textures.initialize(self, (None, None))

        print('\t Models...')
        from .model_management.ModelsManagerClass import ModelsManager
        self.models = ModelsManager()
        self.models.initialize(self)

        print('\t Sounds...')
        from .sound_management.SoundsManagerClass import SoundsManager
        self.sounds = SoundsManager()

        # print('\t IOHelper...')
        # from .IOHelperClass import IOHelper
        # self.io = IOHelper()

        # print('\t Threading...')
        # from ..ThreadingManagerClass import ThreadingManager
        # self.threading = ThreadingManager()
        # self.threading.initialize(maxThreads)

        print('\t Scenes...')
        self.scenes.initialize(self)

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
                    logger.log(error)
                    raise RuntimeError(error)

        if restrictContextTo:
            # Todo: add context fallback
            SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, restrictContextTo[0])
            SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, restrictContextTo[1])

        # SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG)
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)

        if SDL_GL_SetAttribute(SDL_GL_SHARE_WITH_CURRENT_CONTEXT, 1) != 0:
            error = 'Error setting SDL shared context flag: ' + self.getSDLError()
            logger.log(error)
            raise RuntimeError(error)

        isDOubleBuffered = not SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1)

        if not isDOubleBuffered:
            logger.log('Error setting SDL double buffer flag: ' + self.getSDLError(), logLevelsEnum.info)

        if multiSampleLevel is not None and multiSampleLevel > 0:
            self._multisampleFallback(multiSampleLevel, SDL_WINDOW_OPENGL | SDL_WINDOW_HIDDEN)

        # Next causes multisample to fail.
        # if SDL_GL_SetAttribute(SDL_GL_ACCELERATED_VISUAL, 1) != 0:
        #     error = 'Error setting SDL hw acceleration flag: ' + self.getSDLError()
        #     logger.log(error)
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
        logger.log('Terminating systems...')
        self.textures.terminate()
        self.shaders.terminate()
        self.sounds.terminate()
        self.scenes.terminate()
        # self.threading.terminate()

        # self.localqueue.close()

    def postEvent(self, event):
        if not issubclass(type(event), Event) or not isinstance(event, Event):
            raise TypeError('"event" object must be of type "Event" or inherith from it.\n'
                            'It is of type: ' + str(type(event)))

        self.events._announce(event)

    def createWindow(self, title='', gameName='', size=None, FullScreenSize=None, parent=None, fullscreen=False,
                     vSynch=True, iconPath=None):
        """

        :rtype: Window
        """
        win = Window(self, title, gameName, size, FullScreenSize, parent, fullscreen, vSynch, iconPath)
        self._windows[id(win)] = win
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
        # if ss3[0] == '4' and int(ss3[1]) >= 30:
        try:
            self._fillSuportedGLSLVersions()
        except:
            pass
        logger.log('OpenGL version: ' + str(self.globals.oglversionraw), logLevelsEnum.info)
        logger.log('GLSL version: {}.{}'.format(self.globals.glslmajor, self.globals.glslminor), logLevelsEnum.info)
        if len(self.globals.glslall) > 0:
            logger.log('{} GLSL supported versions'.format(len(self.globals.glslall)), logLevelsEnum.debug)
            for ver in self.globals.glslall:
                logger.log('{} GLSL supported'.format(ver))

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
            logger.log(glGetStringi(GL_EXTENSIONS, e))

    def __createDummyWindowAndContext(self):
        flags = SDL_WINDOW_OPENGL | SDL_WINDOW_HIDDEN

        try:
            self.globals.dummywindow = SDL_CreateWindow('', -1, -1, 0, 0, flags)
        except ArgumentError:
            self.globals.dummywindow = SDL_CreateWindow(b'', -1, -1, 0, 0, flags)
        sdlerr = self.getSDLError()
        if self.globals.dummywindow is None or sdlerr != '':
            error = 'Error creating dummy window: ' + sdlerr
            logger.log(error)
            raise RuntimeError(error)

        try:
            _, self.globals.dummycontext = self._getNewContext()
        except:
            raise
        SDL_GL_MakeCurrent(self.globals.dummywindow, self.globals.dummycontext)

    def _getNewContext(self, window=None):
        """

        @rtype : (SDL_Window, SDL_GLContext)
        """
        if window is None:
            window = self.globals.dummywindow
        newContext = SDL_GL_CreateContext(window)
        if not newContext:
            sdlerr = self.getSDLError()
            error = 'Error creating context: ' + sdlerr
            logger.log(error)
            raise RuntimeError(error)
        return window, newContext

    def _multisampleFallback(self, multisampleLevel, flags):
        window = None
        ms = SDL_GL_SetAttribute(SDL_GL_MULTISAMPLEBUFFERS, 1)
        if ms < 0:
            logger.log('Error setting multisample: ' + self.getSDLError())
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
                logger.log('Error setting multisample level {}. Trying {}'.format(level + 1, level), logLevelsEnum.info)

        if level == 0:
            logger.log('Multisample disabled: ' + self.getSDLError() + ".")
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
            logger.log('Error in \'Engine.terminate\': ' + str(ex))
        SDL_GL_DeleteContext(self.globals.dummycontext)
        SDL_DestroyWindow(self.globals.dummywindow)
        SDL_Quit()
        logger.log('Engine Terminated. Logger closed.')


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


