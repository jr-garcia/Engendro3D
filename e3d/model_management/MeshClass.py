from collections import defaultdict
import numpy as np
from cycgkit.cgtypes import *
from cycgkit.boundingbox import BoundingBox
from numpy import arccos, arctan2, array, float32, ndarray, pi, sqrt, uint32

from ..LoggerClass import logger
from ..commonValues import scaleNumber


class UVCalculationTypeEnum(object):
    noUVs = 'noUVs'
    spherical = 'spherical'
    planar = 'planar'
    box = 'box'


class NormalsCalculationTypeEnum(object):
    smooth = 'smooth'
    hard = 'hard'


class Mesh(object):
    def __init__(self):
        self.boneOffsets = {}
        self.boneMinMax = {}
        self._vertexBufferArray = None
        self._indexBufferArray = None
        self._declaration = {}
        self._stride = 0
        self._hasTexCoords = [False] * 8
        self._materialIndex = -1
        self._transformation = None
        self._minmax = [[0, 0, 0], [0, 0, 0]]

        self._VertexCount = 0
        self._PrimitiveCount = 0
        self._IndexCount = 0
        self.ID = -1

    def get_PrimitiveCount(self):
        return self._PrimitiveCount

    primitiveCount = property(fget=get_PrimitiveCount)

    def get_VertexCount(self):
        return self._VertexCount

    vertexCount = property(fget=get_VertexCount)

    def get_IndexCount(self):
        return self._IndexCount

    indexCount = property(fget=get_IndexCount)

    @staticmethod
    def fromAssimpMesh(mesh, transform, useChannel0AsUVChannel, lastUVs, boneDict, forceStatic):
        """






        @param forceStatic:
        @param mesh:
        @type mesh: assimpCy.aiMesh
        @param transform:
        @type transform: mat4
        @param useChannel0AsUVChannel:
        @param lastUVs:
        @rtype : Mesh
        """

        logger.meassure('check for uv\'s presence')
        newMesh_hasTexCoords = mesh.HasTextureCoords
        if isinstance(useChannel0AsUVChannel, int) and useChannel0AsUVChannel > 0:
            newMesh_hasTexCoords[useChannel0AsUVChannel] = True

        vertices = mesh.mVertices
        normals = mesh.mNormals
        tangents = mesh.mTangents
        bitangents = mesh.mBitangents
        colours = mesh.mColors

        if not forceStatic:
            bones = mesh.mBones
        else:
            bones = None

        texCoords = []
        i = 0
        while i < 8:
            if newMesh_hasTexCoords[i]:
                if useChannel0AsUVChannel != i:
                    texCoords.append(mesh.mTextureCoords[i])
            else:
                texCoords.append([])
            i += 1
        try:
            if len(lastUVs) > 0:
                lastind = int(lastUVs[0][2])
                # print('lastind start: ' + str(lastind))
                v = 0
                while v <= mesh.mNumVertices - 1:
                    texCoords[useChannel0AsUVChannel].append(lastUVs[lastind])
                    lastind += 1
                    # print('next lastind: ' + str(lastind))
                    v += 1
                lastUVs[0][2] += float(v)
        except Exception as ex:
            raise Exception(
                    "The imported UV's do not match the second model's vertex count." + '\nOriginal message:\n' +
                    ex.message)

        nMesh = Mesh.fromObjectInfo(vertices, mesh.mFaces, None, texCoords, normals, tangents, bitangents, transform,
                                    bones, colours, mesh.mMaterialIndex, boneDict)

        # return Mesh.fromAssimpMesh2(mesh, transform, useChannel0AsUVChannel, lastUVs, boneDict, forceStatic)
        return nMesh

    @staticmethod
    def fromObjectInfo(vertices, faces, minmax, UVsOrCalculationType, normals, tangents=None, bitangents=None,
                       transform=None, mesh_mBones=None, colors=None, materialIndex=0, boneDict=None,
                       forceReIndexing=False):
        """

        @rtype : Mesh
        """
        if not transform:
            transform = mat4.identity()

        baketrans = mesh_mBones is None

        """@type:mat4"""
        invTranspose = transform.inversed().transposed()

        newMesh = Mesh()
        newMesh.ID = id(newMesh)
        newMesh._materialIndex = materialIndex

        hasColors = colors is not None and colors[0] is not None
        hasTangents = tangents is not None
        hasBones = mesh_mBones is not None
        texCoords = []

        reindexingRequired = forceReIndexing

        if normals is None:
            normals = NormalsCalculationTypeEnum.hard
        if len(normals) < len(vertices) or isinstance(normals, type(NormalsCalculationTypeEnum.smooth)):
            logger.meassure('calculate normals')
            if normals == NormalsCalculationTypeEnum.hard:
                normals, vertices, faces = Mesh.calculateHardNormals(vertices, faces)
                reindexingRequired = True
            else:
                normals = Mesh.calculateSmoothNormals(vertices, faces)

        hasNormals = True

        logger.meassure('calculate UVs')
        uvsTypes = [list, ndarray]
        hasAnyTex = False
        if type(UVsOrCalculationType) in uvsTypes:
            if len(UVsOrCalculationType) != 8:
                raise ValueError("'UVsOrCalculationType should be of len=7. It is len={}".format(len(UVsOrCalculationType)))
            for i in range(len(UVsOrCalculationType)):
                if type(UVsOrCalculationType[i]) in uvsTypes and (len(UVsOrCalculationType[i]) == len(vertices)
                                                                  or len(UVsOrCalculationType[i]) == len(faces)):
                    newMesh._hasTexCoords[i] = True
                    hasAnyTex = True
                    texCoords.append(UVsOrCalculationType[i])
                if i >= 7:
                    break

            if not hasAnyTex:
                UVsOrCalculationType = UVCalculationTypeEnum.planar

        vertices = [list(v) for v in vertices]
        faces = [list(f) for f in faces]
        if hasAnyTex:
            texCoords[0] = [list(t) for t in texCoords[0]]
        normals = [list(n) for n in normals]         #    todo: convert everything to vec3?

        if UVsOrCalculationType == UVCalculationTypeEnum.spherical:
            texCoords.append(Mesh.calculateSphericalUVS(vertices))
            Mesh.fixSphereUVs(vertices, faces, texCoords[0], normals)
            newMesh._hasTexCoords[0] = True
            reindexingRequired = True
        elif UVsOrCalculationType == UVCalculationTypeEnum.box:
            texCoords.append(Mesh.calculateBoxUVS(vertices, faces, normals))
            newMesh._hasTexCoords[0] = True
        elif UVsOrCalculationType == UVCalculationTypeEnum.planar:
            texCoords.append(Mesh.calculatePlanarUVS([vertices], normals))
            newMesh._hasTexCoords[0] = True

        if newMesh._hasTexCoords[0] and (tangents is None and bitangents is None):
            logger.meassure('Creating Tangents/Bitangents')
            tangents, bitangents = Mesh.calculateTanBitan(vertices, faces, texCoords[0], normals)
            hasTangents = True
            # hasBiTangents = True

        tangents = [list(t) for t in tangents]
        bitangents = [list(b) for b in bitangents]

        if reindexingRequired:
            logger.meassure('Re-indexing')
            res = Mesh.reIndexMesh(vertices, faces, normals, tangents, bitangents, texCoords[0])
            vertices, faces, normals, tangents, bitangents, texCoords[0] = res
            # TODO: Properly fix all present texcoord channels

        _3floatStride = np.empty((1,), np.float32).strides[0] * 3
        # _4intStride = np.empty((1,), np.int).strides[0] * 4
        newMesh._stride = _3floatStride

        logger.meassure('"Declarations" creation')
        newMesh._declaration = [VertexDeclaration("position", 0)]
        if hasColors:
            newMesh._declaration.append(VertexDeclaration("color", newMesh._stride))
            newMesh._stride += _3floatStride
        if hasNormals:
            newMesh._declaration.append(VertexDeclaration("normal", newMesh._stride))
            newMesh._stride += _3floatStride
        if hasTangents:
            newMesh._declaration.append(VertexDeclaration("tangent", newMesh._stride))
            newMesh._stride += _3floatStride
            newMesh._declaration.append(VertexDeclaration("bitangent", newMesh._stride))
            newMesh._stride += _3floatStride
        for i in range(8):
            if newMesh._hasTexCoords[i]:
                newMesh._declaration.append(VertexDeclaration("texcoord" + str(i), newMesh._stride))
                newMesh._stride += (_3floatStride / 3) * 2
        if hasBones:
            newMesh._declaration.append(VertexDeclaration("boneweights", newMesh._stride))
            newMesh._stride += (_3floatStride / 3) * 4
            newMesh._declaration.append(VertexDeclaration("boneindexes", newMesh._stride))
            newMesh._stride += (_3floatStride / 3) * 4
            for b in mesh_mBones:
                newMesh.boneOffsets[b.mName] = mat4(b.mOffsetMatrix.tolist())

        # if baketrans and transform != mat4.identity():
        logger.meassure('baking transformations')
        vertices = transformVec(transform, vertices, baketrans)
        normals = transformVec(invTranspose, normals, baketrans)
        tangents = transformVec(invTranspose, tangents, baketrans)
        bitangents = transformVec(invTranspose, bitangents, baketrans)

        logger.meassure('create new vertex buffer')
        vertexStream = []
        if minmax:
            newMesh._minmax = minmax
        # else:
        #     # vl = list(vertices[0])
        #     # newMesh._minmax = [list(vl), list(vl)]
        #     newMesh._minmax = [0, 0]

        currentVertexN = 0
        for v in vertices:
            vertexStream.extend(v)
            if hasColors:
                vertexStream.extend(colors[currentVertexN])
            # if hasNormals:
            normal = normals[currentVertexN]
            try:
                normal = normal.normalized()
            except Exception:
                pass
            vertexStream.extend(normal)
            if hasTangents:
                vertexStream.extend(tangents[currentVertexN])
                # if hasBiTangents:
                vertexStream.extend(bitangents[currentVertexN])
            for uvchan in texCoords:
                if not len(uvchan) == 0:
                    coord = [float(uvchan[currentVertexN][0]), float(uvchan[currentVertexN][1])]
                    coord[1] = 1 - coord[1]
                    vertexStream.extend(coord)

            vl = vec3(v)
            if baketrans:
                cv = newMesh._minmax
                newMesh._minmax[0][0] = min(cv[0][0], vl[0])
                newMesh._minmax[0][1] = min(cv[0][1], vl[1])
                newMesh._minmax[0][2] = min(cv[0][2], vl[2])
                newMesh._minmax[1][0] = max(cv[1][0], vl[0])
                newMesh._minmax[1][1] = max(cv[1][1], vl[1])
                newMesh._minmax[1][2] = max(cv[1][2], vl[2])

            if hasBones:
                bb = 0
                bonewl = [0, 0, 0, 0]
                # boneil = [_maxBones, _maxBones, _maxBones, _maxBones]
                boneil = [0, 0, 0, 0]
                for b in mesh_mBones:
                    for w in b.mWeights:
                        if w.mVertexId == currentVertexN:
                            if bb < 4:
                                bName = b.mName
                                bonewl[bb] = float(w.mWeight)
                                boneil[bb] = float(boneDict[bName])
                                if bonewl[bb] > 0.0:
                                    if bName in newMesh.boneMinMax.keys():
                                        cv = list(newMesh.boneMinMax[bName])
                                        newMesh.boneMinMax[bName][0][0] = min(cv[0][0], vl[0])
                                        newMesh.boneMinMax[bName][0][1] = min(cv[0][1], vl[1])
                                        newMesh.boneMinMax[bName][0][2] = min(cv[0][2], vl[2])
                                        newMesh.boneMinMax[bName][1][0] = max(cv[1][0], vl[0])
                                        newMesh.boneMinMax[bName][1][1] = max(cv[1][1], vl[1])
                                        newMesh.boneMinMax[bName][1][2] = max(cv[1][2], vl[2])
                                    else:
                                        newMesh.boneMinMax[bName] = [vl, vl]
                                bb += 1
                            else:
                                logger.log('Vertex {} is affected by more than 4 bones.'.format(currentVertexN))
                            b.mWeights.remove(w)
                            break
                vertexStream.extend(bonewl)
                vertexStream.extend(boneil)

            currentVertexN += 1

        logger.meassure('Create VBOs')

        newMesh._vertexBufferArray = array(vertexStream, float32)
        newMesh._indexBufferArray = array(faces, dtype=uint32).flatten()

        newMesh._VertexCount = len(vertices)
        newMesh._PrimitiveCount = len(faces)
        newMesh._IndexCount = len(faces) * 3
        logger.meassure('done mesh')

        return newMesh

    @staticmethod
    def calculateHardNormals(verts, faces):
        newVertices = []
        newFaces = []
        finalNormals = []
        normals = []

        for i in range(len(faces)):
            face = int(faces[i][0]), int(faces[i][1]), int(faces[i][2])
            triang = [verts[face[0]], verts[face[1]], verts[face[2]]]
            normal = Mesh.calculateSurfaceNormal(triang)
            normals.append(normal)

        for i in range(len(faces)):
            face = int(faces[i][0]), int(faces[i][1]), int(faces[i][2])
            triang = list([verts[face[0]], verts[face[1]], verts[face[2]]])
            normal = list(normals[i])
            newVertices.extend(triang)
            finalNormals.extend([normal] * 3)
            nvLen = len(newVertices)
            newFaces.append([nvLen - 3, nvLen - 2, nvLen - 1])

        return finalNormals, newVertices, newFaces

    @staticmethod
    def calculateSmoothNormalsAv(verts, faces):
        normals = []
        snormals = []
        vertexDict = {}
        for i in range(len(verts)):
            vertexDict[i] = []
            snormals.append(list(vec3(0)))

        for i in range(len(faces)):
            ind = faces[i]
            vertexDict[ind[0]].append(i)
            vertexDict[ind[1]].append(i)
            vertexDict[ind[2]].append(i)
            triang = [verts[ind[0]], verts[ind[1]], verts[ind[2]]]
            normal = Mesh.calculateSurfaceNormal(triang)
            normals.append(normal)

        for vert in vertexDict.items():
            totalN = vec3()
            for face in vert[1]:
                totalN += normals[face]
            if len(vert[1]) > 0:
                snormals[vert[0]] = list(totalN / len(vert[1]))

        return snormals

    @staticmethod
    def calculateSmoothNormals(verts, inds):
        snormals = []
        for i in range(len(verts)):
            snormals.append(vec3(0))

        for i in range(len(inds)):
            a, b, c = inds[i]
            ind = int(a), int(b), int(c)
            triang = [verts[ind[0]], verts[ind[1]], verts[ind[2]]]
            normal = Mesh.calculateSurfaceNormal(triang)
            snormals[ind[0]] += vec3(normal)
            snormals[ind[1]] += vec3(normal)
            snormals[ind[2]] += vec3(normal)

        return snormals

    @staticmethod
    def calculateSurfaceNormal(Triangle):
        # http://www.iquilezles.org/www/articles/normals/normals.htm
        U = vec3(Triangle[0]) - vec3(Triangle[1])
        V = vec3(Triangle[2]) - vec3(Triangle[1])
        n = V.cross(U)
        return list(n)

    @staticmethod
    def calculateSurfaceNormalAlt(Triangle):
        # opengl wiki
        U = vec3(Triangle[1]) - vec3(Triangle[0])
        V = vec3(Triangle[2]) - vec3(Triangle[0])

        Normal = vec3()
        Normal.x = (U.y * V.z) - (U.z * V.y)
        Normal.y = (U.z * V.x) - (U.x * V.z)
        Normal.z = (U.x * V.y) - (U.y * V.x)

        return list(Normal)

    @staticmethod
    def calculateSphericalUVS(vertices):
        # http://sol.gfxile.net/sphere/
        uvs = []
        for vv in vertices:
            ver = vec3(vv)
            tlen = sqrt(ver.x * ver.x + ver.y * ver.y + ver.z * ver.z)
            v = float(arccos(ver.y / tlen) / pi)
            u = float((arctan2(ver.x, ver.z) / pi + 1.0) * 0.5)
            uvs.append(list(vec3(u, 1.0 - v, 0)))
        return uvs

    @staticmethod
    def calculateBoxUVS(vertices, faces, normals):
        uvs = [None] * len(vertices)
        quads = {}
        for i in range(len(normals)):
            isinQuads = False
            norm = vec3(normals[i])
            for qnorm in quads.keys():
                if qnorm == norm:
                    isinQuads = True
                    break
            if not isinQuads:
                quads[norm] = []

        for i in range(len(faces)):
            verta = int(faces[i][0])
            norm = vec3(normals[verta])
            for qnorm in quads.keys():
                if qnorm == norm:
                    quads[qnorm].append(faces[i])
                    break
        quadUVS = []
        for q in quads.items():
            vertlist = []
            for face in q[1]:
                ver0 = vertices[int(face[0])]
                ver1 = vertices[int(face[1])]
                ver2 = vertices[int(face[2])]
                vertlist.append([ver0, ver1, ver2])
            res = Mesh.calculatePlanarUVS(vertlist, q[0])
            quadUVS.append(res)

        counter = 0
        for q in quads.items():
            lastface = 0
            facesUvs = quadUVS[counter]
            for face in q[1]:
                uvs[int(face[0])] = facesUvs[lastface]
                uvs[int(face[1])] = facesUvs[lastface + 1]
                uvs[int(face[2])] = facesUvs[lastface + 2]
                lastface += 3
            counter += 1

        return uvs

    @staticmethod
    def calculatePlanarUVS(groupedVertices, normal):
        if isinstance(normal, list):
            if normal.__len__() > 1:
                normal = vec3(normal[0])
            else:
                normal = vec3(normal)

        uvs = []
        bbox = BoundingBox()
        M = mat3.fromToRotation(normal, vec3(0, 0, 1))
        newverts = []

        for v in groupedVertices:
            faceverts = []
            for vv in v:
                ver = M * vec3(vv)
                faceverts.append(ver)
            newverts.append(faceverts)

        for v in newverts:
            for vv in v:
                bbox.addPoint(vv)

        src1, src2 = bbox.getBounds()
        srcU = [src1.x, src2.x]
        srcV = [src1.y, src2.y]

        for v in newverts:
            for ver in v:
                U = scaleNumber(ver.x, srcU, [0.0, 1.0])
                V = scaleNumber(ver.y, srcV, [0.0, 1.0])
                uvs.append([U, V, 1.0])

        return uvs

    @staticmethod
    def fixPolarUVS(faces, uvs, vertices, normals, place):
        assert isinstance(vertices, list)
        assert isinstance(normals, list)
        assert isinstance(uvs, list)
        assert isinstance(faces, list)
        sharesdict = {}
        for i in range(len(vertices)):
            sharesdict[i] = []
        try:
            for i in range(faces.__len__()):
                face = faces[i]
                for verN in range(3):
                    sharesdict[face[verN]].append(i)
        except Exception:
            raise
        shareN = {}
        for vert in sharesdict.items():
            shareN[vert[0]] = len(vert[1])
        svalues = sorted(shareN.values(), reverse=True)
        polars = []
        for ob in shareN.items():
            if ob[1] in [svalues[0], svalues[1]]:
                polars.append(ob[0])
                if polars.__len__() == 2:
                    break
        polarF0 = sharesdict[polars[0]]
        polarF1 = sharesdict[polars[1]]
        for f in polarF0:
            face = faces[f]
            face = int(face[0]), int(face[1]), int(face[2])
            for v in range(3):
                if face[v] == polars[0]:
                    newuv = list(uvs[face[v]])
                    uvstoav = [uvs[face[0]][place], uvs[face[1]][place], uvs[face[2]][place]]
                    uvstoav.pop(v)
                    avuv = (uvstoav[0] + uvstoav[1]) / 2.0
                    newvertex = list(vertices[face[v]])
                    vertices.append(newvertex)
                    if 0 in uvstoav:
                        for ui in range(2):
                            if uvstoav[ui] != 0:
                                if uvstoav[ui] > 0.5:
                                    newuv[place] = 1.0  # - .063
                                else:
                                    newuv[place] = avuv
                                break
                    else:
                        newuv[place] = avuv
                    uvs.append(newuv)
                    newnormal = vec3(normals[face[v]])
                    normals.append(list(newnormal))
                    base = len(vertices)
                    faces[f][v] = base - 1
                    break

        for f in polarF1:
            face = faces[f]
            face = int(face[0]), int(face[1]), int(face[2])
            for v in range(3):
                if face[v] == polars[1]:
                    newuv = list(uvs[face[v]])
                    uvstoav = [uvs[face[0]][place], uvs[face[1]][place], uvs[face[2]][place]]
                    uvstoav.pop(v)
                    avuv = (uvstoav[0] + uvstoav[1]) / 2.0
                    newvertex = list(vertices[face[v]])
                    vertices.append(newvertex)
                    if 0 in uvstoav:
                        for ui in range(2):
                            if uvstoav[ui] != 0:
                                if uvstoav[ui] > 0.5:
                                    newuv[place] = 1.0  # - .063
                                else:
                                    newuv[place] = avuv
                                    pass
                                break
                    else:
                        newuv[place] = avuv
                    uvs.append(newuv)
                    newnormal = vec3(normals[face[v]])
                    normals.append(list(newnormal))
                    base = len(vertices)
                    faces[f][v] = base - 1
                    break

    @staticmethod
    def fixSphereUVs(vertices, faces, uvs, normals):
        """

        @param vertices:
        @type vertices: list
        @param faces:
        @type faces: list
        @param uvs:
        @type uvs: list
        @param normals:
        @type normals: list
        @return:
        @rtype:

        http://gamedev.stackexchange.com/a/33957

        Check each triangle if it is on the seam.

        1a. Get each texture coord for the triangle.

        1b. If one or two have their U coord = 0, it is on the seam

        1c. If the remaining texcoords have U > 0.5 (closer to 1 than 0) this triangle is also causing distortion.

        If so, clone the vertices where texcoord.U = 0, and set the U value to 1.
        Get the index of each cloned vertex
        Alter the current triangle, to use theese indices instead.
        Draw/Add the altered triangle
        """
        place = 0
        Mesh.fixPolarUVS(faces, uvs, vertices, normals, place)
        # place = 1
        for i in range(faces.__len__()):
            face = faces[i]
            face = int(face[0]), int(face[1]), int(face[2])
            uv0 = uvs[face[0]]
            uv1 = uvs[face[1]]
            uv2 = uvs[face[2]]
            allcuvs = [uv0, uv1, uv2]
            uvlist = [uv0[place], uv1[place], uv2[place]]
            testa = 0.0 in uvlist
            testb = any([True if val > 0.5 else False for val in uvlist])
            if testa and testb:
                for uv in range(3):
                    if uvlist[uv] == 0.0:
                        newvertex = list(vertices[face[uv]])
                        vertices.append(newvertex)
                        newuv = list(allcuvs[uv])
                        newuv[place] = 1.0
                        newnormal = vec3(normals[face[uv]])
                        uvs.append(newuv)
                        normals.append(newnormal)
                        base = len(vertices)
                        faces[i][uv] = base - 1

    @staticmethod
    def calculateTanBitan(vertices, faces, uvs, normals):
        # http://www.opengl-tutorial.org/intermediate-tutorials/tutorial-13-normal-mapping/
        tangents = [list([0.0, 0.0, 0.0])] * len(vertices)
        bitangents = [list([0.0, 0.0, 0.0])] * len(vertices)

        for face in faces:
            face = int(face[0]), int(face[1]), int(face[2])
            v0 = vertices[face[0]]
            v1 = vertices[face[1]]
            v2 = vertices[face[2]]

            uv0 = uvs[face[0]]
            uv1 = uvs[face[1]]
            uv2 = uvs[face[2]]

            norm0 = normals[face[0]]
            norm1 = normals[face[1]]
            norm2 = normals[face[2]]

            deltaPos1 = vec3(v1) - vec3(v0)
            deltaPos2 = vec3(v2) - vec3(v0)
            deltaUV1 = vec3(uv1) - vec3(uv0)
            deltaUV2 = vec3(uv2) - vec3(uv0)

            # todo: replace this dirty fix for a proper fix to avoid division by 0
            rdelta = (deltaUV1.x * deltaUV2.y - deltaUV1.y * deltaUV2.x) or 1.0
            r = 1.0 / rdelta
            tangent = (deltaPos1 * deltaUV2.y - deltaPos2 * deltaUV1.y) * r
            bitangent = (deltaPos2 * deltaUV1.x - deltaPos1 * deltaUV2.x) * r

            tangents[face[0]] = Mesh.fixInvertedTan(tangent, bitangent, norm0)
            tangents[face[1]] = Mesh.fixInvertedTan(tangent, bitangent, norm1)
            tangents[face[2]] = Mesh.fixInvertedTan(tangent, bitangent, norm2)

            bitangents[face[0]] = bitangent
            bitangents[face[1]] = bitangent
            bitangents[face[2]] = bitangent

        return tangents, bitangents

    @staticmethod
    def makeOrthoTan(t, n):
        t = ((t - n) * (n * t))
        try:
            t = t.normalized()  # todo: check change from .normalize to .normalized
        except:
            pass
        return t

    @staticmethod
    def fixInvertedTan(t, b, n):
        n = vec3(n)
        # if (t.cross(n) * b) < 0.0:
        if (n.cross(t) * b) < 0.0:
            t = t * -1.0
        return t

    @staticmethod
    def findSimilarVertexFromLUTable(v, u, n, uvs, norms, table, vertsCount):
        key = '{}|{}|{}'.format(v[0], v[1], v[2])
        if key in table.keys():
            for vectorInd in table[key]:
                if np.all(uvs[vectorInd] == u) and np.all(norms[vectorInd] == n):
                    return vectorInd, table
        table[key].append(vertsCount)
        return None, table

    @staticmethod
    def reIndexMesh(vertices, faces, normals, tangents, bitangents, uvs):
        nver = []
        nnorm = []
        nuvs = []
        nfaces = []
        ntans = []
        nbitans = []
        table = defaultdict(list)

        for face in faces:
            nface = [0, 0, 0]
            for i in range(3):
                cFaceVert = int(face[i])
                v = vertices[cFaceVert]
                u = uvs[cFaceVert]
                n = normals[cFaceVert]
                sv, table = Mesh.findSimilarVertexFromLUTable(v, u, n, nuvs, nnorm, table, nver.__len__())
                if sv is not None:
                    nface[i] = sv
                    if tangents is not None:
                        ntans[sv] = list(vec3(ntans[sv]) + vec3(tangents[cFaceVert]))
                        nbitans[sv] = list(vec3(nbitans[sv]) + vec3(bitangents[cFaceVert]))
                else:
                    nface[i] = nver.__len__()
                    nver.append(v)
                    nuvs.append(u)
                    nnorm.append(n)
                    if tangents is not None:
                        t = tangents[cFaceVert]
                        bt = bitangents[cFaceVert]
                        ntans.append(t)
                        nbitans.append(bt)
            nfaces.append(nface)

        return nver, nfaces, nnorm, ntans, nbitans, nuvs


def transformVec(matrix, vectorsList, baketrans):
    if 'ndarray' in str(type(vectorsList)):
        if vectorsList.dtype != np.double:
            newVectors = vectorsList.astype(np.double)
        else:
            newVectors = vectorsList
    elif isinstance(vectorsList, list):
        newVectors = np.array(vectorsList, np.double)
    else:
        raise TypeError('Wrong data type for vector')

    if baketrans and matrix != mat4.identity():
        return [vec3(ver) * matrix for ver in newVectors]
    else:
        return [vec3(ver) for ver in newVectors]


class VertexDeclaration(object):
    def __init__(self, vname, offset):
        """
        Defines the vertex elements contained in the renderable.
        Accesible through objects's member: _declaration (List)
        @type name: str
        @type offset: int
        @rtype : VertexDeclaration
        @param self:
        @param name:
        @param offset:
        """
        self._name = vname
        self._offset = int(offset)

    def __repr__(self):
        return '{}, offset:{}'.format(self._name, self._offset)
