from cycgkit.cgtypes import vec3, mat4
from uuid import uuid1
import math


class Geometry:
    def __init__(self):

        self.uuid = uuid1()

        self.name = ''
        self.type = 'Geometry'

        self.vertices = []
        self.colors = []  # one-to-one vertex colors, used in Points and Line

        self.faces = []

        self.faceVertexUvs = [[]]

        self.morphTargets = []
        self.morphColors = []
        self.morphNormals = []

        self.skinWeights = []
        self.skinIndices = []

        self.lineDistances = []

        self.boundingBox = None
        self.boundingSphere = None

        self.hasTangents = False

        self.dynamic = True  # the intermediate typed arrays will be deleted when set to False

        # update flags

        # self.verticesNeedUpdate = False
        # self.elementsNeedUpdate = False
        # self.uvsNeedUpdate = False
        # self.normalsNeedUpdate = False
        # self.tangentsNeedUpdate = False
        # self.colorsNeedUpdate = False
        # self.lineDistancesNeedUpdate = False
        #
        # self.groupsNeedUpdate = False

    def center(self):

        self.computeBoundingBox()

        offset = self.boundingBox.center().negate()

        self.applyMatrix(mat4().setPosition(offset))

        return offset

    def computeFaceNormals(self):
        # cb = vec3()
        # ab = vec3()

        for f in range(len(self.faces)):
            face = self.faces[f]

            vA = self.vertices[face.a]
            vB = self.vertices[face.b]
            vC = self.vertices[face.c]

            cb = vC - vB
            ab = vA - vB
            cb = cb.cross(ab)

            cb.normalize()

            face.normal = cb

    def computeVertexNormals(self, areaWeighted):

        # v, vl, f, fl, face, vertices

        vertices = Array(self.vertices.length)
        v = 0
        vl = self.vertices.length

        while v < vl:
            vertices[v] = vec3()
            v += 1

        f = 0
        fl = self.faces.length
        if areaWeighted:

            # vertex normals weighted by triangle areas
            # http://www.iquilezles.org/www/articles/normals/normals.htm

            # vA, vB, vC
            cb = vec3()
            ab = vec3()

            while f < fl:
                face = self.faces[f]

                vA = self.vertices[face.a]
                vB = self.vertices[face.b]
                vC = self.vertices[face.c]

                cb.subVectors(vC, vB)
                ab.subVectors(vA, vB)
                cb.cross(ab)

                vertices[face.a].add(cb)
                vertices[face.b].add(cb)
                vertices[face.c].add(cb)

                f += 1

        else:

            while f < fl:
                face = self.faces[f]

                vertices[face.a].add(face.normal)
                vertices[face.b].add(face.normal)
                vertices[face.c].add(face.normal)
                f += 1

        v = 0
        vl = self.vertices.length

        while v < vl:
            vertices[v].normalize()
            v += 1

        f = 0
        fl = self.faces.length
        while f < fl:
            face = self.faces[f]

            face.vertexNormals[0] = vertices[face.a].clone()
            face.vertexNormals[1] = vertices[face.b].clone()
            face.vertexNormals[2] = vertices[face.c].clone()
            f += 1


            # def computeMorphNormals(self):
            #
            #     i, il, f, fl, face
            #
            #     # save original normals
            #     # - create temp variables on first access
            #     #   otherwise just copy (for faster repeated calls)
            #
            #     for ( f = 0, fl =  self.faces.length f < fl f ++ ):
            #
            #         face =  self.faces[ f ]
            #
            #         if ( ! face.__originalFaceNormal ):
            #
            #             face.__originalFaceNormal = face.normal.clone()
            #
            #         } else {
            #
            #             face.__originalFaceNormal.copy( face.normal )
            #
            #         }
            #
            #         if ( ! face.__originalVertexNormals ) face.__originalVertexNormals = []
            #
            #         for ( i = 0, il = face.vertexNormals.length i < il i ++ ):
            #
            #             if ( ! face.__originalVertexNormals[ i ] ):
            #
            #                 face.__originalVertexNormals[ i ] = face.vertexNormals[ i ].clone()
            #
            #             } else {
            #
            #                 face.__originalVertexNormals[ i ].copy( face.vertexNormals[ i ] )
            #
            #             }
            #
            #         }
            #
            #     }
            #
            #     # use temp geometry to compute face and vertex normals for each morph
            #
            #     tmpGeo = new THREE.Geometry()
            #     tmpGeo.faces =  self.faces
            #
            #     for ( i = 0, il =  self.morphTargets.length i < il i ++ ):
            #
            #         # create on first access
            #
            #         if ( !  self.morphNormals[ i ] ):
            #
            #              self.morphNormals[ i ] = {}
            #              self.morphNormals[ i ].faceNormals = []
            #              self.morphNormals[ i ].vertexNormals = []
            #
            #             dstNormalsFace =  self.morphNormals[ i ].faceNormals
            #             dstNormalsVertex =  self.morphNormals[ i ].vertexNormals
            #
            #             faceNormal, vertexNormals
            #
            #             for ( f = 0, fl =  self.faces.length f < fl f ++ ):
            #
            #                 faceNormal = vec3()
            #                 vertexNormals = { a: vec3(), b: vec3(), c: vec3() }
            #
            #                 dstNormalsFace.append( faceNormal )
            #                 dstNormalsVertex.append( vertexNormals )
            #
            #             }
            #
            #         }
            #
            #         morphNormals =  self.morphNormals[ i ]
            #
            #         # set vertices to morph target
            #
            #         tmpGeo.vertices =  self.morphTargets[ i ].vertices
            #
            #         # compute morph normals
            #
            #         tmpGeo.computeFaceNormals()
            #         tmpGeo.computeVertexNormals()
            #
            #         # store morph normals
            #
            #         faceNormal, vertexNormals
            #
            #         for ( f = 0, fl =  self.faces.length f < fl f ++ ):
            #
            #             face =  self.faces[ f ]
            #
            #             faceNormal = morphNormals.faceNormals[ f ]
            #             vertexNormals = morphNormals.vertexNormals[ f ]
            #
            #             faceNormal.copy( face.normal )
            #
            #             vertexNormals.a.copy( face.vertexNormals[ 0 ] )
            #             vertexNormals.b.copy( face.vertexNormals[ 1 ] )
            #             vertexNormals.c.copy( face.vertexNormals[ 2 ] )
            #
            #         }
            #
            #     }
            #
            #     # restore original normals
            #
            #     for ( f = 0, fl =  self.faces.length f < fl f ++ ):
            #
            #         face =  self.faces[ f ]
            #
            #         face.normal = face.__originalFaceNormal
            #         face.vertexNormals = face.__originalVertexNormals
            #
            #     }
            #
            #
            #
            # def computeTangents(self):
            #
            #     # based on http://www.terathon.com/code/tangent.html
            #     # tangents go to vertices
            #
            #     f, fl, v, vl, i, vertexIndex,
            #         face, uv, vA, vB, vC, uvA, uvB, uvC,
            #         x1, x2, y1, y2, z1, z2,
            #         s1, s2, t1, t2, r, t, test,
            #         tan1 = [], tan2 = [],
            #         sdir = vec3(), tdir = vec3(),
            #         tmp = vec3(), tmp2 = vec3(),
            #         n = vec3(), w
            #
            #     for ( v = 0, vl =  self.vertices.length v < vl v ++ ):
            #
            #         tan1[ v ] = vec3()
            #         tan2[ v ] = vec3()
            #
            #     }
            #
            #     function handleTriangle( context, a, b, c, ua, ub, uc ):
            #
            #         vA = context.vertices[ a ]
            #         vB = context.vertices[ b ]
            #         vC = context.vertices[ c ]
            #
            #         uvA = uv[ ua ]
            #         uvB = uv[ ub ]
            #         uvC = uv[ uc ]
            #
            #         x1 = vB.x - vA.x
            #         x2 = vC.x - vA.x
            #         y1 = vB.y - vA.y
            #         y2 = vC.y - vA.y
            #         z1 = vB.z - vA.z
            #         z2 = vC.z - vA.z
            #
            #         s1 = uvB.x - uvA.x
            #         s2 = uvC.x - uvA.x
            #         t1 = uvB.y - uvA.y
            #         t2 = uvC.y - uvA.y
            #
            #         r = 1.0 / ( s1 * t2 - s2 * t1 )
            #         sdir.set( ( t2 * x1 - t1 * x2 ) * r,
            #                   ( t2 * y1 - t1 * y2 ) * r,
            #                   ( t2 * z1 - t1 * z2 ) * r )
            #         tdir.set( ( s1 * x2 - s2 * x1 ) * r,
            #                   ( s1 * y2 - s2 * y1 ) * r,
            #                   ( s1 * z2 - s2 * z1 ) * r )
            #
            #         tan1[ a ].add( sdir )
            #         tan1[ b ].add( sdir )
            #         tan1[ c ].add( sdir )
            #
            #         tan2[ a ].add( tdir )
            #         tan2[ b ].add( tdir )
            #         tan2[ c ].add( tdir )
            #
            #     }
            #
            #     for ( f = 0, fl =  self.faces.length f < fl f ++ ):
            #
            #         face =  self.faces[ f ]
            #         uv =  self.faceVertexUvs[ 0 ][ f ] # use UV layer 0 for tangents
            #
            #         handleTriangle( this, face.a, face.b, face.c, 0, 1, 2 )
            #
            #     }
            #
            #     faceIndex = [ 'a', 'b', 'c', 'd' ]
            #
            #     for ( f = 0, fl =  self.faces.length f < fl f ++ ):
            #
            #         face =  self.faces[ f ]
            #
            #         for ( i = 0 i < math.min( face.vertexNormals.length, 3 ) i ++ ):
            #
            #             n.copy( face.vertexNormals[ i ] )
            #
            #             vertexIndex = face[ faceIndex[ i ] ]
            #
            #             t = tan1[ vertexIndex ]
            #
            #             # Gram-Schmidt orthogonalize
            #
            #             tmp.copy( t )
            #             tmp.sub( n.multiplyScalar( n.dot( t ) ) ).normalize()
            #
            #             # Calculate handedness
            #
            #             tmp2.crossVectors( face.vertexNormals[ i ], t )
            #             test = tmp2.dot( tan2[ vertexIndex ] )
            #             w = ( test < 0.0 ) ? - 1.0 : 1.0
            #
            #             face.vertexTangents[ i ] = new THREE.Vector4( tmp.x, tmp.y, tmp.z, w )
            #
            #         }
            #
            #     }
            #
            #      self.hasTangents = True
            #
            #
            #
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

            self.faces.splice(idx, 1)

            for j in range(len(self.faceVertexUvs)):
                self.faceVertexUvs[j].splice(idx, 1)

        # Use unique set of vertices

        diff = len(self.vertices) - len(unique)
        self.vertices = unique
        return diff
