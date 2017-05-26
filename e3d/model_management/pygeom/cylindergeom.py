import math

from cycgkit.cgtypes import vec3, vec4

from .Geometry import Geometry
from .face3 import Face3


# Based on CylinderGeometry.js from https://github.com/mrdoob/three.js


class CylinderGeometry(Geometry):
    def __init__(self, radiusTop=20, radiusBottom=20, height=100, radialSegments=8, heightSegments=1, openEnded=False,
                 thetaStart=0.0, thetaLength=2.0 * math.pi):

        Geometry.__init__(self)
        radialSegments = math.floor(radialSegments) or 8
        heightSegments = math.floor(heightSegments) or 1

        self.type = 'CylinderGeometry'

        self.parameters = {'radiusTop'     : radiusTop, 'radiusBottom': radiusBottom, 'height': height,
                           'radialSegments': radialSegments, 'heightSegments': heightSegments, 'openEnded': openEnded,
                           'thetaStart'    : thetaStart, 'thetaLength': thetaLength}

        self.CylinderBufferGeometry(radiusTop, radiusBottom, height, radialSegments, heightSegments, openEnded, thetaStart,
                                    thetaLength)
        # self.mergeVertices()

    def CylinderBufferGeometry(self, radiusTop, radiusBottom, height, radialSegments, heightSegments, openEnded, thetaStart,
                               thetaLength):

        # buffers

        indices = []
        vertices = []
        # normals = []
        uvs = []

        # helper variables

        index = 0
        indexArray = []
        halfHeight = height / 2.0
        groupStart = 0.0
        heightSegments = int(heightSegments)
        radialSegments = int(radialSegments)

        # generate geometry

        def generateTorso(groupStart, index):
            # normal = vec3()
            vertex = vec3()

            groupCount = 0

            # this will be used to calculate the normal
            # slope = (radiusBottom - radiusTop) / float(height)

            # generate vertices, normals and uvs

            for y in range(heightSegments + 1):

                indexRow = []

                v = y / float(heightSegments)

                # calculate the radius of the current row

                radius = v * (radiusBottom - radiusTop) + radiusTop

                for x in range(radialSegments + 1):
                    u = x / float(radialSegments)

                    theta = u * thetaLength + thetaStart

                    sinTheta = math.sin(theta)
                    cosTheta = math.cos(theta)

                    # vertex

                    vertex.x = radius * sinTheta
                    vertex.y = -v * height + halfHeight
                    vertex.z = radius * cosTheta
                    vertices.append(vec3(vertex))

                    # normal

                    # normal = vec3(sinTheta, slope, cosTheta).normalized()
                    # normals.append(normal)

                    # uv

                    uvs.append(vec3(u, 1 - v, 1))

                    # save index of vertex in respective row
                    indexRow.append(index)
                    index += 1

                # now save vertices of the row in our index array

                indexArray.append(indexRow)

            # generate indices

            for x in range(radialSegments):

                for y in range(heightSegments):
                    # we use the index array to access the correct indices

                    a = indexArray[y][x]
                    b = indexArray[y + 1][x]
                    c = indexArray[y + 1][x + 1]
                    d = indexArray[y][x + 1]

                    # faces

                    indices.append(vec3(a, b, d))
                    indices.append(vec3(b, c, d))

                    # update group counter

                    groupCount += 6

            # add a group to the geometry. this will ensure multi material support

            self.addGroup(groupStart, groupCount)

            # calculate start value for groups

            groupStart += groupCount
            return index

        def generateCap(top, index, groupStart):
            uv = vec3()
            vertex = vec3()

            groupCount = 0

            radius = radiusTop if top == True else radiusBottom
            sign = 1.0 if top == True else -1.0

            # save the index of the first center vertex
            centerIndexStart = index

            # first we generate the center vertex data of the cap.
            # because the geometry needs one set of uvs per face,
            # we must generate a center vertex per face/segment

            for x in range(1, radialSegments + 1):
                # vertex

                vertices.append(vec3(0, halfHeight * sign, 0))

                # normal

                # normals.append(vec3(0, sign, 0))

                # uv

                uvs.append(vec3(0.5, 0.5, 1))

                # increase index

                index += 1

            # save the index of the last center vertex

            centerIndexEnd = index

            # now we generate the surrounding vertices, normals and uvs

            for x in range(radialSegments + 1):
                u = x / float(radialSegments)
                theta = u * thetaLength + thetaStart

                cosTheta = math.cos(theta)
                sinTheta = math.sin(theta)

                # vertex

                vertex.x = radius * sinTheta
                vertex.y = halfHeight * sign
                vertex.z = radius * cosTheta
                vertices.append(vec3(vertex))

                # normal

                # normals.append(vec3(0, sign, 0))

                # uv

                uv.x = (cosTheta * 0.5) + 0.5
                uv.y = (sinTheta * 0.5 * sign) + 0.5
                uvs.append(vec3(uv))

                # increase index

                index += 1

            # generate indices

            for x in range(radialSegments):

                c = centerIndexStart + x
                i = centerIndexEnd + x

                if top:

                    # face top

                    indices.append(vec3(i, i + 1, c))

                else:

                    # face bottom

                    indices.append(vec3(i + 1, i, c))

                groupCount += 3

            # add a group to the geometry. this will ensure multi material support

            self.addGroup(groupStart, groupCount)

            # calculate start value for groups

            groupStart += groupCount
            return index, groupStart

        index = generateTorso(groupStart, index)

        if not openEnded:

            if radiusTop > 0:
                index, groupStart = generateCap(True, index, groupStart)
            if radiusBottom > 0:
                _, __ = generateCap(False, index, groupStart)

        # build geometry

        self.setIndex(indices)
        self.vertices = vertices
        self.setFaceUVS(uvs)
