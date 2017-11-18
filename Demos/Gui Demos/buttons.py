# coding=utf-8
from cycgkit.cgtypes import vec3, vec4

from _set_path import setPath

setPath()
from _base._BaseDemo import _Demo_Base, runDemo, triangleMODEL
from e3d.gui import PinningEnum, StyleHintsEnum, Panel, Button, Label
from e3d.Colors import *
import os


class Demo(_Demo_Base):
    def __init__(self, winsize):
        super(Demo, self).__init__(winsize)
        self.texturesToLoad = [['e3dlogo.png', 'logo'], ['../textures/Grass.jpg', 'grass']]

    def loadModels(self):
        # engine = self.engine

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

        if keyName == 'escape':  # ESC
            self.close()
        if 'ctrl' in keyName:
            self.dorot = not self.dorot
        if keyName.__contains__('space'):
            self.window.setFullScreen(not self.window.isFullScreen())
        elif keyName == 'f1':  # F1
            np = [round(d, 3) for d in self.camera.position]
            print('Camera pos:{0}'.format(str(np)))
        
    def buildGui(self):
        self.onelayer = self.window.gui.addLayer('one')
        super(Demo, self).buildGui()

        # load an extra font
        self.window.gui.loadFont('auto', os.path.join(os.path.pardir, 'fonts', 'automati.ttf'))

        container = Panel(80, 10, 250, 150, self.onelayer, ID='container')

        Button(20, 20, 150, 40, 'Click me!', container, ID='hideBtn').onMouseClick = self.buttonClick
        closeBtn = Button(20, 70, 200, 30, 'Close window', container, fontID='auto', ID='CloseButton')
        closeBtn.fontColor = RED
        closeBtn.onMouseClick = lambda ev: self.window.close()
        self.containers = []

        flatContainer = Panel(container.windowPosition.x + container.width + 10, 10, 250, 150, self.onelayer)
        flatContainer.visible = False
        self.containers.append(flatContainer)
        Label(0, 0, 200, 'Flat style', flatContainer)
        Button(20, 30, 150, 40, 'Button 1', flatContainer).styleHint = StyleHintsEnum.Flat
        Button(20, 80, 200, 30, 'Button 2', flatContainer).styleHint = StyleHintsEnum.Flat

    def buttonClick(self, eventData):
        print(eventData)  # for debuggin
        for container in self.containers:
            container.visible = not container.visible


if __name__ == '__main__':
    runDemo(Demo((950, 680)), 'GUI Demo - Single Char')
