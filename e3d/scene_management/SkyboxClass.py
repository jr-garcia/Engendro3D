from os import path
from cycgkit.cgtypes import mat4

from ..Base3DObjectClass import Base3DObject
from ..model_management.MaterialClass import Material


class Skybox(Base3DObject):
    def __init__(self, ID, engine):
        super(Skybox, self).__init__([0, 0, 0], [0, 0, 0], 1, 1, ID=ID)
        self.layers = []
        self._material = Material()
        self._material._shaderID = 'sky'
        self._engine = engine

        p = path.join(engine.path, 'defaults', 'shaders', 'sky')
        vsp = p + 'VS.vs'
        fsp = p + 'FS.fs'

        self.shader = engine.shaders.loadShader(vsp, fsp, 'sky')

    def loadDefault(self):
        texpath = path.join(self._engine.path, 'defaults', 'textures', 'skyboxes', 'Teide')
        ct = self._engine.textures.loadCubeTexture(texpath, 'default')
        self.layers.append(ct)


