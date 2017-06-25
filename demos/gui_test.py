from _do_import import resolve_import

resolve_import()

from e3d.engine import Engine, logLevelsEnum
from e3d.backends import OGL3Backend
from e3d.cameras import SimpleCamera
from e3d.gui import *

from cycgkit.cgtypes import *
from random import randint as ri, random as rf

import _model_paths
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

        self.triangle = None
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
                self.label2.borderSize = min(20, self.label2.borderSize + 1)
            elif e.keyName == 'down':
                self.label2.borderSize = max(0, self.label2.borderSize - 1)
            if e.keyName == 'backspace':
                self.label3.text = self.label3.text[:len(self.label3.text) - 1]
                return
            try:
                if chr(e.keyCode).isprintable():
                    self.label3.text += chr(e.keyCode)
            except ValueError:
                pass
            return
        if e.keyName.__contains__('shift'):
            self.label1.fontID = 'auto'
            self.label2.fontID = 'auto'
        if e.keyName == 'escape':  # ESC
            self.close()
        if e.keyName.__contains__('alt'):
            self.window.setFullScreen(not self.window.isFullScreen())
        if e.keyName.__contains__('ctrl'):
            self.label1.fontID = 'default'
            self.label2.fontID = 'default'
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
            if self.triangle:
                self.triangle.rotateY(.1 * ft)
            if self.triangle2:
                self.triangle2.rotateY(-.1 * ft / 2.0)

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

            engine.models.loadModel(_model_paths.triangleMODEL, "trianglemodel", forceStatic=True)
            self.triangle = self.scene1.addModel('trianglemodel', 'triangle1', vec3(0, 5, 5), vec3(0), 1.5)
            mat = self.triangle.getMaterialByIndex(0)
            mat.useDiffuseTexture = True

        except Exception as ex:
            print('error in main.prepareScene: ' + str(ex))
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

        self.char = SingleChar([.12, .12], [.6, .6], '?', self.onelayer)
        self.char.fontBorderColor = vec4(1, 0, 0, 1)
        self.char.fontBorder = 0.1
        self.char.fontWeight = .5

        self.label1 = Label([.02, .09], [.8, .08], 'Gui needs a lot of work.', parent=textLayer,
                            fontID='default')
        self.label2 = Label([.05, .4], [.8, .2], '%#@%^%(*)!', parent=textLayer, fontID='auto',
                            fontColor=[.5, .5,0, .8], fontBorder=.01, fontBorderColor=[0, 1, 0, 1])

        self.label3 = Label([.02, .8], [.97, .05], 'Press CTRL, SHIFT, UP, DOWN or resize the window', textLayer)

        self.label1.color = [1, 0, 0, 1]
        self.label2.color = [0, 1, 0, .5]
        self.label2.borderSize = 3
        self.label2.borderColor = vec4(1)


mainGame = game('Initializing... | Engendro3D OpenGL')
mainGame.engine.updateLoop()
mainGame.engine.terminate()
