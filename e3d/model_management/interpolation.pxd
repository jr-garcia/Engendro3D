__author__ = 'jrg'

import cython

# @cython.locals(a,b, a1, b1) tupple?
@cython.locals(i=cython.int, j=cython.int, t=cython.float)
cpdef getClosest(cython.dict keys, cython.float time, cython.str chrid, cython.list sortedKeys)
    # cdef inline getfrom(cython.dict keys1, cython.float time, cython.char ch)


# cpdef Lerp(cython.float percent, cython.vector start, cython.vector end)

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