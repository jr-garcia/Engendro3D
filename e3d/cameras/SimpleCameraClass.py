from copy import copy
from cycgkit.cgtypes import *

from ..Base3DObjectClass import Base3DObject
from ..LoggerClass import logger, logLevelsEnum
from ..physics_management.physicsModule import bodyShapesEnum


class SimpleCamera(Base3DObject):
    def get_zFar(self):
        return self._p_zFar

    def set_zFar(self, value):
        self._p_zFar = value

    zFar = property(fget=get_zFar, fset=set_zFar)

    def get_zNear(self):
        return self._p_zNear

    def set_zNear(self, value):
        self._p_zNear = value

    zNear = property(fget=get_zNear, fset=set_zNear)

    def get_FOV(self):
        return self._p_fov

    def set_FOV(self, value):
        self._p_fov = value
        self.updateFOV(self.width, self.height)

    FOV = property(fget=get_FOV, fset=set_FOV)

    # def get_lookAt(self):
    # return self.lookAt
    #
    # lookAt = property(fget=get_lookAt)

    def __init__(self, position, rotation, size=None, shape=bodyShapesEnum.capsule, fov=45, zFar=5000, zNear=1, ID=''):
        """
        Basic Camera
        @type position: list
        @type size: list
        @type rotation: list
        @type sceneWidth: int
        @type sceneHeight: int
        @rtype : SimpleCamera
        """
        if not size:
            size = [1, 5, 1]

        super(SimpleCamera, self).__init__(position, rotation, 1, size, shape, 1.0, True, ID)
        self.__sw = 0
        self.__sh = 0
        self._vm = None
        self.__lastpos = None
        self.__lastrot = None
        self._p_fov = fov
        self._p_zFar = zFar
        self._p_zNear = zNear
        self.lookAtConstant = vec3(0, 0, 1)
        self.upConstant = vec3(0, 1, 0)
        self.lookAt = self.lookAtConstant
        self.lookAtFixed = self.lookAtConstant
        self.projectionMatrix = None

        self._update(True)

    def updateFOV(self, width, height):
        try:
            self.projectionMatrix = mat4.perspective(self._p_fov, float(width) / float(height),
                                                     self._p_zNear, self._p_zFar)
        except Exception as ex:
            logger.log(str(ex), 0)
            self.projectionMatrix = mat4.perspective(45, 640.0 / 480.0, 0.1, 500)

    def _update(self, force=False):
        """
         Updates the transformation (view matrix) of the camera, and returns it.
        @rtype : mat4
        """
        if super(SimpleCamera, self)._update() or force:
            self.lookAtFixed = self._rotationMatrix * self.lookAtConstant
            self.lookAt = self._position + self.lookAtFixed
            self._vm = self.lookAtRH(self._position, self.lookAt, self._rotationMatrix * self.upConstant)
            self.__lastpos = copy(self._position)
            self.__lastrot = copy(self._rotation)

        return self._vm

    @staticmethod
    def lookAtRH(eye, target, up):
        # http://devmaster.net/posts/7255/glulookat-alternative-and-building-look-at-matrix
        # http://webglfactory.blogspot.mx/2011/06/how-to-create-view-matrix.html

        try:
            vz = vec3(target - eye).normalize()
            vx = vec3(vec3(vz).cross(up)).normalize()
            vy = vec3(vx).cross(vz)
            v4e = vec4(eye)
            v4e.w = 1

            ViewMatrix = mat4(
                vec4(vx),
                vec4(vy),
                vec4(-vz),
                # vec4(0, 0, 0, 1))
                v4e)
            return ViewMatrix.inverse()  # * mat4.translation(eye)

        except Exception as ex:
            raise Exception('lookAtRH error: ' + ex.message)
