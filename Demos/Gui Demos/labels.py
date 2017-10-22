# coding=utf-8
from cycgkit.cgtypes import vec3, vec4

from _set_path import setPath

setPath()
from _base._BaseDemo import _Demo_Base, runDemo, triangleMODEL
from e3d.gui import PinningEnum, Label, CharRangesEnum
from math import sin
import os


class Demo(_Demo_Base):
    def __init__(self):
        super(Demo, self).__init__((950, 480))
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

        # load default font with japanese letters / symbols
        self.window.gui.loadFont('default', os.path.join(self.engine.path.defaults.fonts, 'code', 'Code200365k.ttf'),
                                 baseSize=34, charRange=CharRangesEnum.latin, force=True)

        self.window.gui.loadFont('auto', os.path.join(os.path.pardir, 'fonts', 'automati.ttf'))

        textLayer = self.window.gui.addLayer('text')

        text1 = 'G{]|t!?p=#$%&^*()&*'
        text2 = 'Y eso lo es, pero no! Puedo yo, pues?'
        self.label1 = Label(20, 80, 900, text1, parent=textLayer, fontSize=74, fontID='default', borderSize=3,
                            outlineColor=[1, 0, 0, 1], outlineLength=.15)
        self.label2 = Label(25, self.label1._height + 100, 700, text2, parent=textLayer, fontID='auto',
                            fontColor=[.5, .5, 0, 1], fontSize=18, borderSize=0)

        self.label3 = Label(20, self.label2._top + 100, 697, 'Press CTRL, SHIFT, UP or DOWN', textLayer)

        self.label1.color = [1, 1, 0, 1]
        self.label2.color = [0, 1, 0, .5]
        self.label1.borderColor = vec4(1)


if __name__ == '__main__':
    runDemo(Demo(), 'GUI Demo - Single Char')
