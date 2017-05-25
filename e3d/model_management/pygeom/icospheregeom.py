import math

from cycgkit.cgtypes import vec3, vec4

from .Geometry import Geometry
from .face3 import Face3


# Based on https://gamedev.stackexchange.com/a/31312

class IcoSphereGeometry(Geometry):
    def __init__(self, detailLevel=3):

        Geometry.__init__(self)

        self.type = 'IcoSphereGeometry'

        self.parameters = {'detailLevel': detailLevel}

        vectors = []
        indices = []

        geom = GeometryProvider(vectors, indices)

        for i in range(detailLevel):
            indices = geom.Subdivide(vectors, indices, True)

        # normalize vectors to "inflate" the icosahedron into a sphere.
        for i in range(len(vectors)):
            vectors[i].normalize()

        self.vertices = vectors
        for i in range(0, len(indices), 3):
            c, b, a = [indices[i], indices[i + 1], indices[i + 2]]
            self.faces.append(Face3(a, b, c))


class GeometryProvider:
    def GetMidpointIndex(self, midpointIndices, vertices, i0, i1):

        edgeKey = "{0}_{1}".format(min(i0, i1), max(i0, i1))

        midpointIndex = midpointIndices.get(edgeKey)

        if not midpointIndex:
            v0 = vertices[i0]
            v1 = vertices[i1]

            midpoint = (v0 + v1) / 2.0

            if midpoint in vertices:
                midpointIndex = vertices.index(midpoint)
            else:
                midpointIndex = len(vertices)
                vertices.append(midpoint)
                midpointIndices[edgeKey] = midpointIndex

        return midpointIndex

    def Subdivide(self, vectors, indices, removeSourceTriangles):
        midpointIndices = dict()

        newIndices = [] * (len(indices) * 4)

        if not removeSourceTriangles:
            newIndices.AddRange(indices)

        for i in range(0, len(indices) - 2, 3):
            i0 = indices[i]
            i1 = indices[i + 1]
            i2 = indices[i + 2]

            m01 = self.GetMidpointIndex(midpointIndices, vectors, i0, i1)
            m12 = self.GetMidpointIndex(midpointIndices, vectors, i1, i2)
            m02 = self.GetMidpointIndex(midpointIndices, vectors, i2, i0)

            newIndices.extend([i0, m01, m02, i1, m12, m01, i2, m02, m12, m02, m01, m12])

        return newIndices

    def __init__(self, vertices, indices):
        # op's note: icosahedron definition may have come from the OpenGL red book. I don't recall where I found it.
        filteredList = [f + len(vertices) for f in
                        [0, 4, 1, 0, 9, 4, 9, 5, 4, 4, 5, 8, 4, 8, 1, 8, 10, 1, 8, 3, 10, 5, 3, 8, 5, 2, 3, 2, 7, 3, 7,
                         10, 3, 7, 6, 10, 7, 11, 6, 11, 0, 6, 0, 1, 6, 6, 1, 10, 9, 0, 11, 9, 11, 2, 9, 2, 5, 7, 2, 11]]

        # .Select(i= > i + vertices.Count)

        indices.extend(filteredList)

        X = 0.525731112119133606
        Z = 0.850650808352039932

        vertices.extend([vec3(-X, 0, Z), vec3(X, 0, Z), vec3(-X, 0, -Z), vec3(X, 0, -Z), vec3(0, Z, X), vec3(0, Z, -X),
                         vec3(0, -Z, X), vec3(0, -Z, -X), vec3(Z, X, 0), vec3(-Z, X, 0), vec3(Z, -X, 0),
                         vec3(-Z, -X, 0)])
