import math

from cycgkit.cgtypes import vec3, vec4

from .Geometry import Geometry
from .face3 import Face3

# Based on PlaneBufferGeometry.js from https://github.com/mrdoob/three.js


class PlaneGeometry(Geometry):
    def __init__(self, width, depth, widthSegments=1, depthSegments=1):
        Geometry.__init__(self)

        self.type = 'PlaneGeometry'

        self.parameters = {'width'         : width, 'depth': depth, 'widthSegments': widthSegments,
                           'depthSegments': depthSegments}

        width_half = width / 2.0
        depth_half = depth / 2.0

        gridX = int(widthSegments or 1)
        gridY = int(depthSegments or 1)

        gridX1 = gridX + 1
        gridY1 = gridY + 1

        segment_width = width / float(gridX)
        segment_depth = depth / float(gridY)

        vertices = [0.0] * gridX1 * gridY1
        uvs = [0.0] * (gridX1 * gridY1)

        offset = 0

        for iy in range(gridY1):

            y = iy * segment_depth - depth_half

            for ix in range(gridX1):
                x = ix * segment_width - width_half
                vertices[offset] = vec3(x, 0, y)

                uvs[offset] = vec3(ix / float(gridX), 1 - (iy / float(gridY)), 1)

                offset += 1

        indices = []

        for iy in range(gridY):

            for ix in range(gridX):
                a = ix + gridX1 * iy
                b = ix + gridX1 * (iy + 1)
                c = (ix + 1) + gridX1 * (iy + 1)
                d = (ix + 1) + gridX1 * iy

                indices.append(vec3(a,b,d))
                indices.append(vec3(b,c,d))

        self.setIndex(indices)
        self.vertices = vertices
        self.setFaceUVS(uvs)

