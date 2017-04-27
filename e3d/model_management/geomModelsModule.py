from ..commonValues import radian
from cycgkit.cgtypes import mat4, vec3
from cycgkit.boundingbox import BoundingBox
# from cycgkit.trimeshgeom import TriMeshGeom
from pygeom.spheregeom import SphereGeometry
# from cgkit.boxgeom import BoxGeom
# from cgkit.plane import PlaneGeom


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
    sp = BoxGeom(sx, sy, sz, segmentsX, segmentsY, segmentsZ)
    return _getObjVertIndBBox(sp)


def _getPlaneVertIndBBox(sx, sy, segmentsX, segmentsY):
    sp = PlaneGeom(sx, sy, segmentsX, segmentsY)
    return _getObjVertIndBBox(sp)


def getObjectInfo(gtype, attDict):
    """

    @type gtype: geomTypeEnum
    """
    if gtype == geomTypeEnum.sphere:
        rad = attDict.get('radius', 4.0)
        segU = attDict.get('segmentsU', 16)
        segV = attDict.get('segmentsV')
        if segV is None:
            segV = segU
        obTup = _getSphereVertIndBBox(rad, segU, segV)
    elif gtype == geomTypeEnum.box:
        size = attDict.get('size', [1.0, 1.0, 1.0])
        if type(size) in [int, float]:
            size = [size] * 3
        elif isinstance(size, list) and len(size) in [1, 3]:
            if len(size) == 1:
                size = [size[0], size[0], size[0]]
        else:
            raise TypeError('Size should be a 3 element list of numbers, or a single number.')
        sx, sy, sz = size
        segX = attDict.get('segmentsX', 1)
        segY = attDict.get('segmentsY')
        segZ = attDict.get('segmentsZ')
        if segY is None:
            segY = segX
        if segZ is None:
            segZ = segX
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
