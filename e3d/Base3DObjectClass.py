from cycgkit.cgtypes import *
from .commonValues import *

from .physics_management.physicsModule import rigidObject, bodyShapesEnum

from abc import ABCMeta, abstractmethod


class Attachable(object):
    def _getParent(self):
        return self._parent

    parent = property(_getParent)

    def __init__(self):
        self._children = []
        self._parent = None

    def attachTo(self, parent):
        if parent is not None:
            if issubclass(type(parent), Attachable):
                if self._parent is not None:
                    try:
                        self._parent._children.pop(self._parent._children.index(self._children))
                    except:
                        pass
                parent._children.append(self)
                parent._dirty = True
                self._parent = parent
            else:
                raise TypeError('"parent" object can\'t receive attached objects.')
        else:
            raise AttributeError('"parent" object is None.')


class Base3DObject(Attachable):
    class animationState(object):
        stopped = 0
        playing = 1
        paused = 2

        def __init__(self):
            self.stopped = 0
            self.playing = 1
            self.paused = 2

    """
        Abstract.
        Base type for all 3D objects.
        @rtype : Base3DObject
    """
    __metaclass__ = ABCMeta

    def __init__(self, position, rotation, uniformScale, size, shape=bodyShapesEnum.box, mass=None, isDynamic=False,
                 ID='', offset=None):
        if not offset:
            offset = [0, 0, 0]
        super(Base3DObject, self).__init__()
        self.debugColor = []
        self.ID = ID
        self._transformation = None
        self._forwardConstant = vec3(0, 0, 1)
        self._position = vec3(position)
        self._scale = vec3(uniformScale)
        self._rotation = vec3(rotation)
        self._rotationMatrix = None
        self._positionMatrix = None
        self._scaleMatrix = None
        self.visible = True
        self._dirty = True
        self._dirtyP = False
        self._animationID = ''
        self._animationStartupTime = -1
        self._animationPausedTime = 0
        self._animLastPauseStartup = -1
        self._animationLastPlayedFrame = -1
        self.animState = Base3DObject.animationState.stopped
        # Callbacks>>>>>>>>>>>>>>>>>
        self.onUpdate_Callback = None
        self.onClick_Callback = None
        self.onMouseIn_Callback = None
        self.onMouseOut_Callback = None
        self.onKeyPress_Callback = None
        self.onKeyRelease_Callback = None

        self._updateTransformation()
        self._dirty = False

        if size is None:  # todo:check he need of this
            size = [1, 1, 1]
        elif (isinstance(size, list) or isinstance(size, tuple)) and len(size) != 3:
            size = [size[0]] * 3
        elif isinstance(size, int) or isinstance(size, float):
            size = [size] * 3

        self._size = vec3(size)

        if uniformScale != 1:
            fs = [s * float(uniformScale) for s in size]
            noff = [s * float(uniformScale) for s in offset]
        else:
            fs = size
            noff = offset

        self._pOffset = noff

        self.physicsBody = None
        # self.physicsBody = rigidObject(self, shape, mass, fs, isDynamic)

        # <<<<<<<<<<<<<<<<<<<<<<<<<<

    def __repr__(self):
        return '\'{}\''.format(self.ID)

    def getSize(self):
        return self._scale[0] * self._size

    def _getAbsolutePosition(self):
        """

        @rtype : vec3
        """
        return self._position

    def _setAbsolutePosition(self, value):
        """

        @type value: vec3
        """
        self._position = vec3(value)
        self._dirty = True

    position = property(fget=_getAbsolutePosition, fset=_setAbsolutePosition)

    def _getRotation(self):
        """

        @rtype : list
        """
        return self._rotation

    def _setRotation(self, value):
        """

        @type value: list
        """
        self._rotation = vec3(value)
        self._dirty = True

    rotation = property(fget=_getRotation, fset=_setRotation)

    def _getTransformation(self):
        return self._transformation

    transformation = property(_getTransformation)

    def _updateTransformation(self):
        self._updateRotationMatrix()
        self._positionMatrix = mat4.translation(self._position)
        self._scaleMatrix = mat4.scaling(self._scale)
        self._transformation = self._positionMatrix * self._rotationMatrix * self._scaleMatrix

    @staticmethod
    def _buildRotMat(rx, ry, rz):
        return mat4.rotation(rz * radian, vec3(0, 0, -1)).rotate(ry * radian, vec3(0, 1, 0)).rotate(rx * radian,
                                                                                                    vec3(1, 0, 0))

    @staticmethod
    def _fixrot(l):
        while l > 360:
            l = 360 - l
        while l < 0:
            l = 360 + l
        if l == 360:
            l = 0

        return l

    def _updateRotationMatrix(self):
        self._rotationMatrix = self._buildRotMat(self._rotation.x, self._rotation.y, self._rotation.z)

    def rotateX(self, angle):
        self._rotation.x += angle
        self._dirty = True

    def rotateY(self, angle):
        self._rotation.y += angle
        self._dirty = True

    def rotateZ(self, angle):
        self._rotation.z += angle
        self._dirty = True

    def addMove(self, vector):
        """
        Movement trough a vector
        @rtype : None
        @param vector:
        @type vector: vec3
        """
        self._updateRotationMatrix()
        tv = self._rotationMatrix * vector
        self._position = self._position + tv
        self._dirty = True

    def moveForward(self, amount):
        """
        @rtype : None
        @param amount:
        @type amount: int
        """
        self.addMove(vec3(0, 0, amount))

    def moveBackward(self, amount):
        """
            @rtype : None
            @param amount:
            @type amount: int
            """
        self.addMove(vec3(0, 0, -amount))

    def moveUp(self, amount):
        """
            @rtype : None
            @param amount:
            @type amount: int
            """
        tv = vec3(0, amount, 0)
        self.addMove(tv)

    def moveDown(self, amount):
        """
            @rtype : None
            @param amount:
            @type amount: int
            """
        tv = vec3(0, -amount, 0)
        self.addMove(tv)

    def moveLeft(self, amount):
        """
            @rtype : None
            @param amount:
            @type amount: int
            """
        tv = vec3(amount, 0, 0)
        self.addMove(tv)

    def moveRight(self, amount):
        """
            @rtype : None
            @param amount:
            @type amount: int
            """
        tv = vec3(-amount, 0, 0)
        self.addMove(tv)

    def _setUniformScale(self, intScale):
        if not isinstance(intScale, int):
            raise TypeError('scale must be a sinle int')
        self._scale = [intScale, intScale, intScale]

    def _getUniformScale(self):
        return self._scale[0]

    uniformScale = property(_getUniformScale, _setUniformScale)

    def _update(self):
        # Todo: implement calbacks
        if self._dirty:
            self._updateTransformation()
            self._dirty = False
            for c in self._children:
                c._update()
            return True
        else:
            return False

    def setAnimation(self, id, start=False):
        self._animationID = id
        if start:
            self.animState = Base3DObject.animationState.playing
        else:
            self.animState = Base3DObject.animationState.stopped

    def playAnimation(self):
        self.animState = Base3DObject.animationState.playing

    def pauseAnimation(self):
        self.animState = Base3DObject.animationState.paused

    def stopAnimation(self):
        self.animState = Base3DObject.animationState.stopped
        self._animationStartupTime = -1

    def _getFrwd(self):
        frwd = self._rotationMatrix * self._forwardConstant
        return frwd

    forward = property(_getFrwd)


class DefaultObjectParameters(object):
    def __init__(self):
        self.model = None
        self.view = None
        self.projection = None

        self.ModelView = None
        self.ModelViewProjection = None
        self.ModelProjection = None
        self.ModelInverse = None
        self.ModelInverseTranspose = None
        self.ModelViewInverse = None
        self.ModelViewInverseTranspose = None
        self.NormalMatrix = None
        self.hasBones = False

    def construct(self):
        self.ModelView = self.view * self.model
        self.ModelViewProjection = self.projection * self.ModelView
        self.ModelInverse = self.model.inversed()
        self.ModelInverseTranspose = self.ModelInverse.transposed()
        self.ModelViewInverse = self.ModelView.inversed()
        self.ModelViewInverseTranspose = self.ModelViewInverse.transposed()
        self.ModelProjection = self.projection * self.model
        self.NormalMatrix = self.ModelView.getMat3().inversed().transposed()
        # todo:convert each field into property to multiply only when needed.
