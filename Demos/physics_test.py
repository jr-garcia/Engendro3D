from cycgkit.cgtypes import vec3

from _base._physics_base import Physics_Demo_Base, runDemo, tubeMODEL


class Demo(Physics_Demo_Base):
    def __init__(self):
        Physics_Demo_Base.__init__(self)

    def loadModels(self):
        engine = self.engine
        Physics_Demo_Base.loadModels(self)
        engine.models.loadSphere("spheremodel", 12)
        engine.models.loadBox("boxmodel", [6], 1)
        engine.models.loadBox("pushboxmodel", [50, 10, 10], 1)
        engine.models.loadPlane("planemodelWalls", 600, 300, 20)

        engine.models.loadModel(tubeMODEL, "tubemodel")
        self.camera.position = vec3(0, 90, 350)

        self.bigSphere = self.scene1.addModel('bigspheremodel', 'bigSphere', [0, 10, 0], [0, 0, 0], 25, mass=8)
        self.bigSphere.physicsBody.isDynamic = True
        mats = self.bigSphere.getMaterialByIndex(0)
        mats.specularPower = 50
        mats.useDiffuseTexture = True
        mats.useNormalMapTexture = True
        mats.normalMapTextureID = 'defND'
        mats.textureRepeat = 4
        self.bumpymats.append(mats)
        self.texmats.append(mats)

        self.box1 = self.scene1.addModel('boxmodel', 'box1', [0, 90, 0], [0, 90, 0], 10, mass=7)
        self.box1.physicsBody.isDynamic = True
        mt = self.box1._materials[0]
        mt.specularPower = 40
        mt.useDiffuseTexture = True
        mt.useNormalMapTexture = True
        mt.normalMapTextureID = 'defNI'
        self.bumpymats.append(mt)
        self.texmats.append(mt)

        self.pushbox1 = self.scene1.addModel('pushboxmodel', 'pushbox1', [200, 6, 0], [0, 0, 0], 4, mass=50)
        self.pushbox2 = self.scene1.addModel('pushboxmodel', 'pushbox2', [-200, 6, 0], [0, 0, 0], 4, mass=50)

        self.floor = self.scene1.addModel('floorplane', 'floor', [0, 0, 0], [0, 0, 0], 1000, mass=0)
        mt = self.floor._materials[0]
        mt.specularPower = 50
        mt.useDiffuseTexture = True
        mt.useNormalMapTexture = True
        mt.normalMapTextureID = 'defNI'
        mt.textureRepeat = 10
        self.bumpymats.append(mt)
        self.texmats.append(mt)

        self.planer = self.scene1.addModel('planemodelWalls', 'planer', [300, 170, 0], [90, 0, 0], 1)
        self.planer.rotateY(-90)
        mt = self.planer._materials[0]
        mt.useNormalMapTexture = True
        mt.normalMapTextureID = 'testN'
        mt.textureRepeat = 10
        self.bumpymats.append(mt)

        self.planel = self.scene1.addModel('planemodelWalls', 'planel', [-300, 170, 0], [90, 0, 0], 1)
        self.planel.rotateY(90)
        self.planel._materials[0] = mt

        self.planef = self.scene1.addModel('planemodelWalls', 'planef', [0, 170, -300], [90, 0, 0], 1)
        self.planef._materials[0] = mt

        self.tube = self.scene1.addModel('tubemodel', 'tube1', [-150, 20, 0], [0, 0, 0], 7)
        self.tube.setAnimation(self.tube.getAnimationsList()[0], True)
        # self.tube.physicsBody.isDynamic = True

        self.tube2 = self.scene1.addModel('tubemodel', 'tube2', [150, 70, 0], [0, 0, 0], 7)
        self.tube2.physicsBody.isDynamic = True

    def scene1Update(self, ev):
        ft = ev[0] + .01

        if self.dorot:
            if self.pushbox1:
                self.pushbox1.rotateY(-.07 * ft)
                self.pushbox2.rotateY(-.07 * ft)
        Physics_Demo_Base.scene1Update(self, ev)


if __name__ == '__main__':
    runDemo(Demo(), 'Physics Test 1')
