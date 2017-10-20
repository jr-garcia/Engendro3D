import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logging.getLogger('PIL').setLevel(logging.ERROR)
from cycgkit.cgtypes import vec3

from _do_import import resolve_import
resolve_import()

from _base._model_paths import *

from e3d import Engine, __version__, logLevelsEnum
from e3d.backends import OGL3Backend
from e3d.cameras.SimpleCameraClass import SimpleCamera
from e3d.events_processing.EventsManagerClass import EventsListener
from e3d.gui import Panel, PinningEnum

GLOBAL_NAME = 'Engendro3D OpenGL {}'.format(__version__)
LOGOSSIZE = 60


class _Demo_Base(object):

    camera = None

    def __init__(self, winSize=(640, 480)):
        self._winSize = winSize
        self.camrot = 3
        self.dorot = True
        self.sphereMat = None
        self.scene0 = None
        self.scene1 = None
        self.onelayer = None
        self.plane = None
        self.dlight = None
        self.lastspeed = 0
        self.engine = Engine(OGL3Backend, multiSampleLevel=16, maxContext=[2, 1])
        self.window = None
        self.firstRun = False
        self.pendingTex = 0
        self.isWaitingTex = False
        self.texturesToLoad = []

    def run(self, title):
        # Initialize the Engine
        self.engine.initialize()

        # Create the Engendro3D.Window
        self.window = self.engine.createWindow(title, size=self._winSize)

        self.camera = SimpleCamera([0, 0, 0], [0, 180, 0])

        self.window.FPS_UpdatedCallback = self.updateTitle

        self.window.firstRunCallback = self.onFirstRun

        self.loadTextures()
        self.scene0 = self.engine.scenes.addScene('scene0')
        self.scene0.beforeUpdateCallback = self.defUpdate
        self.scene0.ambientColor = vec3(.2, .0, .05)
        self.engine.scenes.currentSceneID = 'scene0'
        self.engine.updateLoop()

    def onFirstRun(self, e):
        listener = EventsListener()
        listener.onCustomEvent = self.customEvent
        self.window.events.addListener('main', listener)

    def defUpdate(self, e):
        if self.pendingTex == 0:
            self.engine.log('All Textures Loaded.')
            self.prepareScene()
            self.loadModels()
            self.addLights()
            self.buildGui()
            self.window.onKeyEvent = self.keydown
            self.window.onMouseEvent = self.mouseMove
            self.scene0.beforeUpdateCallback = None

    def keydown(self, e):
        pass

    def mouseMove(self, ev):
        pass

    def addLights(self):
        self.dlight = self.scene1.addLight(0, vec3(100000.0, 10000.0, 100000.0), vec3(45, 45, 0))
        self.dlight.color = vec3(.9, .9, 0.7)

    def updateTitle(self, ev):
        self.window.title = "FPS: {0} | Frame: {1} | {2}".format(ev[0], ev[1], self.gameName)

    def close(self):
        self.window.close()

    def loadTextures(self):
        def loadTexture(*args):
            args = args[0]
            if len(args) == 2:
                args.append(False)
            print('<< Loading texture: ' + args[1])
            # self.pendingTex += 1
            # self.isWaitingTex = True
            self.engine.textures.loadTexture(args[0], args[1], args[2])

        texCount = len(self.texturesToLoad)
        if texCount > 0:
            self.engine.log('Loading {} Textures.'.format(texCount), logLevelsEnum.info)
            list(map(loadTexture, self.texturesToLoad))

    def prepareScene(self):
        engine = self.engine
        try:
            self.scene1 = engine.scenes.addScene('scene1')
            self.scene1.currentCamera = self.camera
            self.scene1.beforeUpdateCallback = self.scene1Update
            self.scene1.ambientColor = vec3(.04, .06, .09)

        except Exception as ex:
            print('error in main.prepareScene: {}'.format(str(ex)))
            raise

        self.camera.position = [0, 10, 230]

        self.engine.log('Switch scene 0 >> 1', logLevelsEnum.debug)
        engine.scenes.setCurrentSceneID('scene1')

    def loadModels(self):
        pass

    def scene1Update(self, ev):
        pass

    def buildGui(self):
        if not self.window.gui.hasLayerID('one'):
            self.onelayer = self.window.gui.addLayer('one')
        self._addCornerLogos()

    def _addCornerLogos(self):
        w, h = self.window.size
        
        logos = []

        rightBorder = w - LOGOSSIZE
        bottomBorder = h - LOGOSSIZE
        
        logos.append(Panel(0, 0, LOGOSSIZE, LOGOSSIZE, self.onelayer))
        logos.append(Panel(rightBorder, 0, LOGOSSIZE, LOGOSSIZE, self.onelayer, PinningEnum.TopRight))
        logos.append(Panel(0, bottomBorder, LOGOSSIZE, LOGOSSIZE, self.onelayer, PinningEnum.BottomLeft))
        logos.append(Panel(rightBorder, bottomBorder, LOGOSSIZE, LOGOSSIZE, self.onelayer, PinningEnum.BottomRight))
        for panel in logos:
            panel.color = 0
            panel.borderSize = 0
            panel.backgroundImageID = 'logo'
            panel.opacity = .4

    def customEvent(self, e):
        if e.name == self.engine.textures.textureLoaded and self.isWaitingTex:
            self.textLoadedCallback(e)

    def textLoadedCallback(self, ev):
        self.pendingTex -= 1
        self._engine.log('Texture \'{}\' Loaded.'.format(ev.textureID), logLevelsEnum.warning)
        if self.pendingTex == 0:
            self.isWaitingTex = False


def runDemo(mainGame, title):
    try:
        title = title + ' | ' + GLOBAL_NAME
        mainGame.gameName = title
        mainGame.run('Initializing... | {}'.format(title))
    except Exception as ex:
        print('Fatal error in main: ' + str(ex))
        raise
    finally:
        mainGame.engine.terminate()
