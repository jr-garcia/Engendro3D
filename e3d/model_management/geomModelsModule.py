from ..commonValues import radian
from cycgkit.cgtypes import mat4, vec3
from cycgkit.boundingbox import BoundingBox

from pygeom.spheregeom import SphereGeometry
from pygeom.boxgeom import BoxGeometry

class geomTypeEnum(object):
    sphere = 'sphere'
    box = 'box'
    capsule = 'capsule'
    plane = 'plane'


def _getObjVertIndBBox(geomObj):
    vert = geomObj.vertices
    ind = []

    for f in geomObj.faces:
        ind.append(f.abcVec3())

    bbox = geomObj.boundingBox = BoundingBox()
    for v in vert:
        bbox.addPoint(v)
    return vert, ind, bbox


def _getSphereVertIndBBox(radius, segmentsU, segmentsV):
    sp = SphereGeometry(radius, segmentsU, segmentsV)
    return _getObjVertIndBBox(sp)


def _getBoxVertIndBBox(sx, sy, sz, segmentsX, segmentsY, segmentsZ):
    sp = BoxGeometry(sx, sy, sz, segmentsX, segmentsY, segmentsZ)
    return _getObjVertIndBBox(sp)


def _getPlaneVertIndBBox(sx, sy, segmentsX, segmentsY):
    sp = PlaneGeom(sx, sy, segmentsX, segmentsY)
    return _getObjVertIndBBox(sp)


def getObjectInfo(gtype, attDict):
    """

    @type gtype: geomTypeEnum
    """
    if gtype == geomTypeEnum.sphere:
        rad = attDict.get('radius')
        segU = attDict.get('segmentsU')
        segV = attDict.get('segmentsV')
        obTup = _getSphereVertIndBBox(rad, segU, segV)
    elif gtype == geomTypeEnum.box:
        sx, sy, sz = attDict.get('size')
        segX = attDict.get('segmentsX')
        segY = attDict.get('segmentsY')
        segZ = attDict.get('segmentsZ')
        obTup = _getBoxVertIndBBox(sx, sy, sz, segX, segY, segZ)
    elif gtype == geomTypeEnum.plane:
        sx, sy = attDict.get('size', [1.0, 1.0])
        segX = attDict.get('segmentsX', 1)
        segY = attDict.get('segmentsY')
        if segY is None:
            segY = segX
        obTup = _getPlaneVertIndBBox(sx, sy, segX, segY)
    else:
        raise NotImplementedError('oops :(', gtype, attDict)

    return obTup
