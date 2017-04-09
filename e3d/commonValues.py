from numpy import array, arctan2, arcsin
# from cyBullet.bullet import Vector3, Quaternion, Transform
from cycgkit.cgtypes import quat, mat4, vec3

radian = 0.0174532925
FOVconst = 57.295780490442972

defaultMass = 1.0
defaultGravity = 9.8


class eVec3(vec3):
    def __init__(self, *args):
        super(eVec3, self).__init__(*args)
        value = 0
        self.x = value
        self.y = value
        self.z = value

    # @staticmethod
    # def fromNumpy(narray):
    #     """
    #
    #     @type narray: array
    #     """
    #     nvec = eVec3()
    #     nvec.x = narray.X
    #     nvec.y = narray.Y
    #     nvec.z = narray.Z
    #     return nvec

    def toNumpy(self):
        """

        @rtype : array
        """
        return array(self, 'f')

    @staticmethod
    def frombtVector3(btVec3):
        return eVec3(btVec3.x, btVec3.y, btVec3.z)

    def tobtVector3(self):
        return Vector3(self.x, self.y, self.z)

    def toList(self):
        return list(self)

    def setAll(self, value):
        self.x = value
        self.y = value
        self.z = value

    def cross(self, other):
        res = super(eVec3, self).cross(other)
        return eVec3(res)


def bulletQuatToRotList(btquat):
    q = quat(btquat.getW(), btquat.getX(), btquat.getY(), btquat.getZ())
    x, y, z = _threeAxisRot(2 * (q.x * q.y + q.w * q.z),
                            q.w * q.w + q.x * q.x - q.y * q.y - q.z * q.z,
                            -2 * (q.x * q.z - q.w * q.y),
                            2 * (q.y * q.z + q.w * q.x),
                            q.w * q.w - q.x * q.x - q.y * q.y + q.z * q.z)
    lvec = [x / radian, y / radian, -1.0 * (z / radian)]
    # todo: add 'getOpenGLMatrix(m)' to bullet transform
    '''
    btTransform trans2;
    pinRigidBody->getMotionState()->getWorldTransform(trans2);
    btScalar m[16];
    trans.getOpenGLMatrix(m);
    '''
    return lvec


def bulletVectorToList(vector):
    return [vector.x, vector.y, vector.z]


def listToBulletVector(oList):
    return Vector3(oList[0], oList[1], oList[2])


def listToBulletQuat(oList):
    quat = Quaternion.fromScalars(oList[0], oList[1], oList[2], oList[3])
    return quat


def cgQuatToBulletQuat(cgQuat):
    quat = Quaternion.fromScalars(cgQuat.x, cgQuat.y, cgQuat.z, cgQuat.w)
    return quat


def btTransformFromPosRotMat(pos, rotMat):
    if rotMat is None:
        rotMat = mat4.identity()
    btpos = listToBulletVector(pos)
    btrot = cgQuatToBulletQuat(quat().fromMat(mat4(rotMat)))
    newtrans = Transform()
    newtrans.setOrigin(btpos)
    newtrans.setRotation(btrot)
    return newtrans


def scaleNumber(val, src, dst):
    """
    http://stackoverflow.com/a/4155197

    Scale the given value from the scale of src to the scale of dst.

    @rtype : int
    @type dst: list
    @type src: list
    @type val: int

    Examples:
    >> scaleNumber(0, (0.0, 99.0), (-1.0, 1.0))
    -1.0
    >> scaleNumber(99, (0.0, 99.0), (-1.0, 1.0))
    1
    >> scaleNumber(1, (0.0, 2.0), (0.0, 1.0))
    0.5
    """
    return ((val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]


def _threeAxisRot(r11, r12, r21, r31, r32):
    # http://bediyap.com/programming/convert-quaternion-to-euler-rotations/
    # http://stackoverflow.com/a/27496984
    res = [0, 0, 0]
    res[0] = arctan2(r31, r32)
    try:
        res[1] = arcsin(r21)
    except RuntimeWarning:
        pass
    res[2] = arctan2(r11, r12)
    return res
