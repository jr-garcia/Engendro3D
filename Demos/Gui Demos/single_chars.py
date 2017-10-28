# coding=utf-8
from cycgkit.cgtypes import vec3, vec4

from _set_path import setPath
setPath()
from _base._BaseDemo import _Demo_Base, runDemo, triangleMODEL
from e3d.gui import PinningEnum, SingleChar, CharRangesEnum
from math import sin
import os


class Demo(_Demo_Base):
    def __init__(self):
        super(Demo, self).__init__()
        self.texturesToLoad = [['e3dlogo.png', 'logo'], ['../textures/Grass.jpg', 'grass']]

    def loadModels(self):
        engine = self.engine

        self.camera.position = vec3(0, 100, 290)
        self.camera.rotateX(20)

        engine.models.loadModel(triangleMODEL, "trianglemodel", forceStatic=True)
        self.triangle = self.scene1.addModel('trianglemodel', 'triangle1', vec3(0, 0, 0), vec3(0), 1.5)
        mat = self.triangle.getMaterialByIndex(0)
        mat.useDiffuseTexture = True

    def keydown(self, e):
        if e.eventName == 'keyUp':
            return
        keyName = e.keyName
        try:
            e.keyName = keyName.decode()
        except Exception:
            pass

        if keyName == 'escape':  # ESC
            self.close()
        if 'ctrl' in keyName:
            self.dorot = not self.dorot
        if keyName.__contains__('space'):
            self.window.setFullScreen(not self.window.isFullScreen())
        if keyName == 'f1':  # F1
            np = [round(d, 3) for d in self.camera.position]
            print('Camera pos:{0}'.format(str(np)))

    def scene1Update(self, ev):
        ft = ev[0] + .01
        if self.dorot:
            if self.triangle:
                self.triangle.rotateY(.1 * ft)

    def buildGui(self):
        self.onelayer = self.window.gui.addLayer('one')
        super(Demo, self).buildGui()

        # load default font with japanese letters / simbols
        self.window.gui.loadFont('defaultJap', os.path.join(self.engine.path.defaults.fonts, 'code', 'Code200365k.ttf'),
                                 baseSize=34, charRange=CharRangesEnum.japanese)

        self.window.gui.loadFont('auto', os.path.join(os.path.pardir, 'fonts', 'automati.ttf'))

        textLayer = self.window.gui.addLayer('text')

        self.char = SingleChar(30, 30, 200, '?', textLayer)
        self.char.outlineColor = vec4(1, 0, 0, 1)

        SingleChar(250, 250, 200, u'癒', self.onelayer, fontID='defaultJap')


if __name__ == '__main__':
    runDemo(Demo(), 'GUI Demo - Single Char')

