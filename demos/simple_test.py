from _do_import import resolve_import

resolve_import()

from e3d.engine import Engine
from e3d.backends import OGL3Backend
from e3d.cameras import SimpleCamera
from cycgkit.cgtypes import vec3

import os

from random import randint as ri, random as rf


class game:
    planepath = os.path.join(os.path.dirname(__file__), os.pardir, "e3d", "defaults", "primitives", "plane.x")
    duckMODEL = os.path.join(os.path.dirname(__file__), "models", "duck", "duck.3DS")
    # duckMODEL = os.path.join(os.path.dirname(__file__), "models", 'dragon.obj')
    dragonModel = os.path.join(os.path.dirname(__file__), "models", 'dragon.obj')
    dwarfMODEL = os.path.join(os.path.dirname(__file__), "models", 'dwarf', "dwarf.x")
    tubeMODEL = os.path.join(os.path.dirname(__file__), "models", 'first_bone.x')

    camera = None

    def __init__(self, title):
        self.onelayer = None
        self.plane = None
        self.dlight = None
        self.lastspeed = 0
        nsize = [640, 480]

        self.engine = Engine(OGL3Backend, multiSampleLevel=16, maxContext=[2, 1])
        self.engine.initialize()

        # Create the Engendro3D.Window
        self.window = self.engine.createWindow(title, size=nsize, vSynch=True)
        self.window.onKeyEvent = self.keydown
        self.window.onMouseEvent = self.mouseMove

        self.scene1 = None
        self.camera = SimpleCamera(vec3(0, 30, 200), vec3(0, 180, 0), ID='maincam')

        # self.camera.rotateY(180)
        self.duck = None
        self.dorot = True
        self.camrot = 3
        self.quack = None

        self.window.FPS_UpdatedCallback = self.updateTitle

        self._started()

    def keydown(self, e):
        if e.eventName == 'keyUp':
            return
        # print "Key pressed=", e.keyName
        try:
            e.keyName = e.keyName.decode()
        except:
            pass
        if e.keyName.__contains__('shift'):
            self.window.mouseLock = not self.window.mouseLock
        if e.keyName == 'escape':  # ESC
            self.close()
        if e.keyName == 'l':
            for l in self.lights:
                l.rotation = vec3(ri(-200, 200), ri(-200, 200), ri(-380, 280))
                l.position = vec3(ri(-200, 200), ri(-200, 200), ri(-380, 280))
                l.type = ri(0, 1)
                l.color = vec3(ri(0, 1), ri(0, 1), ri(0, 1))
        # if e.keyName == 'left':
        #     self.dwarf.moveLeft(5)
        # if e.keyName == 'right':
        #     self.dwarf.moveRight(5)
        if e.keyName == 'space':
            self.window.setFullScreen(not self.window.isFullScreen())
        if e.keyName.__contains__('ctrl'):
            self.dorot = not self.dorot
        if e.keyName == 'f1':  # F1
            np = [round(d, 3) for d in self.camera.position]
            print('Camera pos:{0}'.format(str(np)))

    def mouseMove(self, ev):
        if ev.eventName == 'motion':
            if self.window.hasFocus():
                r = 1.0 / 10 if self.window.mouseLock else 1
                self.camera.rotateY(-ev.xRel * r)
                self.camera.rotateX(ev.yRel * r)

    def scene1Update(self, ev):
        ft = ev[0] + .01
        movespeed = ft / 10.0
        self.lastspeed = movespeed
        if self.dorot:
            self.lights[0].rotateZ(.1 * ft)
            # print ('sun rot', self.dlight.rotation)
            # print ('sun frw', self.dlight.forward)
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
            # self.window.backend.fullScreenEffects.addEffect('shaders/simple_override.fse', 'simpleFSE', 'simple')
            # self.window.backend.debugModeActive = True
            # engine.textures.loadTexture('e3dlogo.png', 'logo')
            # engine.textures.loadTexture('Grass.jpg', 'grass')

            engine.shaders.loadShader('normalsVS.glsl', 'normalsFS.glsl', 'normals')

            self.scene1 = engine.scenes.addScene('scene1')
            self.scene1.currentCamera = self.camera
            self.scene1.beforeUpdateCallback = self.scene1Update
            # self.scene1.setDefaultSkyBox()
            self.scene1.ambientColor = [v / 3.0 for v in [0.23, 0.34, 0.65]]
            # self.scene1.ambientColor = [.23, .34, .45]
            # self.dlight = self.scene1.addLight()
            # self.dlight.color = vec3(1.0, 1.0, .80)
            # self.dlight.rotation = vec3(45, 45, 0)

            # Random lights
            self.lights = []
            for i in range(8):
                l = self.scene1.addLight(ri(0, 1), rotation=vec3(ri(-200, 200), ri(-200, 200), ri(-380, 280)),
                                         ID='li' + str(i))
                l.color = vec3(ri(0, 1), ri(0, 1), ri(0, 1))
                l.position = vec3(ri(-200, 200), ri(-200, 200), ri(-380, 280))
                self.lights.append(l)
            # self.window.mouseLock = True

            # self.rlight = self.scene1.addLight(1)
            # self.rlight.color = vec3(1.0, .0, .0)
            # self.rlight.rotation = vec3(-5, 45, 50)

            engine.models.loadModel(self.duckMODEL, "duckmodel", forceStatic=True)
            self.duck = self.scene1.addModel('duckmodel', 'duck1', vec3(0, -20, 5), vec3(0), 1)
            mat = self.duck.getMaterialByIndex(0)
            mat.shaderID = 'normals'
            # mat.isLightAffected = False
            # mat.useDiffuseTexture = True
            quackpath = os.path.join(os.path.dirname(__file__), "sounds", "Duck.wav")
            engine.sounds.loadSound('quacksound', quackpath)
            # self.quack = self.duck.attachSound('quacksound', 'quack')
            # self.quack.volume = 60
            # self.quack.looped = True
            # self.quack.play()

            self.duck2 = self.scene1.addModel('duckmodel', 'duck2', vec3(-20, 30, -100), vec3(0), 1.7)
            # mat = self.duck2.getMaterialByIndex(0)
            # mat.shaderID = 'normals'
            # self.duck2._materials[0] = mat
            # engine.models.loadModel(self.dwarfMODEL, "dwarfmodel", preCalculateFrames=-1)
            # self.dwarf = self.scene1.addModel('dwarfmodel', 'dwarf1', vec3(0), vec3(0), 13)
            # self.dwarf._materials[0].specularPower = 50
            # self.dwarf._materials[1].specularPower = 50
            # self.dwarf.rotateY(180)
            # self.dwarf.moveRight(100)
            # self.dwarf.setAnimation(list(self.dwarf.getAnimationsList())[0], True)

            # engine.models.loadModel(self.tubeMODEL, "tubemodel")
            # self.tube = self.scene1.addModel('tubemodel', 'tube1', vec3(0), vec3(0), 7)
            # self.tube.setAnimation(list(self.tube.getAnimationsList())[0], True)
            # self.tube.moveRight(100)
            # self.tube._materials[0].opacity = .5

            # engine.models.loadModel(self.planepath, "planemodel")
            # self.plane = self.scene1.addModel('planemodel', 'floor', vec3(0), vec3(0), 20)
            # mat = self.plane.getMaterialByIndex(0)
            # mat.specularPower = 1000
            # mat.diffuseTextureID = 'grass'
            # mat.useDiffuseTexture = True
            # mat.textureRepeat = 60

        except Exception as ex:
            print('error in main.prepareScene: ' + str(ex))
            self.close()
            self.engine.terminate()
            raise

        # self.window.backend.showAsWireframe = True

        engine.scenes.currentSceneID = 'scene1'

    def buildGui(self):
        self.onelayer = self.window.gui.addLayer('one')
        logos = []
        pSize = [0.1, 0.1]
        fDis = 1.0 - pSize[0]
        manfred = self.engine.manfred
        logos.append(Panel(manfred, [0.0, 0.0], pSize, self.onelayer))
        logos.append(Panel(manfred, [fDis, 0.0], pSize, self.onelayer))
        logos.append(Panel(manfred, [0.0, fDis], pSize, self.onelayer))
        logos.append(Panel(manfred, [fDis, fDis], pSize, self.onelayer))
        for panel in logos:
            # panel.color = [1, 0, 1, .5]
            panel.backgroundImageID = 'logo'
            panel.opacity = .3


mainGame = game('Initializing... | Engendro3D OpenGL')
mainGame.engine.updateLoop()
mainGame.engine.terminate()
