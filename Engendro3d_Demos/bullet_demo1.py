from _do_import import resolve_import

from cgkit.cgtypes import vec3

from e3d.LoggerClass import logger, logLevelsEnum

resolve_import()

from _BaseDemo import game, runDemo


class Demo(game):
    def __init__(self):
        super(Demo, self).__init__()
        self.texturesToLoad = [
            # ['e3dlogo.png', 'logo'],
            # ['Grass.jpg', 'grass'],
            ['defaults/default_n.png', 'defN'], ['./textures/n_deep.png', 'defND', True],
            ['./textures/n_irr.png', 'defNI', True], ['./textures/nmap_test.png', 'testN', True],
            ['./textures/earth_nasa_brighter.jpg', 'earth']]

    def loadModels(self):
        engine = self.engine
        engine.models.loadSphere("mainspheremodel", 32)
        self.sphere1 = self.scene1.addModel('mainspheremodel', 'sphere1', [0, 10, 0], [0, 0, 0], 4, mass=8)
        # self.sphere1.physicsBody.isDynamic = True
        # mats = self.sphere1.getMaterialByIndex(0)
        # mats.specularPower = 50
        # mats.useDiffuseTexture = True
        # mats.useNormalMapTexture = True
        # mats.normalMapTextureID = 'defND'
        # mats.textureRepeat = 4
        # self.sphereMat = mats
        # self.bumpymats.append(mats)
        # self.texmats.append(mats)

        # engine.models.loadSphere("spheremodel", 12)

        # engine.models.loadBox("boxmodel", [6], 1)
        # self.box1 = self.scene1.addModel('boxmodel', 'box1', [0, 90, 0], [0, 90, 0], 5, mass=7)
        # self.box1.physicsBody.isDynamic = True
        # mt = self.box1._materials[0]
        # mt.specularPower = 40
        # mt.useDiffuseTexture = True
        # mt.useNormalMapTexture = True
        # mt.normalMapTextureID = 'defNI'
        # self.bumpymats.append(mt)
        # self.texmats.append(mt)
        #
        # engine.models.loadBox("pushboxmodel", [55, 3, 3], 2)
        # self.pushbox1 = self.scene1.addModel('pushboxmodel', 'pushbox1', [140, 6, 0], [0, 0, 0], 4, mass=50)
        # self.pushbox2 = self.scene1.addModel('pushboxmodel', 'pushbox2', [-140, 6, 0], [0, 0, 0], 4, mass=50)
        #
        # engine.models.loadPlane("planemodelbig", 1, 15)
        # engine.models.loadPlane("planemodel1", 1, 5)
        # IMPORTANT!: High number of segments (tesselation) is needed for large objects. See:
        # https://www.opengl.org/archives/resources/features/KilgardTechniques/oglpitfall/
        # 2. Poor Tessellation Hurts Lighting
        # self.plane1 = self.scene1.addModel('planemodelbig', 'plane1', [0, 0, 0], [-90, 0, 0], 1200)
        # mt = self.plane1._materials[0]
        # mt.specularPower = 50
        # mt.useDiffuseTexture = True
        # mt.useNormalMapTexture = True
        # mt.normalMapTextureID = 'defNI'
        # mt.textureRepeat = 40
        # self.bumpymats.append(mt)
        # self.texmats.append(mt)

        # self.planer = self.scene1.addModel('planemodel1', 'planer', [300, 0, 0], [0, -80, 0], 280)
        # mt = self.planer._materials[0]
        # self.planer.moveUp(self.planer.getSize().y)
        # mt.useNormalMapTexture = True
        # mt.normalMapTextureID = 'testN'
        # mt.textureRepeat = 10
        # self.bumpymats.append(mt)

        # self.planel = self.scene1.addModel('planemodel1', 'planel', [-300, 0, 0], [0, 80, 0], 280)
        # self.planel.moveUp(self.planer.getSize().y)
        # self.planel._materials[0] = mt
        #
        # self.planef = self.scene1.addModel('planemodel1', 'planef', [0, 0, -200], [0, 0, 0], 280)
        # self.planef.moveUp(self.planer.getSize().y)
        # self.planef._materials[0] = mt

        # engine.models.loadModel(self.tubeMODEL, "tubemodel")

        # self.tube = self.scene1.addModel('tubemodel', 'tube1', [-150, 20, 0], [0, 0, 0], 7)
        # self.tube.setAnimation(self.tube.getAnimationsList()[0], True)
        # self.tube.physicsBody.isDynamic = True

        # self.tube2 = self.scene1.addModel('tubemodel', 'tube2', [0, 70, 0], [0, 0, 0], 7,
        # shape=bodyShapesEnum.box)
        # self.tube2.physicsBody.isDynamic = True
        #
        # self.tube3 = self.scene1.addModel('tubemodel', 'tube3', [50, 0, 0], [0, 0, 0], 7,
        # shape=bodyShapesEnum.sphere)
        # self.tube3.setAnimation(self.tube3.getAnimationsList()[1], True)
        # self.tube3.physicsBody.isDynamic = True

        # engine.models.loadModel(self.planepath, "planemodel")
        # self.plane = self.scene1.addModel('planemodel', 'plane0', [0, 0, 0], [1, 0, 1], 2)
        # # self.plane.visible = False
        # mat = self.plane.getMaterialByIndex(0)
        # mat.specularPower = 20000000000
        # # mat.diffuseTextureID = 'grass'
        # mat.useDiffuseTexture = True
        # mat.textureRepeat = self.plane.uniformScale * 3

        # self.planef = self.scene1.addModel('planemodel1', 'planef', [0, 0, -200], [0, 0, 0], 280)
        # self.sphere1 = self.scene1.addModel('mainspheremodel', 'sphere1', [0, 10, 0], [0, 0, 0], 4, mass=8)
        # self.planel = self.scene1.addModel('planemodel1', 'planel', [-300, 0, 0], [0, 80, 0], 280)
        # self.box1 = self.scene1.addModel('boxmodel', 'box1', [0, 90, 0], [0, 90, 0], 5, mass=7)
        # self.ballcount = 0
        # self.boxcount = 1
        # self.pushbox1 = self.scene1.addModel('pushboxmodel', 'pushbox1', [140, 6, 0], [0, 0, 0], 4, mass=50)
        # self.pushbox2 = self.scene1.addModel('pushboxmodel', 'pushbox2', [-140, 6, 0], [0, 0, 0], 4, mass=50)
        # self.addLights()

    def addLights(self):
        print('Adding Lights')
        self.dlight = self.scene1.addLight(0, vec3(1.0, 1.0, 1.0), vec3(45, 45, 0))
        self.dlight.color = vec3(.9, .9, 0.7)
        self.createLightSphere(2, vec3(-190.0, 110.0, 0.0), vec3(1.0, 0.0, 0.0))
        self.createLightSphere(2, vec3(0.0, 70.0, -150.0), vec3(1.0, 1.0, 0.0))
        self.createLightSphere(1, vec3(-50.0, 30.0, 290.0), vec3(0.0, 1.0, 0.0))
        self.createLightSphere(2, vec3(0.0, 150.0, 0.0), vec3(.50, .0, 1.0))
        self.createLightSphere(1, vec3(280.0, 30.0, 10.0), vec3(0.0, .0, 1.0))

    def dropBox(self):
        try:
            self.boxcount += 1
            sceneid = 'box' + str(self.boxcount)
            pos = list(self.camera.position)
            pos[1] += 20
            box = self.scene1.addModel('boxmodel', sceneid, pos, [0, 0, 0], 1)
            mats = box._materials[0]
            mats.specularPower = 20
            # mats.useDiffuseTexture = True
            mats.diffuseColor = box.debugColor
            box.physicsBody.isDynamic = True
            box.physicsBody.punchCenter(250, self.camera.forward)
        except Exception as ex:
            print(ex.message)

    def dropBall(self):
        try:
            sceneid = 'ball' + str(self.ballcount)
            pos = list(self.camera.position)
            pos[1] += 20
            ball = self.scene1.addModel('spheremodel', sceneid, pos, [0, 0, 0], 1)
            mat = ball._materials[0]
            mat.specularPower = 50
            mat.useDiffuseTexture = True
            mat.diffuseTextureID = 'earth'
            ball.physicsBody.isDynamic = True
            ball.physicsBody.punchCenter(250, self.camera.forward)
            self.ballcount += 1
        except Exception as ex:
            print(ex.message)

    def mouseMove(self, ev):
        if ev.eventName == 'motion':
            if self.window.hasFocus():
                r = 1.0 / 10 if self.window.mouseLock else 1
                self.camera.rotateY(-ev.xRel * r)
                self.camera.rotateX(ev.yRel * r)
        elif ev.eventName == 'buttonDown':
            if ev.button == 'right':
                self.dropBox()
            elif ev.button == 'left':
                self.dropBall()
                # else:
                #     print ev

    def keydown(self, e):
        if e.name == 'keyUp':
            return
        # print "Key pressed=", e.keyName
        if e.keyName.__contains__('shift'):
            self.window.mouseLock = not self.window.mouseLock
        if e.keyName == 'escape':  # ESC
            self.close()
        if e.keyName == 'f8':
            self.window.renderingMan.debugModeActive = not self.window.renderingMan.debugModeActive
        if e.keyName == 'f4':
            self.window.renderingMan.showAsWireframe = not self.window.renderingMan.showAsWireframe
        if e.keyName == 'space':
            self.window.setFullScreen(not self.window.isFullScreen())
        if e.keyName.__contains__('ctrl'):
            self.dorot = not self.dorot
        if e.keyName == 'f1':
            np = [round(d, 3) for d in self.camera.position]
            logger.log('Camera pos:{0}'.format(str(np)), logLevelsEnum.info)
            logger.log('Poligons drawn:{}'.format(self.window.renderingMan.poligonsDrawnThisUpdate),
                       logLevelsEnum.info)
            logger.log('Boxes: ' + str(self.boxcount), logLevelsEnum.debug)
            logger.log('Balls: ' + str(self.ballcount), logLevelsEnum.debug)
        if e.keyName == 'g':
            val = self.window.gamma
            print ('old gamma:' + str(val))
            if val <= 1.8:
                self.window.gamma = 2.5
            else:
                self.window.gamma = 1.7
            print ('new gamma:' + str(self.window.gamma))
        if e.keyName == 'right':
            self.scene1.physics.step(50)
        if e.keyName == 'left':
            self.scene1.physics.paused = False
        if e.keyName == 'p':
            self.box1.physicsBody.punchCenter(250, [1, .5, 0])
        if e.keyName == 'l':
            self.dlight.enabled = not self.dlight.enabled
        if e.keyName == 'n':
            for mat in self.bumpymats:
                mat.useNormalMapTexture = not mat.useNormalMapTexture
        if e.keyName == 't':
            for mat in self.texmats:
                mat.useDiffuseTexture = not mat.useDiffuseTexture


if __name__ == '__main__':
    runDemo(Demo(), 'Physics and light Demo')
