from cycgkit.cgtypes import vec3, vec4

from Demos._base._BaseDemo import _Demo_Base, runDemo, triangleMODEL
from e3d.gui import Panel, GradientTypesEnum, PinningEnum


class Demo(_Demo_Base):
    def __init__(self, winSize):
        super(Demo, self).__init__(winSize)
        self.texturesToLoad = [['e3dlogo.png', 'logo']]

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
        try:
            e.keyName = e.keyName.decode()
        except Exception:
            pass

        if e.keyName == 'escape':  # ESC
            self.close()
        if e.keyName.__contains__('space'):
            self.window.setFullScreen(not self.window.isFullScreen())
        if e.keyName == 'f1':  # F1
            np = [round(d, 3) for d in self.camera.position]
            print('Camera pos:{0}'.format(str(np)))

    def scene1Update(self, ev):
        ft = ev[0] + .01
        movespeed = ft / 10.0
        self.lastspeed = movespeed
        if self.dorot:
            if self.triangle:
                self.triangle.rotateY(.1 * ft)

    def buildGui(self):
        self.onelayer = self.window.gui.addLayer('one')
        super(Demo, self).buildGui()

        panelSize = 100

        borderedPanel = Panel(110, 0, panelSize, panelSize, self.onelayer)
        longPanel = Panel(220, 0, panelSize * 2.5, panelSize, self.onelayer, color=vec4(1, 0, 1, 1), borderSize=0)
        for i in range(9):
            Panel(110 * i, 105, panelSize, panelSize, self.onelayer, borderSize=1, gradientType=i).opacity = .7

        pinnedW = panelSize * 4
        pinnedH = panelSize * 2
        pinnedCorners = []
        cornerSize = 30
        rightBorder = pinnedW - cornerSize
        bottomBorder = pinnedH - cornerSize

        pinnedPanel = Panel(250, 220, pinnedW, pinnedH, self.onelayer, color=vec4(0, 1, 0, .5), ID='pinned',
                            borderSize=5)
        pinnedPanel.pinning = PinningEnum.all
        pinnedCorners.append(Panel(0, 0, cornerSize, cornerSize, pinnedPanel))
        pinnedCorners.append(Panel(rightBorder, 0, cornerSize, cornerSize, pinnedPanel, PinningEnum.TopRight))
        pinnedCorners.append(Panel(0, bottomBorder, cornerSize, cornerSize, pinnedPanel, PinningEnum.BottomLeft))
        pinnedCorners.append(Panel(rightBorder, bottomBorder, cornerSize, cornerSize, pinnedPanel,
                                   PinningEnum.BottomRight))
        for panel in pinnedCorners:
            panel.color = vec4(.5, 1, 1, 1)
            panel.borderSize = 1

        for i in range(4):
            Panel(10 + (20 * i), 220 + (20 * i), panelSize, panelSize, self.onelayer, color=vec4(1, 1, 0, 1))


if __name__ == '__main__':
    runDemo(Demo((950, 480)), 'GUI Demo - Panels')
