from cycgkit.cgtypes import vec3, vec4

from _set_path import setPath

setPath()
from _base._BaseDemo import _Demo_Base, runDemo, triangleMODEL
from e3d.gui import Panel, GradientTypesEnum, PinningEnum
from e3d import Colors
from e3d.video import Video
from math import sin
from os import path


class Demo(_Demo_Base):
    def __init__(self, winSize):
        super(Demo, self).__init__(winSize)

    def loadModels(self):
        engine = self.engine

        camera = self.camera
        camera.rotateX(15)
        camera.position = vec3(0, 40.051, 108.345)

        engine.models.loadPlane("floorplane", 500, 500, 6)
        self.floor = self.scene1.addModel('floorplane', 'floor', [0, 0, 0], [0, 0, 0], 1)
        mt = self.floor._materials[0]
        mt.specularPower = 50
        mt.useDiffuseTexture = True
        mt.setDefaultNormalMap()
        mt.textureRepeat = 80

        engine.models.loadBox("boxmodel", [28, 20, 20], 2)
        self.box1 = self.scene1.addModel('boxmodel', 'box1', [0, 11, 0], [0, 0, 0], 2)
        mt = self.box1._materials[0]
        mt.specularPower = 40
        mt.textureRepeat = 2
        mt.useDiffuseTexture = True

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
        if keyName == 'p':
            self.video.play()  # todo: add pause
        if 'ctrl' in keyName:
            self.dorot = not self.dorot
        if keyName == 'f1':
            np = [round(d, 3) for d in self.camera.position]
            self._engine.log('Camera pos:{0}'.format(str(np)), logLevelsEnum.debug)
            self._engine.log('Poligons drawn:{}'.format(self.window.backend.poligonsDrawnThisUpdate),
                             logLevelsEnum.debug)
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

    def buildGui(self):
        self.onelayer = self.window.gui.addLayer('one')
        super(Demo, self).buildGui()

        videos = self.engine.videos
        bunnyPath = '../videos/bunny/bunny_trimed_1_15.webm'

        '''
        Video sample extracted from Big Buck Bunny short, at time 0:1:15.16
        (c) copyright 2008, Blender Foundation / www.bigbuckbunny.org
        '''

        info = videos.getVideoInfo(bunnyPath)
        width, height = info['video_size']

        width /= 2  # My development computer is slow, so I need to resize
        height /= 2  # this fullHD video to make it run smoothly on my device

        video = videos.load(bunnyPath, resizeTo=(width, height))
        self.video = video
        videoTexID = video.getTextureID()  # get the ID for the video's texture
        height, width = video._size

        longPanel = Panel(10, 10, width / 4, height / 4, self.onelayer, color=vec4(0, 0, 1, 1))
        longPanel.borderColor = vec4(.8, .5, 0, 1)
        longPanel.borderSize = 4
        longPanel.opacity = .70

        mat = self.box1.getMaterialByIndex(0)
        mat.useDiffuseTexture = True

        longPanel.backgroundImageID = videoTexID  # apply the video texture to the panel
        mat.diffuseTextureID = videoTexID  # and the models

        print('Press P to switch video playing.')


if __name__ == '__main__':
    runDemo(Demo((980, 600)), 'GUI Demo - Panels')
