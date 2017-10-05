from math import sin
from random import randint, random

from cycgkit.cgtypes import vec3

from Demos._base._BaseDemo import _Demo_Base, runDemo, tubeMODEL, logLevelsEnum


class Demo(_Demo_Base):
    def __init__(self):
        super(Demo, self).__init__()
        self.texturesToLoad = [['e3dlogo.png', 'logo'], ['./textures/n_deep.png', 'defND', True],
            ['./textures/n_irr.png', 'defNI', True], ['./textures/nmap_test.png', 'testN', True],
            ['./textures/earth_nasa_brighter.jpg', 'earth']]  # TODO: credit textures or replace them

        self.bumpymats = []
        self.texmats = []
        self.spots = []
        self.spotAngles = {}

    def createLightSphere(self, ltype, pos, color):
        nlight = self.scene1.addLight(ltype, pos, vec3(0, 0, 0))
        nlight.color = color
        nlight.spotIntensity = random()  # .1
        nlight.spotRange = .9
        nlight.attenuation = randint(150, 300)

        if ltype == 2:
            self.spotAngles[nlight] = (randint(1, 30) - randint(10, 50)), (randint(1, 30) - randint(10, 50))
            lmod = self.scene1.addModel('conemodel', nlight.ID + 'sph', pos, [0, 0, 0], 1)
            self.spots.append((nlight, lmod))
        else:
            lmod = self.scene1.addModel('spheremodel', nlight.ID + 'sph', pos, [0, 0, 0], 1)
        mat = lmod._materials[0]
        mat.emissiveColor = color
        mat.isLightAffected = False

    def loadModels(self):
        engine = self.engine

        self.camera.rotateX(40)
        self.camera.position = vec3(0, 340, 350)

        engine.models.loadSphere("mainspheremodel", 32)
        self.sphere1 = self.scene1.addModel('mainspheremodel', 'sphere1', [0, 10, 0], [0, 0, 0], 4, mass=8)
        # self.sphere1.physicsBody.isDynamic = True
        mats = self.sphere1.getMaterialByIndex(0)
        mats.specularPower = 50
        mats.useDiffuseTexture = True
        mats.useNormalMapTexture = True
        mats.normalMapTextureID = 'defND'
        mats.textureRepeat = 4
        self.bumpymats.append(mats)
        self.texmats.append(mats)

        engine.models.loadSphere("spheremodel", 12)
        engine.models.loadCone("conemodel", 20, 10, radialSegments=20)

        engine.models.loadBox("boxmodel", [6], 1)
        self.box1 = self.scene1.addModel('boxmodel', 'box1', [0, 90, 0], [0, 90, 0], 5, mass=7)
        mt = self.box1._materials[0]
        mt.specularPower = 40
        mt.useDiffuseTexture = True
        mt.useNormalMapTexture = True
        mt.normalMapTextureID = 'defNI'
        self.bumpymats.append(mt)
        self.texmats.append(mt)

        engine.models.loadPlane("floorplane", 600, 600, 50)
        # engine.models.loadPlane("planemodelback", 600, 300, 10)
        engine.models.loadPlane("planemodelWalls", 600, 300, 50)
        # IMPORTANT!: High number of segments (tesselation) is needed for large objects. See:
        # https://www.opengl.org/archives/resources/features/KilgardTechniques/oglpitfall/
        # 2. Poor Tessellation Hurts Lighting
        self.floor = self.scene1.addModel('floorplane', 'floor', [0, 0, 0], [0, 0, 0], 1)
        mt = self.floor._materials[0]
        mt.specularPower = 50
        mt.useDiffuseTexture = True
        mt.useNormalMapTexture = True
        mt.normalMapTextureID = 'defNI'
        mt.textureRepeat = 10
        self.bumpymats.append(mt)
        self.texmats.append(mt)

        self.planer = self.scene1.addModel('planemodelWalls', 'planer', [300, 150, 0], [90, 0, 0], 1)
        self.planer.rotateY(-90)
        mt = self.planer._materials[0]
        mt.useNormalMapTexture = True
        mt.normalMapTextureID = 'testN'
        mt.textureRepeat = 10
        self.bumpymats.append(mt)

        self.planel = self.scene1.addModel('planemodelWalls', 'planel', [-300, 150, 0], [90, 0, 0], 1)
        self.planel.rotateY(90)
        self.planel._materials[0] = mt

        self.planef = self.scene1.addModel('planemodelWalls', 'planef', [0, 150, -300], [90, 0, 0], 1)
        self.planef.moveUp(self.planer.getSize().y)
        self.planef._materials[0] = mt

        engine.models.loadModel(tubeMODEL, "tubemodel")

        self.tube = self.scene1.addModel('tubemodel', 'tube1', [-150, 0, 0], [0, 0, 0], 9)
        self.tube.setAnimation(self.tube.getAnimationsList()[0], True)

        self.tube2 = self.scene1.addModel('tubemodel', 'tube2', [150, 0, 0], [0, 0, 0], 9)
        self.tube2.setAnimation(self.tube2.getAnimationsList()[1], True)

    def addLights(self):
        print('Adding Lights')
        super(Demo, self).addLights()
        self.dlight.enabled = False
        self.createLightSphere(2, vec3(-259.0, 120.0, 0.0), vec3(1.0, 0.0, 0.0))
        self.createLightSphere(2, vec3(0.0, 270.0, -190.0), vec3(1.0, 1.0, 0.0))
        self.createLightSphere(1, vec3(-50.0, 30.0, 290.0), vec3(0.0, 1.0, 0.0))
        self.createLightSphere(2, vec3(0.0, 150.0, 0.0), vec3(.50, .0, 1.0))
        self.createLightSphere(1, vec3(280.0, 30.0, 10.0), vec3(0.0, .0, 1.0))

    def mouseMove(self, ev):
        if ev.eventName == 'motion':
            if self.window.hasFocus():
                r = 1.0 / 10 if self.window.mouseLock else 1
                self.camera.rotateY(-ev.xRel * r)
                self.camera.rotateX(ev.yRel * r)

    def keydown(self, e):
        if e.eventName == 'keyUp':
            return
        keyName = e.keyName
        if 'shift' in keyName:
            self.window.mouseLock = not self.window.mouseLock
        if keyName == 'escape':  # ESC
            self.close()
        if keyName == 'f8':
            self.window.backend.debugModeActive = not self.window.backend.debugModeActive
        if keyName == 'f4':
            self.window.backend.showAsWireframe = not self.window.backend.showAsWireframe
        if keyName == 'space':
            self.window.setFullScreen(not self.window.isFullScreen())
        if keyName.__contains__('ctrl'):
            self.dorot = not self.dorot
        if keyName == 'f1':
            np = [round(d, 3) for d in self.camera.position]
            engine = self.engine
            engine.log('Camera pos:{0}'.format(str(np)), logLevelsEnum.info)
            engine.log('Poligons drawn:{}'.format(self.window.backend.poligonsDrawnThisUpdate), logLevelsEnum.info)
        if keyName == 'g':
            val = self.window.gamma
            print('old gamma:' + str(val))
            if val <= 1.8:
                self.window.gamma = 2.5
            else:
                self.window.gamma = 1.7
            print('new gamma:' + str(self.window.gamma))
        if keyName == 'l':
            self.dlight.enabled = not self.dlight.enabled
        if keyName == 'n':
            for mat in self.bumpymats:
                mat.useNormalMapTexture = not mat.useNormalMapTexture
        if keyName == 't':
            for mat in self.texmats:
                mat.useDiffuseTexture = not mat.useDiffuseTexture

    def scene1Update(self, ev):
        ft = ev[0] + .01
        movespeed = ft / 10.0
        self.scene1.ambientColor = vec3(.004, .006, .009)
        self.scene1.bgColor = vec3(.04, .06, .09)

        for s, m in self.spots:
            rotVec = vec3(self.spotAngles[s][0] * sin(ev[1] / 1000.0), 0, self.spotAngles[s][1] * sin(ev[1] / 500.0))
            s.rotation = rotVec
            m.rotation = rotVec
        if self.dorot:
            self.sphere1.rotateY(-.07 * ft)
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


if __name__ == '__main__':
    runDemo(Demo(), 'Light Demo')
