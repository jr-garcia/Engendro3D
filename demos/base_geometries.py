from _BaseDemo import _Demo_Base, runDemo

from math import sin
from cycgkit.cgtypes import vec3


class Demo(_Demo_Base):
    def __init__(self):
        _Demo_Base.__init__(self)

    def loadModels(self):
        engine = self.engine
        self.camera.rotateX(30)
        self.camera.position = vec3(0, 100.051, 208.345)

        engine.models.loadSphere("spheremodel", segmentsU=32)
        self.sphere1 = self.scene1.addModel('spheremodel', 'sphere1', [40, 18, 60], [0, 0, 0], 4)
        mats = self.sphere1.getMaterialByIndex(0)
        mats.specularPower = 50
        mats.useDiffuseTexture = True
        mats.setDefaultNormalMap()
        mats.textureRepeat = 4

        engine.models.loadBox("boxmodel", [20], 2)
        self.box1 = self.scene1.addModel('boxmodel', 'box1', [-60, 11, 0], [0, 0, 0], 1)
        mt = self.box1._materials[0]
        mt.specularPower = 40
        mt.useDiffuseTexture = True
        mt.setDefaultNormalMap()
                                              # radius=100, tube=40, radialSegments=64, tubularSegments=8, p=2, q=3,
                                                # heightScale=1
        engine.models.loadTorusKnot("tkmodel1", 12, 3, 64, 32, 3, 4)
        engine.models.loadTorusKnot("tkmodel2", 12, 3, 64, 32, 3, 1)
        engine.models.loadTorusKnot("tkmodel3", 12, 3, 48, 16, 1, 3)
        engine.models.loadTorusKnot("tkmodel4", 12, 3, 48, 16)
        self.tk1 = self.scene1.addModel('tkmodel1', 'tk1', [-20, 25, 0], [0, 0, 0], 1)
        self.tk2 = self.scene1.addModel('tkmodel2', 'tk2', [20, 25, 0], [0, 0, 0], 1)
        self.tk3 = self.scene1.addModel('tkmodel3', 'tk3', [-80, 25, 60], [0, 0, 0], 1)
        self.tk4 = self.scene1.addModel('tkmodel4', 'tk4', [80, 25, -60], [0, 0, 0], 1)
        mt = self.tk1._materials[0]
        mt.specularPower = 40
        mt.useDiffuseTexture = True
        mt.setDefaultNormalMap()
        mt.textureRepeat = .5  # todo: Should the textureRepeat be non-uniform?
        self.tk2._materials[0] = mt
        self.tk3._materials[0] = mt
        self.tk4._materials[0] = mt

        engine.models.loadPlane("floorplane", 500, 500, 6)
        self.floor = self.scene1.addModel('floorplane', 'floor', [0, 0, 0], [0, 0, 0], 1)
        mt = self.floor._materials[0]
        # self.floor._materials[0]  =mt
        mt.specularPower = 50
        mt.useDiffuseTexture = True
        mt.setDefaultNormalMap()
        mt.textureRepeat = 80

        engine.models.loadCylinder("cylindermodel",radialSegments=10)
        self.cyli1 = self.scene1.addModel('cylindermodel', 'cyli1', [-20, 20, 70], [0, 0, 0], .4)
        mats = self.cyli1.getMaterialByIndex(0)
        mats.specularPower = 50
        mats.useDiffuseTexture = True

        engine.models.loadCone("conemodel", radialSegments=10)
        self.cone1 = self.scene1.addModel('conemodel', 'cone1', [-60, 20, 70], [0, 0, 0], .4)
        mats = self.cone1.getMaterialByIndex(0)
        mats.specularPower = 50
        mats.useDiffuseTexture = True

    def mouseMove(self, ev):
        if ev.eventName == 'motion':
            if self.window.hasFocus():
                r = 1.0 / 10 if self.window.mouseLock else 1
                self.camera.rotateY(-ev.xRel * r)
                self.camera.rotateX(ev.yRel * r)

    def keydown(self, e):
        if e.eventName == 'keyUp':
            return
        if 'shift' in e.keyName:
            self.window.mouseLock = not self.window.mouseLock
        if e.keyName == 'escape':  # ESC
            self.close()
        if e.keyName == 'f8':
            self.window.backend.debugModeActive = not self.window.backend.debugModeActive
        if e.keyName == 'f4':
            self.window.backend.showAsWireframe = not self.window.backend.showAsWireframe
        if e.keyName == 'space':
            self.window.setFullScreen(not self.window.isFullScreen())
        if 'ctrl' in e.keyName:
            self.dorot = not self.dorot
        if e.keyName == 'f1':
            np = [round(d, 3) for d in self.camera.position]
            self._engine.log('Camera pos:{0}'.format(str(np)), logLevelsEnum.debug)
            self._engine.log('Poligons drawn:{}'.format(self.window.backend.poligonsDrawnThisUpdate),
                       logLevelsEnum.debug)
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

    def scene1Update(self, ev):
        ft = ev[0] + .01
        movespeed = ft / 10.0
        npos = self.camera.forward
        npos[2] *= 100000000
        self.lastspeed = movespeed
        spherespeed = - .05
        ran1 = 45 * sin(ev[1] / 1000.0)
        ran2 = 45 * sin(ev[1] / 500.0)
        if self.dorot:
            if self.sphere1:
                self.sphere1.rotateY(spherespeed * ft)
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
    runDemo(Demo(), 'Basic geometries Demo')
