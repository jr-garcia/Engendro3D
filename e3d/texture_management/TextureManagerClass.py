import os
from multiprocessing import Process, cpu_count, Queue
from multiprocessing.queues import Empty
from time import sleep
from warnings import warn


from .CubeTextureClass import CubeTexture
from ..events_processing.eventClasses import Event, EventType
from .TextureManagerServer import serve, TexturesManagerServer
# from ThreadedSystemClass import ThreadedSystem
# from ParalellServiceClass import messageType
from ..Logging import logLevelsEnum
from .._baseManager import BaseManager


class textureLoadedEvent(Event):
    def __init__(self, textureID):
        super(textureLoadedEvent, self).__init__(EventType.custom)
        self.name = TexturesManager.textureLoaded
        self.textureID = textureID


class TexturesManager(BaseManager):
    textureLoaded = 'textureLoaded'

    def __init__(self):
        # ThreadedSystem.__init__(self)
        super(TexturesManager, self).__init__()
        self._textureCache = {}
        self._cubeTexCache = {}
        self._context = None
        self._window = None
        self._defaultTexture = None
        self._defaultNormalMap = None
        self._engine = None

    def initialize(self, engine, window_context):
        self._window, self._context = window_context
        self._engine = engine
        self.remotequeue = Queue()
        self.localqueue = Queue()
        # self.parallelProcess = Process(target=serve, args=[self.remotequeue, self.localqueue])
        # self.parallelProcess.start()

        dt = os.path.join(self._engine.path.defaults.textures, "default.png")
        dtnm = os.path.join(self._engine.path.defaults.textures, "default_nm.png")
        try:
            self.loadTexture(dt, "default", serial=True, raiseOnError=True)
            self._defaultTexture = self._textureCache.get('default')
            self.loadTexture(dtnm, "_defaultNM", serial=True, raiseOnError=True)
            self._defaultNormalMap = self._textureCache.get('_defaultNM')
        except Exception:
            raise

    def run(self):
        # if SDL_GL_MakeCurrent(self._window, self._context):
        #     raise RuntimeError(SDL_GetError())
        while self._running:
            sleep(1.5)
            self.checkQueue()

    def getDefaultNormalMap(self):
        return self._defaultNormalMap

    def checkQueue(self):
        # return
        try:
            if not self.localqueue._closed:
                # remoteID, ttype, taskID, args = self.localqueue.get(False, 1)
                remoteID, ttype, taskID, args = self.localqueue.get_nowait()
                if ttype == messageType.ready:
                    self._fillTexture(args)
                elif ttype == messageType.exception:
                    raise RuntimeError(*args)
        except Empty:
            pass

    def createEmpty2DTexture(self, ID, mipmapsNumber, width, height,):
        self._engine.log('Using untested createEmpty2DTexture', logLevelsEnum.warning)
        self._engine.backend.createOGL2DTexture(ID, mipmapsNumber, None, width, height, GL_RGBA8, GL_RGBA)

    def _fillTexture(self, args):
        pix, w, h, mode1, mode2, ID, mipmapsNumber, repeat = args
        tex = -1
        try:
            tex = self._engine.backend.createOGL2DTexture(ID, mipmapsNumber, pix, w, h, mode1, mode2, repeat)
            self._textureCache[ID] = tex
        except Exception as ex:
            self._engine.log('Error loading texture \'{0}\':\n\t{1}\n'
                             'Using default texture.'.format(ID, str(ex)))
            if self._defaultTexture is None:
                raise
            self._textureCache[ID] = self._defaultTexture

        self._engine.postEvent(textureLoadedEvent(ID))

    def loadTexture(self, filePath, ID, mipmapsNumber=10, serial=True, raiseOnError=False, repeat=True, force=False):
        """
        Load texture 'filename' as 'ID'. If 'serial', loading will be done secuentially, so
        this function won't return until the load is finished.
        If 'raiseOnError' is True, any error will raise an Exception. Otherwise, the default
        texture will be returned.
        @param raiseOnError:
        @type raiseOnError:bool
        @type ID: str
        @type filePath: str
        @rtype : None
        @param filePath:
        @param ID:
        """
        warn('forcing serial texture load')
        filePath = os.path.abspath(filePath)
        tex = self._textureCache.get(ID)
        getdefault = False
        if tex is None or force:
            if not os.path.exists(filePath):
                defaultTexturesDir = os.path.join(self._engine.path, 'defaults', 'textures')
                filename = os.path.basename(filePath)
                defaultedpath = os.path.join(defaultTexturesDir, filename)
                if not os.path.exists(defaultedpath):
                    getdefault = True
                    if raiseOnError:
                        raise RuntimeError('File not Found', filePath)
                    else:
                        self._engine.log('Error loading texture \'{0}\'\n'
                                   '\tUsing default texture.'.format(filePath), logLevelsEnum.error)
                else:
                    self._engine.log('Error loading texture \'{0}\'\n'
                               '\tUsing texture found at: {1}'.format(filePath, defaultedpath), logLevelsEnum.error)
                    filePath = defaultedpath

            if not getdefault:
                if serial:
                    pix, w, h, mode1, mode2 = self._engine.backend.getPILpixels(filePath)
                    self._fillTexture([pix, w, h, mode1, mode2, ID, mipmapsNumber, repeat])
                else:
                    self.remotequeue.put_nowait(('loadTexture', [filePath, ID, mipmapsNumber, repeat]))
            else:
                if self._defaultTexture is None:
                    raise AttributeError("Fatal error: Default texture not defined.")
                else:
                    tex = self._defaultTexture
                self._textureCache[ID] = tex

    def loadCubeTexture(self, folderPath, ID):
        """

        @type ID: str
        @type folderPath: str
        @rtype : None
        @param ID:
        """
        # TODO: turn into parallel
        cube = self._cubeTexCache.get(ID)
        if not cube:
            if not os.path.exists(folderPath):
            #     folderPath = self._engine.io.findPath(folderPath)
            # if not folderPath:
                self._engine.log('Error loading cube texture {0}:\n{1}'.format(folderPath, 'Folder not found.'), logLevelsEnum.error)

            cube = CubeTexture(self._engine, ID)
            cube.loadFromFolder(folderPath, self._engine.backend.getPILpixels)

        return cube

    def exists(self, texID):
        return texID in self._textureCache

    def existsCube(self, cubeID):
        return cubeID in self._cubeTexCache

    def getTexture(self, ID):
        return self._textureCache.get(ID, self._defaultTexture)

    def getCubeTexture(self, ID):
        return self._cubeTexCache.get(ID)

    def _addTextureIDs(self, IDs):
        for a, b in IDs:
            if a not in self._textureCache.keys():
                self._textureCache[a] = b
            else:
                raise AttributeError('Texture ID \'{}\' already exist.'.format(a))

    def getDefaultTexture(self):
        return self._defaultTexture

    def terminate(self):
        try:
            pass
            # self.remotequeue.put_nowait(('close', []))
            # self.remotequeue.close()
        except BrokenPipeError:
            pass

        # self.parallelProcess.terminate()

        # TODO: Move following code to backend
        # glBindTexture(GL_TEXTURE_2D, 0)
        # for t in self._textureCache.values():
        #
        #     glDeleteTextures(1, np.array([t], np.int32))
        #
        # for t in self._cubeTexCache.values():
        #     glDeleteTextures(1, np.array([t], np.int32))
        #
        # # SDL_GL_DeleteContext(self._context)
