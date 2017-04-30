import math

from cycgkit.cgtypes import vec3, vec4

from .Geometry import Geometry
from .face3 import Face3


class BoxGeometry(Geometry):
    def __init__(self, width, height, depth, widthSegments=1, heightSegments=1, depthSegments=1):
        Geometry.__init__(self)

        self.type = 'BoxGeometry'

        width = float(width)
        height = float(height)
        depth = float(depth)

        self.parameters = {'width'         : width, 'height': height, 'depth': depth, 'widthSegments': widthSegments,
                           'heightSegments': heightSegments, 'depthSegments': depthSegments}

        width_half = width / 2.0
        height_half = height / 2.0
        depth_half = depth / 2.0

        def buildPlane(u, v, udir, vdir, width, height, depth, materialIndex):
            gridX = widthSegments
            gridY = heightSegments
            width_half = width / 2.0
            height_half = height / 2.0
            offset = float(len(self.vertices))

            indDict = {'x': 0, 'y': 1, 'z': 2}

            if (u == 'x' and v == 'y') or (u == 'y' and v == 'x'):
                w = 'z'

            elif (u == 'x' and v == 'z') or (u == 'z' and v == 'x'):
                w = 'y'
                gridY = depthSegments

            elif (u == 'z' and v == 'y') or (u == 'y' and v == 'z'):
                w = 'x'
                gridX = depthSegments

            gridX1 = gridX + 1
            gridY1 = gridY + 1
            segment_width = width / gridX
            segment_height = height / gridY
            normal = vec3()
            normal[indDict[w]] = 1 if depth > 0 else -1

            for iy in range(gridY1):

                for ix in range(gridX1):
                    vector = vec3()
                    vector[indDict[u]] = (ix * segment_width - width_half) * udir
                    vector[indDict[v]] = (iy * segment_height - height_half) * vdir
                    vector[indDict[w]] = depth

                    self.vertices.append(vector)

            for iy in range(gridY):

                for ix in range(gridX):
                    a = ix + gridX1 * iy
                    b = ix + gridX1 * (iy + 1)
                    c = (ix + 1) + gridX1 * (iy + 1)
                    d = (ix + 1) + gridX1 * iy

                    uva = vec3(ix / gridX, 1 - iy / gridY, 1)
                    uvb = vec3(ix / gridX, 1 - (iy + 1) / gridY, 1)
                    uvc = vec3((ix + 1) / gridX, 1 - (iy + 1) / gridY, 1)
                    uvd = vec3((ix + 1) / gridX, 1 - iy / gridY, 1)

                    face = Face3(a + offset, b + offset, d + offset)
                    face.normal = vec3(normal)
                    face.vertexNormals.append(vec3(normal))

                    self.faces.append(face)
                    self.faceVertexUvs[0].append([uva, uvb, uvd])

                    face = Face3(b + offset, c + offset, d + offset)
                    face.normal = vec3(normal)
                    face.vertexNormals.append(vec3(normal))

                    self.faces.append(face)
                    self.faceVertexUvs[0].append([vec3(uvb), vec3(uvc), vec3(uvd)])

        buildPlane('z', 'y', - 1, - 1, depth, height, width_half, 0)  # px
        buildPlane('z', 'y', 1, - 1, depth, height, - width_half, 1)  # nx
        buildPlane('x', 'z', 1, 1, width, depth, height_half, 2)  # py
        buildPlane('x', 'z', 1, - 1, width, depth, - height_half, 3)  # ny
        buildPlane('x', 'y', 1, - 1, width, height, depth_half, 4)  # pz
        buildPlane('x', 'y', - 1, - 1, width, height, - depth_half, 5)  # nz

        self.mergeVertices()
