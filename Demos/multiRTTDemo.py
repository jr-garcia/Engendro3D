
from cycgkit.cgtypes import vec3

from Demos._base._BaseDemo import _Demo_Base, runDemo, LOGOSSIZE
from Demos._base._model_paths import *
from e3d.cameras import SimpleCamera
from e3d.gui import Panel


class Demo(_Demo_Base):
    camera = None

    def __init__(self):
        super(Demo, self).__init__()
        self.onelayer = None
        self.plane = None
        self.dlight = None
        self.lastspeed = 0
        self.duck = None
        self.duck2 = None
        self.dorot = True
        self.camrot = 3
        self.quack = None

    def keydown(self, e):
        if e.eventName == 'keyUp':
            return
        try:
            e.keyName = e.keyName.decode()
        except:
            pass
        if e.keyName.__contains__('shift'):
            self.window.mouseLock = not self.window.mouseLock
        if e.keyName == 'escape':  # ESC
            self.close()
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

    def close(self):
        self.window.close()

    def prepareScene(self):
        try:

            # Note: If default shaders in engine are modified, shaders in 'Demos/shaders' should be updated acordingly.

            engine = self.engine
            # self.window.backend.fullScreenEffects.addEffect('simple_override.fse', 'simpleFSE', 'simple')
            self.fse = self.window.backend.fullScreenEffects.addEffect('shaders/simple_multiRTT.fse',
                                                                            'simpleMultiRTT', 'simple')
            # self.window.backend.debugModeActive = True
            engine.textures.loadTexture('e3dlogo.png', 'logo')
            engine.textures.loadTexture('./textures/Grass.jpg', 'grass')

            # engine.shaders.loadShader('shaders/multiVS.glsl', 'shaders/multiFS.glsl', 'multi')

            self.camera = SimpleCamera(vec3(0, 30, 200), vec3(0, 180, 0), ID='maincam', zFar=900)

            self.scene1 = engine.scenes.addScene('scene1')
            self.scene1.currentCamera = self.camera
            self.scene1.beforeUpdateCallback = self.scene1Update
            # self.scene1.setDefaultSkyBox()
            self.scene1.ambientColor = [v / 3.0 for v in [0.23, 0.34, 0.65]]
            self.scene1.bgColor = [0,0,0]  # fixme: This is overriden by the effect
            # self.scene1.ambientColor = [.23, .34, .45]
            self.dlight = self.scene1.addLight()
            self.dlight.color = vec3(1.0, 1.0, .80)
            self.dlight.rotation = vec3(45, 45, 0)
        except Exception as ex:
            print('error in main.prepareScene: ' + str(ex))
            self.close()
            self.engine.terminate()
            raise

        engine.scenes.currentSceneID = 'scene1'

    def loadModels(self):
        engine = self.engine
        engine.models.loadModel(duckMODEL, "duckmodel", forceStatic=True)
        self.duck = self.scene1.addModel('duckmodel', 'duck1', vec3(0, -20, -10), vec3(0), 1)
        # mat = self.duck.getMaterialByIndex(0)
        # mat.shaderID = 'normals'
        # mat.shaderID = 'multi'

        self.duck2 = self.scene1.addModel('duckmodel', 'duck2', vec3(-100, 0, -200), vec3(0), 1.7)

        engine.models.loadModel(dwarfMODEL, "dwarfmodel", preCalculateFrames=-1)
        self.dwarf = self.scene1.addModel('dwarfmodel', 'dwarf1', vec3(0), vec3(0), 13)
        self.dwarf.rotateY(180)
        self.dwarf.moveRight(100)
        self.dwarf.setAnimation(self.dwarf.getAnimationsList()[0], True)

        engine.models.loadModel(tubeMODEL, "tubemodel")
        self.tube = self.scene1.addModel('tubemodel', 'tube1', vec3(0), vec3(0), 7)
        self.tube.setAnimation(self.tube.getAnimationsList()[0], True)
        self.tube.moveRight(100)

        engine.models.loadPlane("planemodel")
        self.plane = self.scene1.addModel('planemodel', 'floor', vec3(0, -20, 0), vec3(0), 100)
        mat = self.plane.getMaterialByIndex(0)
        mat.specularPower = 10000000000
        mat.diffuseTextureID = 'grass'
        mat.useDiffuseTexture = True
        mat.textureRepeat = 60

    def buildGui(self):
        self.onelayer = self.window.gui.addLayer('one')
        super(Demo, self).buildGui()

        rtW = 120
        rtH = 100
        left = LOGOSSIZE + 10
        diffuse = Panel(left, 0, rtW, rtH, self.onelayer)
        normals = Panel(left + rtW, 0, rtW, rtH, self.onelayer)
        positions = Panel(left + rtW * 2, 0, rtW, rtH, self.onelayer)
        depth = Panel(left + rtW * 3, 0, rtW, rtH, self.onelayer)

        diffuse.backgroundImageID = self.fse.ID + '_diffuse'  # TODO: implement texture retrieval
        normals.backgroundImageID = self.fse.ID + '_normals'
        positions.backgroundImageID = self.fse.ID + '_positions'
        depth.backgroundImageID = self.fse.ID + '_depth'
        diffuse.upSideDownTextures = True
        normals.upSideDownTextures = True
        positions.upSideDownTextures = True
        depth.upSideDownTextures = True


if __name__ == '__main__':
    runDemo(Demo(), 'Multi Render To Texture Demo')
