from __future__ import print_function
from ..commonValues import *
from bullet.bullet import *



class ScenePhysics(object):
    def __init__(self, gravity, resolution):
        self._resolution = resolution
        self.__paused = False
        self._requiredSteppedTimelapse = 0
        self._bodies = {}
        # broadphase = getBroadphaseHandle()
        # collisionConfiguration = CollisionConfiguration()
        # dispatcher = btCollisionDispatcher(collisionConfiguration)
        # solver = SequentialImpulseConstraintSolver()
        # If you want to use soft bodies, use btSoftRigidDynamicsWorld, otherwise use btDiscreteDynamicsWorld
        # http://stackoverflow.com/questions/2474939/bullet-physics-when-to-choose-which-dynamicsworld?rq=1
        self.dynamicsWorld = DiscreteDynamicsWorld()
        self.dynamicsWorld.setGravity(Vector3(0, gravity * 100, 0))

    def _setPaused(self, value):
        self.__paused = value

    def _getPaused(self):
        return value

    paused = property(_getPaused, _setPaused)

    def step(self, miliseconds):
        self.__paused = True
        self._requiredSteppedTimelapse = miliseconds / 1000.0

    def _setRes(self, value):
        if value > 0:
            raise ValueError('Resolution for physics world must be higer than 0.')
        self._resolution = value

    def _getRes(self):
        return self._resolution

    resolution = property(_getRes, _setRes)

    def _setGrav(self, value):
        self.__grav = value
        self.dynamicsWorld.setGravity(Vector3(0, value * 100, 0))

    def _getGrav(self):
        return self.__grav

    gravity = property(_getGrav, _setGrav)

    def addRigidObject(self, physicsBody):
        self._bodies[id(physicsBody.body)] = physicsBody
        self.dynamicsWorld.addRigidBody(physicsBody.body)

    def removeRigidObject(self, physicsBody):
        self._bodies.pop(id(physicsBody.body))
        self.dynamicsWorld.removeRigidBody(physicsBody.body)

    def update(self, elapsedTime):
        if self._requiredSteppedTimelapse != 0:
            elapsedTime = self._requiredSteppedTimelapse
            self._requiredSteppedTimelapse = 0
        elif self.__paused:
            return
        if elapsedTime > 0:
            fixedStep = (1.0 / float(self._resolution))
            originalFixedStep = fixedStep
            steps = int(elapsedTime / fixedStep) + 1
            if steps >= 20:
                fixedStep = 1 / 60.0
            stepsNeeded = self.dynamicsWorld.stepSimulation(elapsedTime, steps, fixedStep)
            if steps > stepsNeeded and originalFixedStep != fixedStep:
                self.dynamicsWorld.stepSimulation(0.05, steps, 1.0 / float(self._resolution))
                # print ('max', steps, 'needed', stepsNeeded)

    def castRay(self, fromPos, toPos):
        """

        @rtype : rayResult
        """
        try:
            rayResult = self.dynamicsWorld.rayTestClosest(Vector3(fromPos[0], fromPos[1], fromPos[2]),
                                                   Vector3(toPos[0], toPos[1], toPos[2]))

            if rayResult:
                return CastRayResult(rayResult, self)
            else:
                return None
        except Exception as ex:
            print(ex.message)


class CastRayResult(object):
    def __init__(self, btRes, scenePhys):
        """

        @type scenePhys: ScenePhysics
        """
        self.physicsObject = scenePhys._bodies.get(id(btRes.collisionObject))
        if not self.physicsObject:
            raise RuntimeError('Body not found in World.')
        self.hitPosition = bulletVectorToList(btRes.hitPointWorld)
        self.hitNormal = bulletVectorToList(btRes.hitNormalWorld)
        self.filterGroup = btRes.collisionFilterGroup
        self.filterMask = btRes.collisionFilterMask
        self.flags = btRes.flags
        self.hitFraction = btRes.closestHitFraction


class bodyShapesEnum(object):
    _allShapes = ['Box2dShape', 'BoxShape', 'BvhTriangleMeshShape', 'CapsuleShape', 'CollisionShape', 'ConvexShape',
                  'CylinderShape', 'CylinderShapeX', 'CylinderShapeZ', 'SphereShape', 'StaticPlaneShape']
    box2d = _allShapes[0]
    box = _allShapes[1]
    capsule = _allShapes[3]
    convex = _allShapes[5]
    cylinder = _allShapes[6]
    sphere = _allShapes[9]
    staticPlane = _allShapes[10]
    auto = 'auto'

    def __init__(self):
        pass


