import math

from cycgkit.cgtypes import vec3, vec4

from .Geometry import Geometry
from .face3 import Face3


class TorusKnotGeometry(Geometry):
    def __init__(self, radius=100, tube=40, radialSegments=64, tubularSegments=8, p=2, q=3, heightScale=1):
        Geometry.__init__(self)

        self.type = 'TorusKnotGeometry'

        self.parameters = {'radius': radius, 'tube': tube, 'radialSegments': radialSegments,
            'tubularSegments'      : tubularSegments, 'p': p, 'q': q, 'heightScale': heightScale}

        radius = float(radius)
        tube = float(tube)
        radialSegments = float(radialSegments)
        tubularSegments = float(tubularSegments)
        p = float(p)
        q = float(q)
        heightScale = float(heightScale)

        grid = [0] * int(radialSegments)
        tang = vec3()
        n = vec3()
        bitan = vec3()

        def getPos(u, in_q, in_p, radius, heightScale):

            cu = math.cos(u)
            su = math.sin(u)
            quOverP = in_q / in_p * u
            cs = math.cos(quOverP)

            tx = radius * (2 + cs) * 0.5 * cu
            ty = radius * (2 + cs) * su * 0.5
            tz = heightScale * radius * math.sin(quOverP) * 0.5

            return vec3(tx, ty, tz)

        for i in range(int(radialSegments)):

            grid[i] = [0] * int(tubularSegments)
            u = i / radialSegments * 2.0 * p * math.pi
            p1 = getPos(u, q, p, radius, heightScale)
            p2 = getPos(u + 0.01, q, p, radius, heightScale)
            tang = p2 - p1
            n = p2 + p1

            bitan = tang.cross(n)
            n = bitan.cross(tang)
            bitan.normalize()
            n.normalize()

            for j in range(int(tubularSegments)):
                v = j / tubularSegments * 2 * math.pi
                cx = - tube * math.cos(v)  # TODO: Hack: Negating it so it faces outside.
                cy = tube * math.sin(v)

                pos = vec3()
                pos.x = p1.x + cx * n.x + cy * bitan.x
                pos.y = p1.y + cx * n.y + cy * bitan.y
                pos.z = p1.z + cx * n.z + cy * bitan.z
                self.vertices.append(pos)
                grid[i][j] = len(self.vertices) - 1
        for i in range(int(radialSegments)):

            for j in range(int(tubularSegments)):
                ip = int((i + 1) % radialSegments)
                jp = int((j + 1) % tubularSegments)

                a = grid[i][j]
                b = grid[ip][j]
                c = grid[ip][jp]
                d = grid[i][jp]

                uva = vec3(i / radialSegments, j / tubularSegments, 1)
                uvb = vec3((i + 1) / radialSegments, j / tubularSegments, 1)
                uvc = vec3((i + 1) / radialSegments, (j + 1) / tubularSegments, 1)
                uvd = vec3(i / radialSegments, (j + 1) / tubularSegments, 1)

                self.faces.append(Face3(a, b, d))
                self.faceVertexUvs.append([uva, uvb, uvd])

                self.faces.append(Face3(b, c, d))
                self.faceVertexUvs.append([vec3(uvb), vec3(uvc), vec3(uvd)])

        self.computeFaceNormals()
        self.computeVertexNormals()
