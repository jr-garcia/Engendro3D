from cycgkit.cgtypes import vec3, vec4


def RGB255(r, g, b):
    return vec4(r / 255.0, g / 255.0, b / 255.0, 1)


def RGBA255(r, g, b, a):
    val = RGB255(r, g, b)
    val.w = a
    return val


def RGB1(r, g, b):
    return vec4(r, g, b, 1)


def RGBA1(r, g, b, a):
    val = RGB1(r, g, b)
    val.w = a
    return val


def fromRGB255_A(RGBcolor, a):
    val = vec4(RGBcolor)
    val.w = a / 255.0
    return val


def fromRGB1_A(RGBcolor, a):
    val = vec4(RGBcolor)
    val.w = a
    return val


BLACK = RGB1(0, 0, 0)
WHITE = RGB1(1, 1, 1)
RED = RGB1(1, 0, 0)
GREEN = RGB1(0, 1, 0)
BLUE = RGB1(0, 0, 1)
YELLOW = RGB1(1, 1, 0)
ORANGE = RGB1(1, .5, 0)
TRANSPARENT = fromRGB255_A(BLACK, 0)
