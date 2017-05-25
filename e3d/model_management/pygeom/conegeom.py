import math

from cycgkit.cgtypes import vec3, vec4

from .Geometry import Geometry
from .face3 import Face3
from .cylindergeom import CylinderGeometry

# Based on ConeGeometry.js from https://github.com/mrdoob/three.js


class ConeGeometry(CylinderGeometry):
    def __init__(self, radius, height, radialSegments, heightSegments, openEnded, thetaStart, thetaLength):
        CylinderGeometry.__init__(self, 0.0000001, radius, height, radialSegments, heightSegments, openEnded, thetaStart,
                                           thetaLength)
        self.type = 'ConeGeometry'

        self.parameters = {
            'radius': radius,
            'height': height,
            'radialSegments': radialSegments,
            'heightSegments': heightSegments,
            'openEnded': openEnded,
            'thetaStart': thetaStart,
            'thetaLength': thetaLength
        }
