from math import sin

from cycgkit.cgtypes import vec3

from Demos._base._BaseDemo import _Demo_Base, dwarfMODEL, runDemo, tubeMODEL


class Demo(_Demo_Base):
    def __init__(self):
        super(Demo, self).__init__()
        self.texturesToLoad = [
            ['e3dlogo.png', 'logo']]

    def loadModels(self):
        engine = self.engine

        self.camera.position = vec3(0, 170, 290)
        self.camera.rotateX(20)

        engine.models.loadPlane("floorplane", 600, 600, 20)
        self.floor = self.scene1.addModel('floorplane', 'floor', [0, 0, 0], [0, 0, 0], 1)
        mt = self.floor._materials[0]
        mt.specularPower = 50
        mt.useDiffuseTexture = True
        mt.setDefaultNormalMap()
        mt.textureRepeat = 10

        engine.models.loadModel(tubeMODEL, "tubemodel")

        self.tube = self.scene1.addModel('tubemodel', 'tube1', [-120, 0, 0], [0, 0, 0], 7)
        self.tube.setAnimation(self.tube.getAnimationsList()[0], True)

        # self.tube2 = self.scene1.addModel('tubemodel', 'tube2', [0, 0, 0], [0, 0, 0], 7)

        self.tube3 = self.scene1.addModel('tubemodel', 'tube3', [120, 0, 0], [0, 0, 0], 7)
        self.tube3.setAnimation(self.tube3.getAnimationsList()[1], True)

        engine.models.loadModel(dwarfMODEL, 'dwarfmodel', preCalculateFrames=-1)
        self.dwarf = self.scene1.addModel('dwarfmodel', 'dwarf', vec3(0), vec3(0, 180, 0), 20)
        self.dwarf.setAnimation(self.dwarf.getAnimationsList()[0], True)

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
            self._engine.log('Camera pos:{0}'.format(str(np)), logLevelsEnum.info)
            self._engine.log('Poligons drawn:{}'.format(self.window.backend.poligonsDrawnThisUpdate),
                       logLevelsEnum.info)
        if keyName == 'g':
            val = self.window.gamma
            print ('old gamma:' + str(val))
            if val <= 1.8:
                self.window.gamma = 2.5
            else:
                self.window.gamma = 1.7
            print ('new gamma:' + str(self.window.gamma))
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
