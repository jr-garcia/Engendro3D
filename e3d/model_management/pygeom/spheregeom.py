import math

from cycgkit.cgtypes import vec3, vec4

from .Geometry import Geometry
from .face3 import Face3


class SphereGeometry(Geometry):
    def __init__(self, radius=50.0, widthSegments=None,
                 heightSegments=None, phiStart=0.0, phiLength=math.pi * 2,
                 thetaStart=0.0, thetaLength=math.pi * 2):

        Geometry.__init__(self)

        radius = float(radius)

        widthSegments = int(max(3, math.floor(widthSegments or 8)))
        heightSegments = int(max(2, math.floor(heightSegments or 6)))

        self.type = 'SphereGeometry'

        self.parameters = {'radius': radius, 'widthSegments': widthSegments, 'heightSegments': heightSegments,
                           'phiStart': phiStart, 'phiLength': phiLength, 'thetaStart': thetaStart,
                           'thetaLength': thetaLength}

        vertices = []
        uvs = []

        for y in range(heightSegments + 1):

            verticesRow = []
            uvsRow = []

            for x in range(widthSegments + 1):
                u = float(x) / widthSegments
                v = float(y) / heightSegments

                vertex = vec3()
                vertex.x = - radius * math.cos(phiStart + u * phiLength) * math.sin(thetaStart + v * thetaLength)
                vertex.y = radius * math.cos(thetaStart + v * thetaLength)
                vertex.z = radius * math.sin(phiStart + u * phiLength) * math.sin(thetaStart + v * thetaLength)

                self.vertices.append(vertex)

                verticesRow.append(len(self.vertices) - 1)
                uvsRow.append(vec3(u, 1 - v, 1))

            vertices.append(verticesRow)
            uvs.append(uvsRow)

        for y in range(heightSegments):
            for x in range(widthSegments):

                v1 = int(vertices[y][x + 1])
                v2 = int(vertices[y][x])
                v3 = int(vertices[y + 1][x])
                v4 = int(vertices[y + 1][x + 1])

                n1 = self.vertices[v1].normalized()
                n2 = self.vertices[v2].normalized()
                n3 = self.vertices[v3].normalized()
                n4 = self.vertices[v4].normalized()

                uv1 = vec3(uvs[y][x + 1])
                uv2 = vec3(uvs[y][x])
                uv3 = vec3(uvs[y + 1][x])
                uv4 = vec3(uvs[y + 1][x + 1])

                if math.fabs(self.vertices[v1].y) == radius:
                    uv1.x = (uv1.x + uv2.x) / 2.0
                    self.faces.append(Face3(v1, v3, v4, [vec3(n1), vec3(n3), vec3(n4)]))
                    self.faceVertexUvs[0].append([uv1, uv3, uv4])
                elif math.fabs(self.vertices[v3].y) == radius:
                    uv3.x = (uv3.x + uv4.x) / 2.0
                    self.faces.append(Face3(v1, v2, v3, [vec3(n1), vec3(n2), vec3(n3)]))
                    self.faceVertexUvs[0].append([uv1, uv2, uv3])
                else:
                    self.faces.append(Face3(v1, v2, v4, [vec3(n1), vec3(n2), vec3(n4)]))
                    self.faceVertexUvs[0].append([uv1, uv2, uv4])

                    self.faces.append(Face3(v2, v3, v4, [vec3(n2), vec3(n3), vec3(n4)]))
                    self.faceVertexUvs[0].append([vec3(uv2), uv3, vec3(uv4)])

        # self.computeFaceNormals()

