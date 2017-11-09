# coding=utf-8
from cycgkit.cgtypes import vec3, vec4

from _set_path import setPath

setPath()
from _base._BaseDemo import _Demo_Base, runDemo, triangleMODEL
from e3d.gui import PinningEnum, Label, CharRangesEnum, TextEnums, GradientTypesEnum
from math import sin
import os
from collections import OrderedDict

weigthNames = OrderedDict()
weigthNames[0.4] = 'light '
weigthNames[.6] = 'normal'
weigthNames[.9] = 'bold '

outlineLengths = OrderedDict()
outlineLengths[0] = 'NoOutline'
outlineLengths[0.125] = 'Little'
outlineLengths[0.25] = 'Medium'
outlineLengths[0.5] = 'Big'


class Demo(_Demo_Base):
    def __init__(self,winsize):
        super(Demo, self).__init__(winsize)

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
        elif keyName == 'f1':  # F1
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
        self.window.gui.loadFont('defaultJapanese',
                                 os.path.join(self.engine.path.defaults.fonts, 'code', 'Code200365k.ttf'),
                                 baseSize=34, charRange=CharRangesEnum.japanese)  # Will take some time first time

        self.window.gui.loadFont('auto', os.path.join(os.path.pardir, 'fonts', 'automati.ttf'))

        textLayer = self.window.gui.addLayer('text')

        text1 = '+)(*&^%$#@!{}|":?><~`'
        text2 = 'Lorem ipsum dolor sit amet, consectetur...'
        text3 = u'デモのみ。非ラテン文字用に最適化されていません。'
        text4 = 'Demo only. Not optimized for non latin chars.'
        TLR = PinningEnum.TopLeftRight
        self.label1 = Label(20, 80, 900, text1, parent=textLayer, pinning=TLR, fontSize=64, fontID='default',
                            outlineLength=outlineLengths.keys()[2])
        self.label1.color = [1, 1, 0, 1]
        self.label1.borderColor = vec4(1, .6, 0, .5)
        self.label1.outlineColor = [1, 0, 0, 1]
        self.label1.borderSize = 6

        self.label2 = Label(25, self.label1.height + 100, 900, text2, parent=textLayer, fontID='auto', fontSize=18,
                            pinning=TLR)
        self.label2.color = [0, 1, 0, .5]
        self.label2.fontColor = [.8, 0, .8, .5]
        self.label2.borderSize = 0

        self.label3 = Label(20, self.label2.top + 100, 697, text3, textLayer, fontID='defaultJapanese')
        self.label4 = Label(20, self.label3.top + self.label3.height, 697, text4, textLayer, fontID='default')


if __name__ == '__main__':
    runDemo(Demo((950, 680)), 'GUI Demo - Single Char')
