from _do_import import resolve_import

resolve_import()

from e3d.engine import Engine, logLevelsEnum
from e3d.backends import OGL3Backend
from e3d.cameras import SimpleCamera
from e3d.gui import *

from cycgkit.cgtypes import *
from random import randint as ri, random as rf

import model_paths
import os


class game:
    def __init__(self, title):
        self.label = None
        self.onelayer = None
        self.plane = None
        self.dlight = None
        self.lastspeed = 0
        self.char = None
        nsize = [640, 480]

        # Initialize the Engine
        self.engine = Engine(OGL3Backend, multiSampleLevel=16, maxContext=[2, 1], logLevel=logLevelsEnum.debug)
        self.engine.initialize()

        # Create the Engendro3D.Window
        self.window = self.engine.createWindow(title, size=nsize, vSynch=True)
        self.window.onKeyEvent = self.keydown
        # self.window.onMouseEvent = self.mouseMove

        self.scene1 = None
        self.camera = SimpleCamera(vec3(0, 30, 200), vec3(0, 180, 0), ID='maincam')

        # self.camera.rotateY(180)
        self.duck = None
        self.dorot = True
        self.camrot = 3
        self.quack = None

        self.window.FPS_UpdatedCallback = self.updateTitle

        self.buildGui()
        self._started()

    def keydown(self, e):
        try:
            e.keyName = e.keyName.decode()
        except:
            pass

        # if e.keyName == 'right':
        #     if self.char.fontWeight + .05 < 1:
        #         self.char.fontWeight += .05
        #         print(self.char.fontWeight)
        # elif e.keyName == 'left':
        #     if self.char.fontWeight - .05 > 0:
        #         self.char.fontWeight -= .05
        #         print(self.char.fontWeight)
        if e.eventName == 'keyDown':
            if e.keyName == 'up':
                self.label.borderSize = min(20, self.label.borderSize + 1)
            elif e.keyName == 'down':
                self.label.borderSize = max(0, self.label.borderSize - 1)
            if e.keyName == 'backspace':
                self.label.text = self.label.text[:len(self.label.text) - 1]
                return
            try:
                if chr(e.keyCode).isprintable():
                    self.label.text += chr(e.keyCode)
            except ValueError:
                pass
            return
        if e.keyName.__contains__('shift'):
            self.label.fontID = 'auto'
        if e.keyName == 'escape':  # ESC
            self.close()
        if e.keyName.__contains__('alt'):
            self.window.setFullScreen(not self.window.isFullScreen())
        if e.keyName.__contains__('ctrl'):
            self.label.fontID = 'default'
        if e.keyName == 'f1':  # F1
            np = [round(d, 3) for d in self.camera.position]
            print('Camera pos:{0}'.format(str(np)))

    def mouseMove(self, ev):
        if ev.name == 'motion':
            if self.window.hasFocus():
                r = 1.0 / 10 if self.window.mouseLock else 1
                self.camera.rotateY(-ev.xRel * r)
                self.camera.rotateX(ev.yRel * r)

    def scene1Update(self, ev):
        ft = ev[0] + .01
        movespeed = ft / 10.0
        self.lastspeed = movespeed
        if self.dorot:
            if self.duck:
                self.duck.rotateY(.1 * ft)
            if self.duck2:
                self.duck2.rotateY(-.1 * ft / 2.0)

        if self.window.events.isKeyPressed('w'):
            self.camera.moveForward(movespeed)
        elif self.window.events.isKeyPressed('s'):
            self.camera.moveBackward(movespeed)

        if self.window.events.isKeyPressed('a'):
            self.camera.moveLeft(movespeed)
        elif self.window.events.isKeyPressed('d'):
            self.camera.moveRight(movespeed)

    def updateTitle(self, ev):
        self.window.title = "FPS: {0} | Frame: {1} | Engendro3D OpenGL - Alpha 0.5".format(ev[0], ev[1])

    def close(self):
        self.window.close()

    def _started(self):
        try:
            engine = self.engine
            engine.textures.loadTexture('e3dlogo.png', 'logo')

            self.scene1 = engine.scenes.addScene('scene1')
            self.scene1.currentCamera = self.camera
            # self.scene1.beforeUpdateCallback = self.scene1Update

            engine.models.loadModel(model_paths.triangleMODEL, "duckmodel", forceStatic=True)
            self.duck = self.scene1.addModel('duckmodel', 'duck1', vec3(0, 5, 5), vec3(0), 1.5)
            mat = self.duck.getMaterialByIndex(0)
            # mat.shaderID = 'normals'
            # mat.isLightAffected = False
            mat.useDiffuseTexture = True
            # quackpath = os.path.join(os.path.dirname(__file__), "sounds", "Duck.wav")
            # engine.sounds.loadSound('quacksound', quackpath)
            # self.quack = self.duck.attachSound('quacksound', 'quack')
            # self.quack.volume = 60
            # self.quack.looped = True
            # self.quack.play()

        except Exception as ex:
            print('error in main._loadModels: ' + str(ex))
            self.close()
            self.engine.terminate()
            raise

        engine.scenes.currentSceneID = 'scene1'

    def buildGui(self):
        # load default font
        self.window.gui.loadFont('default', os.path.join(self.engine.path.defaults.fonts, 'code', 'Code200365k.ttf'),
                                 force=True, baseSize=34)

        self.window.gui.loadFont('auto', os.path.join('fonts', 'automati.ttf'), force=True)

        self.onelayer = self.window.gui.addLayer('one')

        textLayer = self.window.gui.addLayer('text')

        logos = []
        pSize = [0.14]
        fDis = 1.0 - pSize[0]
        logos.append(Panel([0.0, 0.0], pSize, self.onelayer))
        logos.append(Panel([fDis, 0.0], pSize, self.onelayer))
        logos.append(Panel([0.0, fDis], pSize, self.onelayer))
        logos.append(Panel([fDis, fDis], pSize, self.onelayer))
        for panel in logos:
            panel.color = [0, 0, 0, 0]
            panel.backgroundImageID = 'logo'
            panel.opacity = .7
            panel.borderSize = 0

        # self.char = SingleChar([.12, .12], .6, self.onelayer, '?')
        # self.char.fontBorderColor = vec4(1, 0, 0, 1)
        # self.char.fontBorder = 0.1
        # self.char.fontWeight = .5

        self.label = Label([.01, .09], [.4, .2], '%Help oqm0!', parent=textLayer, fontID='auto',
                           fontColor=[1, 1, 1, 1], fontBorder=.0, fontBorderColor=[0, 0, 0, 1])
        # self.label2 = Label([.0, .4], [.99, .2], '%Help oqm01', parent=textLayer, fontID='auto')
        self.label.color = [0, 0, 0, .5]
        # self.label2.color = [.5]


mainGame = game('Initializing... | Engendro3D OpenGL')
mainGame.engine.updateLoop()
mainGame.engine.terminate()
