from _BaseDemo import game, runDemo, tubeMODEL

from math import sin
from cycgkit.cgtypes import vec3
from e3d.LoggerClass import logger, logLevelsEnum


class Demo(game):
    def __init__(self):
        game.__init__(self)
        self.texturesToLoad = [
            ['e3dlogo.png', 'logo'],
            ['./textures/n_deep.png', 'defND', True],
            ['./textures/n_irr.png', 'defNI', True],
            ['./textures/nmap_test.png', 'testN', True],
            ['./textures/earth_nasa_brighter.jpg', 'earth']]  # TODO: credit textures or replace them

        self.bumpymats = []
        self.texmats = []
        self.spots = []

    def loadModels(self):
        engine = self.engine

        # self.camera.rotateX(25)
        # self.camera.rotateY(30)
        self.camera.position = vec3(0, 43, 186)

        # engine.models.loadBox("boxmodel", [6], 1)
        # self.box1 = self.scene1.addModel('boxmodel', 'box1', [0, 15, 0], [0, 0, 0], 5)
        # self.box1.physicsBody.isDynamic = True
        # mt = self.box1._materials[0]
        # mt.specularPower = 40
        # mt.useDiffuseTexture = True
        # mt.useNormalMapTexture = True
        # mt.normalMapTextureID = 'defNI'

        engine.models.loadPlane("planemodelbig", 600, 600, 20)
        self.plane1 = self.scene1.addModel('planemodelbig', 'plane1', [0, 0, 0], [0, 0, 0], 1)
        mt = self.plane1._materials[0]
        mt.specularPower = 50
        mt.useDiffuseTexture = True
        mt.useNormalMapTexture = True
        mt.normalMapTextureID = 'defNI'
        mt.textureRepeat = 40
        self.bumpymats.append(mt)
        self.texmats.append(mt)

        engine.models.loadModel(tubeMODEL, "tubemodel")

        self.tube = self.scene1.addModel('tubemodel', 'tube1', [-50, 0, 0], [0, 0, 0], 7)
        self.tube.setAnimation(list(self.tube.getAnimationsList())[0], True)
        # self.tube.physicsBody.isDynamic = True
        mt = self.tube._materials[0]
        mt.specularPower *= 4

        self.tube2 = self.scene1.addModel('tubemodel', 'tube2', [0, 0, 0], [0, 0, 0], 7)
        # self.tube2.physicsBody.isDynamic = True

        self.tube3 = self.scene1.addModel('tubemodel', 'tube3', [50, 0, 0], [0, 0, 0], 7)
        self.tube3.setAnimation(list(self.tube3.getAnimationsList())[1], True)
        # self.tube3.physicsBody.isDynamic = True

    def mouseMove(self, ev):
        if ev.eventName == 'motion':
            if self.window.hasFocus():
                r = 1.0 / 10 if self.window.mouseLock else 1
                self.camera.rotateY(-ev.xRel * r)
                self.camera.rotateX(ev.yRel * r)

    def keydown(self, e):
        if e.eventName == 'keyUp':
            return
        if e.keyName.__contains__('shift'):
            self.window.mouseLock = not self.window.mouseLock
        if e.keyName == 'escape':  # ESC
            self.close()
        if e.keyName == 'f8':
            self.window.backend.debugModeActive = not self.window.backend.debugModeActive
        if e.keyName == 'f4':
            self.window.backend.showAsWireframe = not self.window.backend.showAsWireframe
        if e.keyName == 'space':
            self.window.setFullScreen(not self.window.isFullScreen())
        if e.keyName.__contains__('ctrl'):
            self.dorot = not self.dorot
        if e.keyName == 'f1':
            np = [round(d, 3) for d in self.camera.position]
            logger.log('Camera pos:{0}'.format(str(np)), logLevelsEnum.info)
            logger.log('Poligons drawn:{}'.format(self.window.backend.poligonsDrawnThisUpdate),
                       logLevelsEnum.info)
        if e.keyName == 'g':
            val = self.window.gamma
            print ('old gamma:' + str(val))
            if val <= 1.8:
                self.window.gamma = 2.5
            else:
                self.window.gamma = 1.7
            print ('new gamma:' + str(self.window.gamma))
        if e.keyName == 'l':
            self.dlight.enabled = not self.dlight.enabled
        if e.keyName == 'n':
            for mat in self.bumpymats:
                mat.useNormalMapTexture = not mat.useNormalMapTexture
        if e.keyName == 't':
            for mat in self.texmats:
                mat.useDiffuseTexture = not mat.useDiffuseTexture

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
        self.scene1.ambientColor = vec3(.004, .006, .009)
        self.scene1.bgColor = vec3(.04, .06, .09)

        ran1 = 45 * sin(ev[1] / 1000.0)
        ran2 = 45 * sin(ev[1] / 500.0)
        for s in self.spots:
            s.rotation = vec3(ran2, 0, ran1)
        # if self.dorot:
            # if self.pushbox1:
            #     self.pushbox1.rotateY(-.07 * ft)
            #     self.pushbox2.rotateY(-.07 * ft)
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


if __name__ == '__main__':
    runDemo(Demo(), 'Physics Demo 1')