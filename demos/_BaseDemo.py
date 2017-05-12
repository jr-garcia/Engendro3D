from cycgkit.cgtypes import vec3

from _do_import import resolve_import
resolve_import()

from e3d import Engine, __version__
from e3d.LoggerClass import logLevelsEnum, logger
from e3d.backends import OGL3Backend
from e3d.cameras.SimpleCameraClass import SimpleCamera
from e3d.events_processing.EventsManagerClass import EventsListener
from e3d.gui import Panel
from _model_paths import *

GLOBAL_NAME = 'Engendro3D OpenGL {}'.format(__version__)


class game:

    camera = None

    def __init__(self):
        self.camrot = 3
        self.dorot = True
        self.sphereMat = None
        self.scene0 = None
        self.scene1 = None
        self.onelayer = None
        self.plane = None
        self.dlight = None
        self.lastspeed = 0
        self.engine = Engine(OGL3Backend, multiSampleLevel=16, maxContext=[2, 1], )
        self.window = None
        self.firstRun = False
        self.pendingTex = 0
        self.isWaitingTex = False
        self.texturesToLoad = []

    def run(self, title):
        # Initialize the Engine
        self.engine.initialize()

        nsize = [640, 480]
        # Create the Engendro3D.Window
        self.window = self.engine.createWindow(title, size=nsize)

        self.camera = SimpleCamera([0, 0, 0], [0, 180, 0])

        self.window.FPS_UpdatedCallback = self.updateTitle

        self.window.firstRunCallback = self.onFirstRun
        self.engine.updateLoop()

    def onFirstRun(self, e):
        listener = EventsListener()
        listener.onCustomEvent = self.customEvent
        self.window.events.addListener('main', listener)
        self.scene0 = self.engine.scenes.addScene('scene0')
        self.scene0.beforeUpdateCallback = self.defUpdate
        self.scene0.ambientColor = vec3(.2, .0, .05)
        self.engine.scenes.currentSceneID = 'scene0'
        self.loadTextures()

    def defUpdate(self, e):
        if self.pendingTex == 0:
            logger.log('All Textures Loaded.', logLevelsEnum.warning)
            self.buildGui()
            self.prepareScene()
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
            print('<< Loading texture:' + args[1])
            # self.pendingTex += 1
            # self.isWaitingTex = True
            self.engine.textures.loadTexture(args[0], args[1], args[2])

        logger.log('Loading Textures.', logLevelsEnum.warning)
        map(loadTexture, self.texturesToLoad)

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

        print('Switch scene 0 >> 1')
        engine.scenes.setCurrentSceneID('scene1')
        self.addLights()
        self.loadModels()

    def loadModels(self):
        pass

    def createLightSphere(self, ltype, pos, color):
        nlight = self.scene1.addLight(ltype, pos, vec3(0, 0, 0))
        nlight.color = color
        nlight.spotIntensity = .1
        nlight.spotRange = .7
        nlight.attenuation = 250
        lmod = self.scene1.addModel('spheremodel', nlight.ID + 'sph', pos, [0, 0, 0], 1)
        ncol = list(color)
        ncol.append(1.0)
        mat = lmod._materials[0]
        mat.emissiveColor = ncol
        mat.isLightAffected = False
        if ltype == 2:
            self.spots.append(nlight)

    def scene1Update(self, ev):
        pass

    def buildGui(self):
        self._addCornerLogos()

    def _addCornerLogos(self):
        self.onelayer = self.window.gui.addLayer('one')
        logos = []
        pSize = [0.1, 0.1]
        fDis = 1.0 - pSize[0]
        logos.append(Panel([0.0, 0.0], pSize, self.onelayer))
        logos.append(Panel([fDis, 0.0], pSize, self.onelayer))
        logos.append(Panel([0.0, fDis], pSize, self.onelayer))
        logos.append(Panel([fDis, fDis], pSize, self.onelayer))
        for panel in logos:
            panel.backgroundImageID = 'logo'
            panel.opacity = .3

    def customEvent(self, e):
        if e.name == self.engine.textures.textureLoaded and self.isWaitingTex:
            self.textLoadedCallback(e)

    def textLoadedCallback(self, ev):
        self.pendingTex -= 1
        logger.log('Texture \'{}\' Loaded.'.format(ev.textureID), logLevelsEnum.warning)
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
