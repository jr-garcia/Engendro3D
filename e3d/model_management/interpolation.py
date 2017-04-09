# import numpy
# from cycgkit.cgtypes import vec3, quat


def getClosest(keys, time, chrid, sortedKeys):
    def getfrom(keys1, time, ch):
        try:
            if ch == 'p':
                return keys1[time].position
            elif ch == 's':
                return keys1[time].scale
            else:
                return keys1[time].rotation
        except KeyError:
            return None

    a = None
    b = None
    a1 = -1
    b1 = -1

    for i in range(len(keys) - 1, -1, -1):
        if sortedKeys[i] < time:
            a = getfrom(keys, sortedKeys[i], chrid)
            a1 = sortedKeys[i]
            break

    for j in range(len(keys)):
        if sortedKeys[j] > time:
            b = getfrom(keys, sortedKeys[j], chrid)
            b1 = sortedKeys[j]
            break

    if a is None:
        if b is not None:
            return b, None, time
        else:
            return getfrom(keys, 0, chrid), None, time

    t = 1.0 - ((b1 - time) / (b1 - a1))
    return a, b, t


# -----------
# http:#keithmaggio.wordpress.com/2011/02/15/math-magician-lerp-slerp-and-nlerp/

def Lerp(percent, start, end):
    return start + (percent * (end - start))


# def Nlerp(percent, start, end):
#     res = Lerp(percent, start, end)
#     if res.shape[0] == 3:
#         return numpy.array(vec3(res).normalize())
#     else:
#         na = numpy.zeros(shape=(4,))
#         tres = quat(res).normalize()
#         # na = res
#         na[0] = tres.w
#         na[1] = tres.x
#         na[2] = tres.y
#         na[3] = tres.z
#         return na