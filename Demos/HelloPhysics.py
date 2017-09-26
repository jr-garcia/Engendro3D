from cycgkit.cgtypes import vec3

from Demos._base._physics_base import Demo as game, runDemo


class Demo(_Demo_Base):
    def __init__(self):
        game.__init__(self)

    def loadModels(self):
        engine = self.engine
        game.loadModels(self)
        self.camera.position = vec3(0, 10, 250)

        self.bigSphere = self.scene1.addModel('bigspheremodel', 'bigSphere', [0, 100, 0], [0, 0, 0], 20, mass=8)
        self.bigSphere.physicsBody.isDynamic = True
        mats = self.bigSphere.getMaterialByIndex(0)
        mats.specularPower = 50
        mats.useDiffuseTexture = True
        mats.useNormalMapTexture = True
        mats.normalMapTextureID = 'defND'
        mats.textureRepeat = 4
        self.bumpymats.append(mats)
        self.texmats.append(mats)

        self.floor = self.scene1.addModel('floorplane', 'floor', [0, 0, 0], [0, 0, 0], 720)
        mt = self.floor._materials[0]
        mt.specularPower = 50
        mt.useDiffuseTexture = True
        mt.setDefaultNormalMap()
        mt.textureRepeat = 4
        self.bumpymats.append(mt)
        self.texmats.append(mt)


if __name__ == '__main__':
    runDemo(Demo(), 'Hello Physics')