class rigidObject(object):
    def __init__(self, bObj, shape=bodyShapesEnum.box, mass=None, size=None, isDynamic=False):
        """

        @param bObj:
        @type bObj: Base3DObject
        @return:
        @rtype: rigidObject
        """
        if size is None:
            size = [1, 1, 1]
        elif isinstance(size, list) and len(size) == 1:
            size = [size[0]] * 3
        if mass is None:
            mass = defaultMass

        self.__isDyn = isDynamic
        self.__mass = mass
        self._phyUpdWait = 0

        self.size = listToBulletVector(size)

        self.btShape = self._build_btShape(shape)

        inertia = Vector3(0, 0, 0)
        self.btShape.calculateLocalInertia(mass, inertia)
        self._base3DObject = bObj
        fpos = bObj._position + bObj._pOffset
        transform = btTransformFromPosRotMat(fpos, bObj._rotationMatrix)
        # self._motion = DefaultMotionState(transform)
        self._motion = e3dMotionState(transform)
        self._motion.bObject = bObj
        self._isTempKin = False
        self.body = RigidBody(self._motion, self.btShape, mass)
        self.body.setRestitution(0.7)  # todo: add bounciness property/parameters
        # self.body.setFriction(1)
        # self.body.linearSleepingThreshold *= 10e9000
        # self.body.angularSleepingThreshold *= 10e9000
        self._beyondBoundary = False

    def _getDynState(self):
        return self.__isDyn

    def _setDynState(self, value):
        """

        @type value: bool
        """
        self.__isDyn = value
        if value:
            dmass = self.__mass
        else:
            dmass = 0
        self._reBuildMass(dmass)

    isDynamic = property(_getDynState, _setDynState)

    def _getMass(self):
        return self.__mass

    def _setMass(self, value):
        self.changeMass(value)

    mass = property(_getMass, _setMass)

    def _reBuildMass(self, mass):
        inertia = Vector3(0, 0, 0)
        self.btShape.calculateLocalInertia(mass, inertia)
        self.body.setMassProps(mass, inertia)
        self.body.updateInertiaTensor()

    def changeMass(self, mass):
        self._reBuildMass(mass)
        self.__mass = mass

    def changeShape(self, shape):
        self.btShape = self._build_btShape(shape)
        self.body.setCollisionShape(self.btShape)

    def _build_btShape(self, shape):
        enum = bodyShapesEnum
        size = self.size
        if shape == enum.box:
            bShape = BoxShape(size)
        elif shape == enum.sphere:
            bShape = SphereShape((size.x + size.z + size.y) / 3.0)
        elif shape == enum.capsule:
            bShape = CapsuleShape((size.x + size.z) / 2.0, size.y)
        # elif shape == enum.staticPlane:
        # bShape = StaticPlaneShape(size, 0)
        else:
            raise NotImplementedError('Shape \'{}\') not yet implemented. Please report it.'.format(shape))

        return bShape

    def _setAsKinematic(self):
        self.body.setCollisionFlags(self.body.getCollisionFlags() | CF_KINEMATIC_OBJECT)  # | CF_NO_CONTACT_RESPONSE
        # to avoid pushing behavoir
        self._reBuildMass(0)
        # self.body.setLinearVelocity(Vector3(0, 0, 0))
        # self.body.setAngularVelocity(Vector3(0, 0, 0))
        self.body.setActivationState(DISABLE_DEACTIVATION)
        self._isTempKin = True

    def _setAsDynamic(self):
        # http://www.bulletphysics.org/Bullet/phpBB3/viewtopic.php?f=9&t=4517
        self.body.setCollisionFlags(CF_STATIC_OBJECT)  # dynamic?
        if self.__isDyn:
            self._reBuildMass(self.__mass)
            self.body.setActivationState(ACTIVE_TAG)  # TODO: may never sleep. How to fix?
        else:
            self._reBuildMass(0)
            self.body.setActivationState(WANTS_DEACTIVATION)  # TODO: may never sleep. How to fix?

        # self.body.setLinearVelocity(Vector3(0, 0, 0))
        # self.body.setAngularVelocity(Vector3(0, 0, 0))
        self._isTempKin = False

    def pushCenter(self, amount, dir):
        x, y, z = dir
        fvec = Vector3(x, y, z) * amount
        self.body.applyCentralForce(fvec)

    def punchCenter(self, amount, dir):
        x, y, z = dir
        fvec = Vector3(x, y, z) * amount
        self.body.applyCentralImpulse(fvec)


class e3dMotionState(overridableMotionState):
    # def setWorldTransform(self, transform):
    #     """
    #     Called from bullet to set 3d object transformation.
    #     @param transform:
    #     @type transform: Transform
    #     @return:
    #     @rtype: None
    #     """
    #     try:
    #         ob = self.bObject
    #         ob._dirtyP = True
    #     except Exception as ex:
    #         self._engine.log('e3dMotionState/setWorldTransform error: ' + ex.message)

    def _setKinematicState(self, pos, rotMat):
        # todo: add offset
        self.worldTrans = btTransformFromPosRotMat(pos, rotMat)
        # # rigidBody.setCenterOfMassTransform(myMotionState.getWorldTransform() ?????????

    def getWorldTransform(self):
        """
        Sends info to bullet with 3d object transformation.
        @return:
        @rtype: Transform
        """
        return self.worldTrans

    def __init__(self, transform):
        """


        @rtype : e3dMotionState
        """
        self.worldTrans = transform
        self.bObject = None