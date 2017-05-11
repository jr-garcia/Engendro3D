import math

from cycgkit.cgtypes import vec3, vec4

from .Geometry import Geometry
from .face3 import Face3


class TorusGeometry(Geometry):
    def __init__(self, radius=100, tube=40, radialSegments=8, tubularSegments=6, arc=math.pi * 2):
        Geometry.__init__(self)
        self.type = 'TorusGeometry'

        self.parameters = {"radius": radius, "tube": tube, "radialSegments": radialSegments,
                           "tubularSegments": tubularSegments, "arc": arc}

        center = vec3()
        uvs = []
        normals = []

        for j in range(radialSegments):
            j = float(j)
            for i in range(tubularSegments):
                i = float(i)
                u = i / tubularSegments * arc
                v = j / radialSegments * math.pi * 2

                center.x = radius * math.cos(u)
                center.y = radius * math.sin(u)

                vertex = vec3()
                vertex.x = (radius + tube * math.cos(v)) * math.cos(u)
                vertex.y = (radius + tube * math.cos(v)) * math.sin(u)
                vertex.z = tube * math.sin(v)

                self.vertices.append(vertex)

                uvs.append(vec3(i / tubularSegments, j / radialSegments, 1))
                normals.append((vertex - center).normalize())

        for j in range(1, radialSegments - 1):
            for i in range(1, tubularSegments - 1):
                a = (tubularSegments + 1) * j + i - 1
                b = (tubularSegments + 1) * (j - 1) + i - 1
                c = (tubularSegments + 1) * (j - 1) + i
                d = (tubularSegments + 1) * j + i

                face = Face3(a, b, d, [vec3(normals[a]), vec3(normals[b]), vec3(normals[d])])
                # face = vec3(vec3(normals[a]), vec3(normals[b]), vec3(normals[d]))
                self.faces.append(face)
                self.faceVertexUvs.append([vec3(uvs[a]), vec3(uvs[b]), vec3(uvs[d])])

                face = Face3(b, c, d, [vec3(normals[b]), vec3(normals[c]), vec3(normals[d])])
                # face = vec3(vec3(normals[b]), vec3(normals[c]), vec3(normals[d]))
                self.faces.append(face)
                self.faceVertexUvs.append([vec3(uvs[b]), vec3(uvs[c]), vec3(uvs[d])])

        self.computeFaceNormals()
