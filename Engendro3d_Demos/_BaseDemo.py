import os
from math import sin

from cgkit.cgtypes import vec3

from e3d import Engine, __version__
from e3d.backends import OGL3Backend
from e3d.LoggerClass import logger, logLevelsEnum
from e3d.cameras.SimpleCameraClass import SimpleCamera
from e3d.gui import Panel
from e3d.events_processing.EventsManagerClass import EventsListener


GLOBAL_NAME = 'Engendro3D OpenGL {}'.format(__version__)


class game:
    maindir = os.path.dirname(__file__)
    planepath = os.path.join(maindir, "Engendro3D", "defaults", "primitives", "plane.x")
    duckMODEL = os.path.join(maindir, "models", "duck", "duck.3DS")
    dwarfMODEL = os.path.join(maindir, "models", 'dwarf', "dwarf.x")
    tubeMODEL = os.path.join(maindir, "models", 'first_bone.x')

    camera = None

    def __init__(self):
        self.camrot = 3
        self.quack = None
        self.dorot = True
        self.sphereMat = None
        self.duck = None
        self.scene0 = None
        self.scene1 = None
        self.spots = []
        self.onelayer = None
        self.plane = None
        self.dlight = None
        self.lastspeed = 0
        self.boxcount = 1
        self.ballcount = 0
        self.engine = Engine(OGL3Backend, multiSampleLevel=16, maxContext=[2, 1], )
        self.window = None
        self.firstRun = False
        self.pendingTex = 0
        self.isWaitingTex = False

    def run(self, title):
        # Initialize the Engine
        self.engine.initialize()

        nsize = [640, 480]
        # Create the Engendro3D.Window
        self.window = self.engine.createWindow(title, size=nsize, iconPath='Engendro3D/defaults/e3dlogo.png')

        self.camera = SimpleCamera([0, 0, 0], [0, 180, 0])

        self.window.FPS_UpdatedCallback = self.updateTitle

        self.window.firstRunCallback = self.onFirstRun
        self.engine.updateLoop()

    def onFirstRun(self, e):
        print('First Run')
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
            self._loadModels()
            self.window.onKeyEvent = self.keydown
            self.window.onMouseEvent = self.mouseMove
            self.scene0.beforeUpdateCallback = None

    def keydown(self, e):
        if e.name == 'keyUp':
            return
        # print "Key pressed=", e.keyName
        if e.keyName.__contains__('shift'):
            self.window.mouseLock = not self.window.mouseLock
        if e.keyName == 'escape':  # ESC
            self.close()
        if e.keyName == 'f8':
            self.window.renderingMan.debugModeActive = not self.window.renderingMan.debugModeActive
        if e.keyName == 'f4':
            self.window.renderingMan.showAsWireframe = not self.window.renderingMan.showAsWireframe
        if e.keyName == 'space':
            self.window.setFullScreen(not self.window.isFullScreen())
        if e.keyName.__contains__('ctrl'):
            self.dorot = not self.dorot
        if e.keyName == 'f1':
            np = [round(d, 3) for d in self.camera.position]
            logger.log('Camera pos:{0}'.format(str(np)), logLevelsEnum.info)
            logger.log('Poligons drawn:{}'.format(self.window.renderingMan.poligonsDrawnThisUpdate),
                       logLevelsEnum.info)
            logger.log('Boxes: ' + str(self.boxcount), logLevelsEnum.debug)
            logger.log('Balls: ' + str(self.ballcount), logLevelsEnum.debug)
        if e.keyName == 'g':
            val = self.window.gamma
            print ('old gamma:' + str(val))
            if val <= 1.8:
                self.window.gamma = 2.5
            else:
                self.window.gamma = 1.7
            print ('new gamma:' + str(self.window.gamma))
        if e.keyName == 'right':
            self.scene1.physics.step(50)
        if e.keyName == 'left':
            self.scene1.physics.paused = False
        if e.keyName == 'p':
            self.box1.physicsBody.punchCenter(250, [1, .5, 0])
        if e.keyName == 'l':
            self.dlight.enabled = not self.dlight.enabled
        if e.keyName == 'n':
            for mat in self.bumpymats:
                mat.useNormalMapTexture = not mat.useNormalMapTexture
        if e.keyName == 't':
            for mat in self.texmats:
                mat.useDiffuseTexture = not mat.useDiffuseTexture

    def mouseMove(self, ev):
        if ev.name == 'motion':
            if self.window.hasFocus():
                r = 1.0 / 10 if self.window.mouseLock else 1
                self.camera.rotateY(-ev.xRel * r)
                self.camera.rotateX(ev.yRel * r)
        elif ev.name == 'buttonDown':
            if ev.button == 'right':
                self.dropBox()
            elif ev.button == 'left':
                self.dropBall()
                # else:
                #     print ev

    def dropBox(self):
        try:
            self.boxcount += 1
            sceneid = 'box' + str(self.boxcount)
            pos = list(self.camera.position)
            pos[1] += 20
            box = self.scene1.addModel('boxmodel', sceneid, pos, [0, 0, 0], 1)
            mats = box._materials[0]
            mats.specularPower = 20
            # mats.useDiffuseTexture = True
            mats.diffuseColor = box.debugColor
            box.physicsBody.isDynamic = True
            box.physicsBody.punchCenter(250, self.camera.forward)
        except Exception as ex:
            print(ex.message)

    def dropBall(self):
        try:
            sceneid = 'ball' + str(self.ballcount)
            pos = list(self.camera.position)
            pos[1] += 20
            ball = self.scene1.addModel('spheremodel', sceneid, pos, [0, 0, 0], 1)
            mat = ball._materials[0]
            mat.specularPower = 50
            mat.useDiffuseTexture = True
            mat.diffuseTextureID = 'earth'
            ball.physicsBody.isDynamic = True
            ball.physicsBody.punchCenter(250, self.camera.forward)
            self.ballcount += 1
        except Exception as ex:
            print(ex.message)

    def scene1Update(self, ev):
        ft = ev[0] + .01
        movespeed = ft / 10.0
        # npos = list(self.camera._position)
        # npos[1] -= 100000000
        npos = self.camera.forward
        npos[2] *= 100000000
        # res = self.scene1.physics.castRay(self.camera._position, npos)
        # if res:
        #     print (res.physicsObject._base3DObject.ID, res.hitPosition)
        self.lastspeed = movespeed

        ran1 = 45 * sin(ev[1] / 1000.0)
        ran2 = 45 * sin(ev[1] / 500.0)
        for s in self.spots:
            s.rotation = vec3(ran2, 0, ran1)
        if self.dorot:
            if self.pushbox1:
                self.pushbox1.rotateY(-.07 * ft)
                self.pushbox2.rotateY(-.07 * ft)
                # self.box1.rotateY(-.07 * ft)
        if self.window.events.isKeyPressed('w'):
            self.camera.moveForward(movespeed)
        elif self.window.events.isKeyPressed('s'):
            self.camera.moveBackward(movespeed)

        if self.window.events.isKeyPressed('a'):
            self.camera.moveLeft(movespeed)
        elif self.window.events.isKeyPressed('d'):
            self.camera.moveRight(movespeed)

        if self.window.events.isKeyPressed('up'):
            self.camera.moveUp(movespeed)
        elif self.window.events.isKeyPressed('down'):
            self.camera.moveDown(movespeed)

    def updateTitle(self, ev):
        self.window.title = "FPS: {0} | Frame: {1} | {2}".format(ev[0], ev[1], self.gameName)

    def close(self):
        self.window.close()

    def loadTextures(self):
        def loadTexture(*args, **kwargs):
            print('<< Loading texture:', args[1])
            # self.pendingTex += 1
            # self.isWaitingTex = True
            self.engine.textures.loadTexture(args[0], args[1], **kwargs)

        logger.log('Loading Textures.', logLevelsEnum.warning)
        loadTexture('e3dlogo.png', 'logo')
        # loadTexture('Grass.jpg', 'grass')
        # loadTexture('defaults/default_n.png', 'defN')
        loadTexture('./textures/n_deep.png', 'defND', raiseOnError=True)
        loadTexture('./textures/n_irr.png', 'defNI', raiseOnError=True)
        loadTexture('./textures/nmap_test.png', 'testN', raiseOnError=True)
        loadTexture('./textures/earth_nasa_brighter.jpg', 'earth')

    def _loadModels(self):
        self.bumpymats = []
        self.texmats = []
        engine = self.engine
        try:
            self.scene1 = engine.scenes.addScene('scene1')
            self.scene1.currentCamera = self.camera
            self.scene1.beforeUpdateCallback = self.scene1Update
            # self.scene1.ambientColor = vec3(.05, .08, .1)
            self.scene1.ambientColor = vec3(.0, .0, .0)

            engine.models.loadSphere("mainspheremodel", 32)
            self.sphere1 = self.scene1.addModel('mainspheremodel', 'sphere1', [0, 10, 0], [0, 0, 0], 4, mass=8)
            self.sphere1.physicsBody.isDynamic = True
            mats = self.sphere1.getMaterialByIndex(0)
            mats.specularPower = 50
            mats.useDiffuseTexture = True
            mats.useNormalMapTexture = True
            mats.normalMapTextureID = 'defND'
            mats.textureRepeat = 4
            self.sphereMat = mats
            self.bumpymats.append(mats)
            self.texmats.append(mats)

            engine.models.loadSphere("spheremodel", 12)

            engine.models.loadBox("boxmodel", [6], 1)
            self.box1 = self.scene1.addModel('boxmodel', 'box1', [0, 90, 0], [0, 90, 0], 5, mass=7)
            self.box1.physicsBody.isDynamic = True
            mt = self.box1._materials[0]
            mt.specularPower = 40
            mt.useDiffuseTexture = True
            mt.useNormalMapTexture = True
            mt.normalMapTextureID = 'defNI'
            self.bumpymats.append(mt)
            self.texmats.append(mt)

            engine.models.loadBox("pushboxmodel", [55, 3, 3], 2)
            self.pushbox1 = self.scene1.addModel('pushboxmodel', 'pushbox1', [140, 6, 0], [0, 0, 0], 4, mass=50)
            self.pushbox2 = self.scene1.addModel('pushboxmodel', 'pushbox2', [-140, 6, 0], [0, 0, 0], 4, mass=50)

            engine.models.loadPlane("planemodelbig", 1, 15)
            engine.models.loadPlane("planemodel1", 1, 5)
            # IMPORTANT!: High number of segments (tesselation) is needed for large objects. See:
            # https://www.opengl.org/archives/resources/features/KilgardTechniques/oglpitfall/
            # 2. Poor Tessellation Hurts Lighting
            self.plane1 = self.scene1.addModel('planemodelbig', 'plane1', [0, 0, 0], [-90, 0, 0], 1200)
            mt = self.plane1._materials[0]
            mt.specularPower = 50
            mt.useDiffuseTexture = True
            mt.useNormalMapTexture = True
            mt.normalMapTextureID = 'defNI'
            mt.textureRepeat = 40
            self.bumpymats.append(mt)
            self.texmats.append(mt)

            self.planer = self.scene1.addModel('planemodel1', 'planer', [300, 0, 0], [0, -80, 0], 280)
            mt = self.planer._materials[0]
            self.planer.moveUp(self.planer.getSize().y)
            mt.useNormalMapTexture = True
            mt.normalMapTextureID = 'testN'
            mt.textureRepeat = 10
            self.bumpymats.append(mt)

            self.planel = self.scene1.addModel('planemodel1', 'planel', [-300, 0, 0], [0, 80, 0], 280)
            self.planel.moveUp(self.planer.getSize().y)
            self.planel._materials[0] = mt

            self.planef = self.scene1.addModel('planemodel1', 'planef', [0, 0, -200], [0, 0, 0], 280)
            self.planef.moveUp(self.planer.getSize().y)
            self.planef._materials[0] = mt

            engine.models.loadModel(self.tubeMODEL, "tubemodel")

            # self.tube = self.scene1.addModel('tubemodel', 'tube1', [-150, 20, 0], [0, 0, 0], 7)
            # self.tube.setAnimation(self.tube.getAnimationsList()[0], True)
            # self.tube.physicsBody.isDynamic = True

            # self.tube2 = self.scene1.addModel('tubemodel', 'tube2', [0, 70, 0], [0, 0, 0], 7,
            # shape=bodyShapesEnum.box)
            # self.tube2.physicsBody.isDynamic = True
            #
            # self.tube3 = self.scene1.addModel('tubemodel', 'tube3', [50, 0, 0], [0, 0, 0], 7,
            # shape=bodyShapesEnum.sphere)
            # self.tube3.setAnimation(self.tube3.getAnimationsList()[1], True)
            # self.tube3.physicsBody.isDynamic = True

            # engine.models.loadModel(self.planepath, "planemodel")
            # self.plane = self.scene1.addModel('planemodel', 'plane0', [0, 0, 0], [1, 0, 1], 2)
            # # self.plane.visible = False
            # mat = self.plane.getMaterialByIndex(0)
            # mat.specularPower = 20000000000
            # # mat.diffuseTextureID = 'grass'
            # mat.useDiffuseTexture = True
            # mat.textureRepeat = self.plane.uniformScale * 3

            self.addLights()

        except Exception as ex:
            print('error in main._loadModels: {}'.format(str(ex)))
            raise

        self.camera.position = [0, 10, 230]

        # self.window.renderingMan.showAsWireframe = True
        print('Switch scene 0 >> 1')
        engine.scenes.setCurrentSceneID('scene1')

    def addLights(self):
        print('Adding Lights')
        self.dlight = self.scene1.addLight(0, vec3(1.0, 1.0, 1.0), vec3(45, 45, 0))
        self.dlight.color = vec3(.9, .9, 0.7)
        self.createLightSphere(2, vec3(-190.0, 110.0, 0.0), vec3(1.0, 0.0, 0.0))
        self.createLightSphere(2, vec3(0.0, 70.0, -150.0), vec3(1.0, 1.0, 0.0))
        self.createLightSphere(1, vec3(-50.0, 30.0, 290.0), vec3(0.0, 1.0, 0.0))
        self.createLightSphere(2, vec3(0.0, 150.0, 0.0), vec3(.50, .0, 1.0))
        self.createLightSphere(1, vec3(280.0, 30.0, 10.0), vec3(0.0, .0, 1.0))

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

    def buildGui(self):
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