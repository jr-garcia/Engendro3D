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
        self.camera.position = vec3(0, 100, 290)
        self.camera.rotateX(20)

    def prepareScene(self):
        super(Demo, self).prepareScene()
        self.scene1.bgColor = vec3(0)

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

    def buildGui(self):
        self.onelayer = self.window.gui.addLayer('one')
        super(Demo, self).buildGui()

        self.window.gui.loadFont('auto', os.path.join(os.path.pardir, 'fonts', 'automati.ttf'))

        textLayer = self.window.gui.addLayer('text')

        self.instructionsLabel = Label(300, self.window.size[1] - 50, 310, 'Press CTRL or Arrow keys',
                                       self.onelayer, pinning=PinningEnum.BottomLeft)
        self.instructionsLabel.gradientType = GradientTypesEnum.Vertical
        self.instructionsLabel.borderSize = 0
        self.instructionsLabel.gradientColor0 = vec4(.3, .1, 0, 1)
        self.instructionsLabel.gradientColor1 = vec4(.8, .3, 0, 1)

        lastTop = 0
        labels = []
        listRange = list(range(26, 5, -2))
        listRange.insert(0, 60)
        listRange.insert(1, 40)
        for i in listRange:
            lab = Label(50, lastTop, 800, '', textLayer, fontID='auto')
            lab.fontSize = i
            lab.outlineColor = vec4(1, 0, 1, 1)
            height = lab.height
            fontID = lab.fontID
            style = weigthNames[lab.fontWeight]
            lastTop += height
            lab.text = 'Size {}, {} pixels. Name {}. Style: {}'.format(i, height, fontID, style)
            lab.borderSize = 0
            labels.append(lab)
        self.labels = labels


if __name__ == '__main__':
    runDemo(Demo((950, 680)), 'GUI Demo - Single Char')
