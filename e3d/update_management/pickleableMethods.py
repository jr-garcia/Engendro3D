from cycgkit.cgtypes import vec3, mat4

from ..commonValues import radian
from ..Base3DObjectClass import Base3DObject


def updateModelTransformation(args):
    ID, position, rotation, scale = args
    positionMatrix = mat4.translation(position)
    # x = Base3DObject._fixrot(rotation.x)
    # y = Base3DObject._fixrot(rotation.y)
    # z = Base3DObject._fixrot(rotation.z)
    # rotationMatrix = Base3DObject._buildRotMat(x, y, z)
    rotationMatrix = Base3DObject._buildRotMat(rotation.x, rotation.y, rotation.z)
    scaleMatrix = mat4.scaling(scale)
    transformation = positionMatrix * rotationMatrix * scaleMatrix
    return ID, transformation, positionMatrix, rotationMatrix, scaleMatrix


def updateLightTransformation(args):
    ID, rotation = args
    rotationMatrix = Base3DObject._buildRotMat(rotation.x, rotation.y, rotation.z)
    return ID, rotationMatrix
