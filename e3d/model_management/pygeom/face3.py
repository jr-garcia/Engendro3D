from cycgkit.cgtypes import vec3


class Face3:
    def __init__(self, a, b, c, normals=None):
        if normals is None:
            normals = []
        self.a = a
        self.b = b
        self.c = c
        self.vertexNormals = normals
        self.normal = vec3()

    def abcVec3(self):
        return vec3(self.a, self.b, self.c)
