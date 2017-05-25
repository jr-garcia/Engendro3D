from cycgkit.cgtypes import vec3, mat4
from uuid import uuid1
import math

from .face3 import Face3

# Based on Geometry.js from https://github.com/mrdoob/three.js


class Geometry:
    def __init__(self):

        self.uuid = uuid1()

        self.name = ''
        self.type = 'Geometry'

        self.vertices = []
        self.colors = []  # one-to-one vertex colors, used in Points and Line

        self.faces = []

        self.faceVertexUvs = []

        self.lineDistances = []
        self.hasTangents = False
        self.groups = []

        # def computeLineDistances(self):
        #
        #     d = 0
        #     vertices =  self.vertices
        #
        #     for ( i = 0, il = vertices.length i < il i ++ ):
        #
        #         if ( i > 0 ):
        #
        #             d += vertices[ i ].distanceTo( vertices[ i - 1 ] )
        #
        #         }
        #
        #          self.lineDistances[ i ] = d
        #
        #     }
        #
        #
        #
        # def computeBoundingBox(self):
        #
        #     if (  self.boundingBox == None ):
        #
        #          self.boundingBox = new THREE.Box3()
        #
        #     }
        #
        #      self.boundingBox.setFromPoints(  self.vertices )
        #
        #
        #
        # def computeBoundingSphere(self):
        #
        #     if (  self.boundingSphere == None ):
        #
        #          self.boundingSphere = new THREE.Sphere()
        #
        #     }
        #
        #      self.boundingSphere.setFromPoints(  self.vertices )
        #
        #

    def mergeVertices(self):
        verticesMap = {}  # Hashmap for looking up vertice by position coordinates (and making sure they are unique)
        unique = []
        changes = {}

        precisionPoints = 4  # number of decimal points, eg. 4 for epsilon of 0.0001
        precision = math.pow(10, precisionPoints)

        for i in range(len(self.vertices)):
            v = self.vertices[i]
            key = '{}_{}_{}'.format(round(v.x * precision), round(v.y * precision), round(v.z * precision))

            if verticesMap.get(key) is None:
                verticesMap[key] = i
                unique.append(self.vertices[i])
                changes[i] = len(unique) - 1
            else:
                # console.log('Duplicate vertex found. ', i, ' could be using ', verticesMap[key])
                changes[i] = changes[verticesMap[key]]

        # if faces are completely degenerate after merging vertices, we
        # have to remove them from the geometry.
        faceIndicesToRemove = []

        for i in range(len(self.faces)):

            face = self.faces[i]

            face.a = changes[face.a]
            face.b = changes[face.b]
            face.c = changes[face.c]

            indices = [face.a, face.b, face.c]

            dupIndex = - 1

            # if any duplicate vertices are found in a Face3
            # we have to remove the face as nothing can be saved
            for n in range(3):
                if indices[n] == indices[(n + 1) % 3]:
                    dupIndex = n
                    faceIndicesToRemove.append(i)
                    break
        for i in range(len(faceIndicesToRemove) - 1, 0, -1):
            # for ( i = faceIndicesToRemove.length - 1 i >= 0 i -- ):
            idx = faceIndicesToRemove[i]

            self.faces.pop(idx)

            # for j in range(len(self.faceVertexUvs)):
            self.faceVertexUvs.pop(idx)

        # Use unique set of vertices

        diff = len(self.vertices) - len(unique)
        self.vertices = unique
        return diff

    def addGroup(self, start, count):

        self.groups.append({'start': start, 'count': count})

        return self

    def setIndex(self, indices):
        for v in indices:
            self.faces.append(Face3(v.x, v.y, v.z))
