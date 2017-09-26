from math import sin

from cycgkit.cgtypes import vec3

from Demos._base._BaseDemo import _Demo_Base, runDemo


class Demo(_Demo_Base):
    def __init__(self):
        _Demo_Base.__init__(self)
        self.texturesToLoad = [
            ['./textures/earth_nasa_brighter.jpg', 'earth']]  # TODO: credit textures or replace them

    def loadModels(self):
        engine = self.engine
        self.camera.position = vec3(0, 0, 80)

        engine.models.loadSphere("spheremodel", segmentsU=32)
        self.sphere1 = self.scene1.addModel('spheremodel', 'sphere1', [0, 0, 0], [0, 0, 0], 4)
        mats = self.sphere1.getMaterialByIndex(0)
        mats.specularPower = 50
        mats.diffuseTextureID = 'earth'
        mats.useDiffuseTexture = True
        # mats.setDefaultNormalMap()
        mats.textureRepeat = (1, 2)

    def prepareScene(self):
        super(Demo, self).prepareScene()
        self.engine.plugins.addPlugin('simple', './plugins/SimplePlugin.epf')

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
    from e3d.plugin_management.PluginHandlers import PluginDescription, packPluginFromFolder

    desc = PluginDescription('Simple Plugin', 'Simple plugin that creates a label',
                             'JR-García', 'some@example.com')

    pluginFolderPath = './plugins/SimplePlugin'
    desc.saveToDisk(pluginFolderPath)
    packPluginFromFolder(pluginFolderPath)

    runDemo(Demo(), 'Simple plugin demo')
