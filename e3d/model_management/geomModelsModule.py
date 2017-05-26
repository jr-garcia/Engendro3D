from ..commonValues import radian
from cycgkit.cgtypes import mat4, vec3
from cycgkit.boundingbox import BoundingBox

from .pygeom.spheregeom import SphereGeometry
from .pygeom.boxgeom import BoxGeometry
from .pygeom.planegeom import PlaneGeometry
from .pygeom.torusknotgeom import TorusKnotGeometry
from .pygeom.cylindergeom import CylinderGeometry
from .pygeom.conegeom import ConeGeometry


class geomTypeEnum(object):
    sphere = 'sphere'
    box = 'box'
    capsule = 'capsule'
    plane = 'plane'
    torusKnot = 'torusKnot'
    icosphere = 'icosphere'
    cylinder = 'cylinder'
    cone = 'cone'


def _getObjData(geomObj):
    vert = geomObj.vertices
    ind = []
    uvs = [vec3(0, 0, 0)] * len(vert)

    for i in range(len(geomObj.faces)):
        f = geomObj.faces[i]
        ind.append(f.abcVec3())
        uvs[int(f.a)] = geomObj.faceVertexUvs[i][0]
        uvs[int(f.b)] = geomObj.faceVertexUvs[i][1]
        uvs[int(f.c)] = geomObj.faceVertexUvs[i][2]

    bbox = geomObj.boundingBox = BoundingBox()
    for v in vert:
        bbox.addPoint(v)

    return vert, ind, bbox, uvs


def getObjectInfo(gtype, attDict):
    """

    @type gtype: geomTypeEnum
    @param attDict: 
    @type attDict: dict
    """
    if gtype == geomTypeEnum.sphere:
        rad = attDict.get('radius')
        segU = attDict.get('segmentsU')
        segV = attDict.get('segmentsV')
        geomObj = SphereGeometry(rad, segU, segV)
    elif gtype == geomTypeEnum.box:
        sx, sy, sz = attDict.get('size')
        segX = attDict.get('segmentsX')
        segY = attDict.get('segmentsY')
        segZ = attDict.get('segmentsZ')
        geomObj = BoxGeometry(sx, sy, sz, segX, segY, segZ)
    elif gtype == geomTypeEnum.plane:
        sx = attDict.get('sizeX')
        sz = attDict.get('sizeZ')
        segX = attDict.get('segmentsX')
        segZ = attDict.get('segmentsZ')
        geomObj = PlaneGeometry(sx, sz, segX, segZ)
    elif gtype == geomTypeEnum.torusKnot:
        geomObj = TorusKnotGeometry(*attDict)
    elif gtype == geomTypeEnum.cylinder:
        geomObj = CylinderGeometry(*attDict)
    elif gtype == geomTypeEnum.cone:
        geomObj = ConeGeometry(*attDict)
    else:
        raise NotImplementedError('geometryType not found :(', gtype, attDict)

    return _getObjData(geomObj)
