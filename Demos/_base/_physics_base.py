from cycgkit.cgtypes import vec3

from _base._BaseDemo import _Demo_Base, runDemo, tubeMODEL


class Demo(_Demo_Base):
    def __init__(self):
        super(Demo, self).__init__()
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
        engine.models.loadPlane("floorplane", 1,1,2,2)

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
            engine = self._engine
            engine.log('Camera pos:{0}'.format(str(np)), logLevelsEnum.info)
            engine.log('Poligons drawn:{}'.format(self.window.backend.poligonsDrawnThisUpdate),
                       logLevelsEnum.info)
            engine.log('Boxes: ' + str(self.boxcount), logLevelsEnum.debug)
            engine.log('Balls: ' + str(self.ballcount), logLevelsEnum.debug)
        if keyName == 'g':
            val = self.window.gamma
            print ('old gamma:' + str(val))
            if val <= 1.8:
                self.window.gamma = 2.5
            else:
                self.window.gamma = 1.7
            print ('new gamma:' + str(self.window.gamma))
        if keyName == 'right':
            self.scene1.physics.step(50)
        if keyName == 'left':
            self.scene1.physics.paused = False
        if keyName == 'p':
            self.box1.physicsBody.punchCenter(250, [1, .5, 0])
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
