from PySide.QtOpenGL import QGLWidget, QGLFormat
from PySide import QtGui
from PySide.QtCore import Qt


from .base import Window_Base


class e3DGLWidget(Window_Base, QGLWidget):
    def __init__(self, engine, title, gameName, sizeAsList, FullScreenSize, fullscreen, vSynch, iconPath):
        QGLWidget.__init__(self, engine._format, None, shareWidget=engine.globals.dummyWindow)
        Window_Base.__init__(self, engine, title, gameName, sizeAsList, FullScreenSize, fullscreen, vSynch, iconPath)

    def _createInternalWindow(self, title, engine, fullscreen):
        self.initializeGL()
        self.makeCurrent()

    @property
    def size(self):
        return self.frameSize().toTuple()

    @size.setter
    def size(self, val):
        self.frameSize = val

    def _performSwap(self):
        self.swapBuffers()

    def _makeContextCurrent(self):
        self.makeCurrent()

    def resizeGL(self, *args, **kwargs):
        w, h = self.frameSize().toTuple()
        self._sizeChanged(w, h)

    def paintGL(self, *args, **kwargs):
        self.update()
