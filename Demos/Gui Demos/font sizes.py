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
        self.texturesToLoad = [['e3dlogo.png', 'logo'], ['../textures/Grass.jpg', 'grass']]

    def loadModels(self):
        engine = self.engine

        self.camera.position = vec3(0, 100, 290)
        self.camera.rotateX(20)

        # engine.models.loadModel(triangleMODEL, "trianglemodel", forceStatic=True)
        # self.triangle = self.scene1.addModel('trianglemodel', 'triangle1', vec3(0, 0, 0), vec3(0), 1.5)
        # mat = self.triangle.getMaterialByIndex(0)
        # mat.useDiffuseTexture = True

    def keydown(self, e):
        if e.eventName == 'keyUp':
            return
        keyName = e.keyName
        try:
            e.keyName = keyName.decode()
        except Exception:
            pass
        change = 0
        change2 = 0
        label0 = self.labels[0]
        fontID = label0.fontID
        weight = label0.fontWeight
        outline = label0.outlineLength
        if keyName == 'escape':  # ESC
            self.close()
        elif 'ctrl' in keyName:
            if fontID == 'default':
                fontID = 'auto'
            else:
                fontID = 'default'
        elif keyName.__contains__('space'):
            self.window.setFullScreen(not self.window.isFullScreen())
        elif keyName == 'f1':  # F1
            np = [round(d, 3) for d in self.camera.position]
            print('Camera pos:{0}'.format(str(np)))
        elif keyName == 'up':
            change = -1
        elif keyName == 'down':
            change = 1
        elif keyName == 'left':
            change2 = -1
        elif keyName == 'right':
            change2 = 1

        vals = list(weigthNames.keys())
        for i in range(len(vals)):
            val = vals[i]
            if weight == val:
                break
        i += change
        if i > 2:
            i = 0
        if i < 0:
            i = 2
        weight = vals[i]

        vals = list(outlineLengths.keys())
        for i in range(len(vals)):
            val = vals[i]
            if outline == val:
                break
        i += change2
        if i > 3:
            i = 0
        if i < 0:
            i = 3
        outline = vals[i]

        lastTop = 0
        for lab in self.labels:
            lab.fontID = fontID
            lab.fontWeight = weight
            lab.outlineLength = outline
            style = weigthNames[weight]
            height = lab.height
            if lab.fontSize <= 20:
                lab.text = 'Size {}, {} pixels. Name: \'{}\'. Style: {}'.format(lab.fontSize, height, fontID, style)
            else:
                lab.text = 'Size {}, {} pixels'.format(lab.fontSize, height)
            left, top, z = lab.position
            lab.position = vec3(left, lastTop, z)
            lastTop += lab.height

    def scene1Update(self, ev):
        pass
        # ft = ev[0] + .01
        # if self.dorot:
        #     if self.triangle:
        #         self.triangle.rotateY(.1 * ft)

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
        # self.label1 = Label(20, 20, 900, text1, parent=textLayer, fontSize=74, fontID='default', borderSize=3,
        #                     outlineColor=[1, 0, 0, 1], outlineLength=.15)
        # self.label2 = Label(25, self.label1._height + 100, 700, text2, parent=textLayer, fontID='auto',
        #                     fontColor=[.5, .5, 0, 1], fontSize=18, borderSize=0)

        # self.label1.color = [1, 1, 0, 1]
        # self.label2.color = [0, 1, 0, .5]
        # self.label1.borderColor = vec4(1)
        self.instructionsLabel = Label(300, self.window.size[1] - 150, 310, 'Press CTRL, SHIFT, UP or DOWN',
                                       self.onelayer, pinning=PinningEnum.BottomLeft,
                                       gradientType=GradientTypesEnum.Vertical, borderSize=0)
        self.instructionsLabel.gradientColor0 = vec4(.3, .1, 0, 1)
        self.instructionsLabel.gradientColor1 = vec4(.8, .3, 0, 1)

        lastTop = 0  # self.label1._height + self.label1._top
        labels = []
        listRange = list(range(20, 4, -1))
        listRange.insert(0, 60)
        listRange.insert(1, 40)
        for i in listRange:
            lab = Label(50, lastTop, 800, '', textLayer, i, borderSize=1, fontID='auto')
            height = lab.height
            fontID = lab.fontID
            style = weigthNames[lab.fontWeight]
            lastTop += height
            lab.text = 'Size {}, {} pixels. Name {}. Style: {}'.format(i, height, fontID, style)
            labels.append(lab)
        self.labels = labels
        # self.fontNameLabel = Label(500, 300, 200, 'Font name: {}'.format(labels[0].fontID), textLayer)


if __name__ == '__main__':
    runDemo(Demo((950, 680)), 'GUI Demo - Single Char')
