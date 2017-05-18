from numpy.core.umath import cos

from ..Base3DObjectClass import Base3DObject
from cycgkit.cgtypes import vec3, vec4
from ..backends.base_backend import ShaderStruct


class lightTypesEnum(object):
    directional = 0
    point = 1
    spot = 2


class light(Base3DObject):
    def __init__(self, type, position=None, rotation=None, ID=''):
        """


        @rtype : light
        """
        self.spotIntensity = 0.0
        self.color = vec3(1, 1, 1)
        self.spotRange = .50
        self.type = lightTypesEnum.directional
        self.attenuation = 250.0
        if not rotation:
            rotation = vec3(0, 0, 0)
        if not position:
            position = vec3(10, 0, 0)
        super(light, self).__init__(position, rotation, 1, vec3(1, 1, 1), ID=ID)
        self._forwardConstant = vec3(0, -1, 0)
        self.type = type
        self._struct = ShaderStruct()
        self.enabled = True

    def _getShaderStruct(self, view):
        st = self._struct
        st['type'] = self.type
        st['color'] = self.color
        st['viewDirection'] = view.getMat3() * self.forward
        st['attenuation'] = float(self.attenuation)
        x, y, z = self._position
        vx, vy, vz, vw = (view * vec4(x, y, z, 1.0))
        st['viewPosition'] = vec3(vx, vy, vz)
        st['spotIntensity'] = float(self.spotIntensity)
        st['spotRange'] = float(cos(self.spotRange))

        return st

    def __repr__(self):
        return super(light, self).__repr__() + ' type:{}'.format(self.type)
