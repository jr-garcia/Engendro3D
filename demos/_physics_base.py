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
        
    def loadModels(self):
        engine = self.engine

        self.scene1.ambientColor = vec3(.004, .006, .009)
        self.scene1.bgColor = vec3(.04, .06, .09)
        # self.camera.rotateX(30)
        # self.camera.rotateY(30)
        self.camera.position = vec3(0, 90, 350)
        
        engine.models.loadSphere("bigspheremodel", 32, radius=1)
        engine.models.loadSphere("spheremodel", 12)
        engine.models.loadBox("boxmodel", [6], 1)
        engine.models.loadBox("pushboxmodel", [50, 10, 10], 1)
        engine.models.loadPlane("floorplane", 1,1,2,2)
        engine.models.loadPlane("planemodelWalls", 600, 300, 20)

        engine.models.loadModel(tubeMODEL, "tubemodel")

        self.ballcount = 0
        self.boxcount = 1

    def dropBox(self):
        try:
            self.boxcount += 1
            sceneid = 'box' + str(self.boxcount)
            pos = list(self.camera.position)
            pos[1] += 20
            box = self.scene1.addModel('boxmodel', sceneid, pos, [0, 0, 0], 1)
            mats = box._materials[0]
            mats.specularPower = 20
            mats.diffuseColor = box.debugColor
            box.physicsBody.isDynamic = True
            box.physicsBody.punchCenter(250, self.camera.forward)
        except Exception as ex:
            print(str(ex))

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
            print(str(ex))

    def mouseMove(self, ev):
        if ev.eventName == 'motion':
            if self.window.hasFocus():
                r = 1.0 / 10 if self.window.mouseLock else 1
                self.camera.rotateY(-ev.xRel * r)
                self.camera.rotateX(ev.yRel * r)
        elif ev.eventName == 'buttonDown':
            if ev.button == 'right':
                self.dropBox()
            elif ev.button == 'left':
                self.dropBall()
                # else:
                #     print ev

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

    def scene1Update(self, ev):
        ft = ev[0] + .01
        movespeed = ft / 10.0

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
