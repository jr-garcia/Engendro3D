# coding=utf-8
from cycgkit.cgtypes import vec3, vec4

from _set_path import setPath

setPath()
from _base._BaseDemo import _Demo_Base, runDemo, triangleMODEL
from e3d.gui import PinningEnum, StyleHintsEnum, Panel, ProgressBar, Label
from e3d.gui.Styling.styles import ColorfullStyle
from e3d.Colors import *
import os
from math import sin


class Demo(_Demo_Base):
    def __init__(self, winsize):
        super(Demo, self).__init__(winsize)
        self.texturesToLoad = [['e3dlogo.png', 'logo'], ['../textures/Grass.jpg', 'grass'],
                               ['../textures/square_blue.png', 'blue'],
                               ['../textures/square_normal.png', 'normal']]
        self.bars = []

    def loadModels(self):
        self.camera.position = vec3(0, 100, 290)
        self.camera.rotateX(20)

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
        if not self.dorot:
            return 
        for bar in self.bars:
            bar.value += sin(ev[1] / 1000.0)
        
    def buildGui(self):
        self.onelayer = self.window.gui.addLayer('one')
        super(Demo, self).buildGui()

        # load an extra font
        self.window.gui.loadFont('auto', os.path.join(os.path.pardir, 'fonts', 'automati.ttf'))

        container = Panel(80, 10, 250, 150, self.onelayer, ID='container')
        Label(0, 0, 200, 'Raised stylehint', container, fontID='auto')
        ProgressBar(20, 30, 150, 40, container, ID='hideBtn').fontID = 'auto'
        raisedPrg = ProgressBar(20, 80, 200, 30, container, ID='CloseButton', color=RED)
        raisedPrg.color = GREEN
        raisedPrg.barColor = BLUE
        raisedPrg.value = 80
        raisedPrg.styleHint = StyleHintsEnum.Sunken
        raisedPrg.borderColor = container.borderColor
        self.bars.append(raisedPrg)

        flatContainer = Panel(container.windowPosition.x + container.width + 10, 10, 250, 150, self.onelayer)
        Label(0, 0, 200, 'Flat stylehint', flatContainer, fontID='auto')
        ProgressBar(20, 30, 150, 40, flatContainer).styleHint = StyleHintsEnum.Flat
        secondFlat = ProgressBar(20, 80, 200, 30, flatContainer, color=RGB1(.1, .5, 0), barColor=BLUE)
        secondFlat.styleHint = StyleHintsEnum.Flat
        secondFlat.value = 28
        secondFlat.backgroundSize = 4
        secondFlat.fontID = 'auto'
        self.bars.append(secondFlat)

        cfStyle = ColorfullStyle()  # This style overriders base color
        colorfullContainer = Panel(400, container.windowPosition.y + container.height + 10,
                                   250, 200, self.onelayer, style=cfStyle)
        Label(10, 10, 200, 'Colorfull style', colorfullContainer, fontID='auto', style=cfStyle)
        ProgressBar(20, 50, 150, 60, colorfullContainer, style=cfStyle)
        colorfullFlatPrg = ProgressBar(20, 120, 180, 40, colorfullContainer, ID='ColorfullFlatButton')
        colorfullFlatPrg.style = cfStyle
        colorfullFlatPrg.styleHint = StyleHintsEnum.Flat
        colorfullFlatPrg.barColor = fromRGB1_A((GREEN + BLUE) / 2.0, 1)
        colorfullFlatPrg.value = 76
        self.bars.append(colorfullFlatPrg)

        ImageContainer = Panel(container.width * 2 + 100, 10, 250, 150, self.onelayer)
        ImageContainer.color = TRANSPARENT
        Label(0, 0, 200, 'Image stylehint', ImageContainer, fontID='auto')
        imagePrg = ProgressBar(20, 60, 200, 30, ImageContainer, color=TRANSPARENT)
        imagePrg.styleHint = StyleHintsEnum.Image
        imagePrg.borderSize = 0
        imagePrg.fontColor = BLACK
        imagePrg.backgroundImageID = 'normal'
        imagePrg.progressImageID = 'blue'
        imagePrg.value = 150
        imagePrg.minimum = 100
        imagePrg.maximum = 200
        imagePrg.showPercent = False

        height = imagePrg.top + imagePrg.height
        Label(imagePrg.left - 10, height, 50, str(int(imagePrg.minimum)), ImageContainer)
        Label(imagePrg.left + imagePrg.width - 20, height, 50, str(int(imagePrg.maximum)), ImageContainer)
        self.bars.append(imagePrg)


if __name__ == '__main__':
    runDemo(Demo((950, 680)), 'GUI Demo - ProgressBars')
