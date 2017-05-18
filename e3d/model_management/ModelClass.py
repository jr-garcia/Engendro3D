from os import path
from assimpcy import aiImportFile, aiPostProcessSteps as pp
from cycgkit.cgtypes import mat4, quat, vec3, slerp
from cycgkit.boundingbox import BoundingBox
from copy import deepcopy

from .AnimationModule import Animation, transformationValues
from ..LoggerClass import logger, logLevelsEnum
from .NodeClass import Node
from .MeshClass import Mesh, UVCalculationTypeEnum, NormalsCalculationTypeEnum
from .MaterialClass import Material
from .geomModelsModule import geomTypeEnum, getObjectInfo
from ..physics_management.physicsModule import bodyShapesEnum
from .interpolation import getClosest, Lerp


class Skeleton(object):
    class bone(object):
        def __init__(self, node, parent, boneList):
            """

            @type parent: Skeleton.bone
            """
            self.ID = node.mName
            self.children = []
            self.transforms = {}
            self.localTransformation = mat4(node.mTransformation).transpose()
            # self.localTransformation = parentTransformation * self.localTransformation
            self.parent = parent
            if bool(node.mChildren):
                for cn in node.mChildren:
                    if cn.mName in boneList:
                        cb = Skeleton.bone(cn, self, boneList)
                        self.children.append(cb)

        @staticmethod
        def isEqual(a, b):
            if len(a) != len(b):
                raise RuntimeError('Wrong types in modelclass.getAnimations. Please Report it.')
            for i in range(len(a)):
                if a[i] != b[i]:
                    return False
            return True

        def getAnimTransforms(self, animation, time, mesh, parentTransformation, finalTransformations):
            """

            @type animation: AnimationModule.Animation
            """
            nodeTransformation = self.localTransformation
            globalTransformation = nodeTransformation

            if self.ID in animation.boneKeys.keys():
                meshtrans = animation.transforms.get(id(mesh))
                if meshtrans:
                    animtrans = meshtrans.get(self.ID)
                else:
                    animation.transforms[id(mesh)] = {}
                    animtrans = None
                if not animtrans:
                    animation.transforms[id(mesh)][self.ID] = {}
                    trans = None
                else:
                    trans = animtrans.get(time)
                if not trans:
                    if time >= 0:
                        keys = animation.boneKeys[self.ID]
                        sortedKeys = sorted(list(keys.keys()))
                        transformationInfo = keys.get(time, transformationValues())
                        if transformationInfo.position is None:
                            a, b, t = getClosest(keys, time, 'p', sortedKeys)
                            if b is None:
                                # if a is None:
                                #     print('pos is none')
                                #     a = array([0, 0, 0])
                                transformationInfo.position = a
                            else:
                                if self.isEqual(a, b):
                                    transformationInfo.position = a
                                else:
                                    transformationInfo.position = Lerp(t, vec3(a), vec3(b))

                        if transformationInfo.scale is None:
                            a, b, t = getClosest(keys, time, 's', sortedKeys)
                            if b is None:
                                # if a is None:
                                #     print('scale is none')
                                #     a = [1, 1, 1]
                                transformationInfo.scale = a
                            else:
                                if self.isEqual(a, b):
                                    transformationInfo.scale = a
                                else:
                                    transformationInfo.scale = Lerp(t, vec3(a), vec3(b))

                        if transformationInfo.rotation is None:
                            a, b, t = getClosest(keys, time, 'r', sortedKeys)
                            if b is None:
                                # if a is None:
                                # print('rot is none')
                                # a = array([1, 0, 0, 0])
                                transformationInfo.rotation = a
                            else:
                                if self.isEqual(a, b):
                                    transformationInfo.rotation = a
                                else:
                                    # transformationInfo.rotation = Nlerp(t, a, b)
                                    transformationInfo.rotation = slerp(t, quat(a), quat(b))
                                    transformationInfo.rotation = list(
                                            [transformationInfo.rotation.w, transformationInfo.rotation.x,
                                             transformationInfo.rotation.y, transformationInfo.rotation.z])

                        rotationMatrix = quat(transformationInfo.rotation).toMat4()
                        positionMatrix = mat4.translation(vec3(transformationInfo.position))
                        scaleMatrix = mat4.scaling(vec3(transformationInfo.scale))
                        nodeTransformation = positionMatrix * rotationMatrix * scaleMatrix

                    nodeTransformation = nodeTransformation.transposed()
                    globalTransformation = nodeTransformation * parentTransformation
                    if self.ID in mesh.boneOffsets.keys():
                        offset = mesh.boneOffsets[self.ID]
                        finalTransformations[self.ID] = offset * globalTransformation
                        finalTransformations[self.ID] = finalTransformations[self.ID].transposed()
                        animation.transforms[id(mesh)][self.ID][time] = finalTransformations[self.ID]
                    else:
                        animation.transforms[id(mesh)][self.ID][time] = globalTransformation
                else:
                    finalTransformations[self.ID] = trans

            for cb in self.children:
                cb.getAnimTransforms(animation, time, mesh, globalTransformation, finalTransformations)

    def __init__(self, rootNode, animations):
        """

        @rtype : Skeleton
        """
        boneList = []
        self._bindTransforms = {}
        self._finalTransformations = {}
        for a in animations.values():
            for b in a.boneKeys.keys():
                if b not in boneList:
                    boneList.append(b)

        self.root = Skeleton.bone(rootNode, None, boneList)

    @staticmethod
    def fromOriginal(originalSkeleton):
        sk = deepcopy(originalSkeleton)
        return sk

    def getAnimationTranformations(self, animation, time, mesh):
        self._finalTransformations = {}
        self.root.getAnimTransforms(animation, time, mesh, mat4.identity(), self._finalTransformations)
        return self._finalTransformations

    def getBindPose(self, animation, mesh):
        mId = id(mesh)
        if mId not in self._bindTransforms.keys():
            ntrans = self.getAnimationTranformations(animation, -1, mesh)
            self._bindTransforms[mId] = ntrans
        else:
            ntrans = self._bindTransforms[mId]

        return ntrans


class Model:
    def __init__(self, engine):
        """

        @rtype : Model
        """
        self._textures = engine.textures
        self._shaders = engine.shaders
        self._engine = engine
        self.materials = []
        self.animations = {}
        self.boneDict = {}
        self.hasBones = False
        self.boundingBox = None
        self._directory = ''
        self.filetitle = ''
        self.rootNode = None
        self.skeleton = None
        self._preShape = bodyShapesEnum.box

    @staticmethod
    def fromFile(filepath, engine, pretransformAccuracy, useChannel0AsUVChannel, lastUVs, uvsFilled,
                 forceStatic=False):
        """

        @rtype : Model
        """
        newModel = Model(engine)

        # pp.aiProcess_FlipWindingOrder | pp.aiProcess_FlipUVs | pp.aiProcess_MakeLeftHanded |

        ppsteps = pp.aiProcess_SortByPType | pp.aiProcess_FindInstances | pp.aiProcess_TransformUVCoords | \
                  pp.aiProcess_JoinIdenticalVertices | pp.aiProcess_GenSmoothNormals | pp.aiProcess_SplitLargeMeshes \
                  | pp.aiProcess_CalcTangentSpace | pp.aiProcess_Triangulate | pp.aiProcess_RemoveRedundantMaterials \
                  | pp.aiProcess_LimitBoneWeights | pp.aiProcess_FindInvalidData | pp.aiProcess_ValidateDataStructure\
                  | pp.aiProcess_OptimizeMeshes | pp.aiProcess_GenUVCoords | pp.aiProcess_ImproveCacheLocality | \
                  pp.aiProcess_OptimizeGraph

        logger.meassure('starts assimp scene loading')

        try:
            scene = aiImportFile(filepath, ppsteps)
        except Exception as ex:
            logger.log("Pyassimp load exception: " + str(ex))
            raise

        logger.meassure('finished pure loading. Starts nodes check and extraction')

        if scene is None:
            logger.log("The scene failed to import.")
            raise Exception("The scene failed to import.")

        if scene.mNumMeshes == 0:
            logger.log("The imported scene has no meshes.")
            raise Exception("The imported scene has no meshes.")

        cnode = scene.mRootNode
        if cnode.mNumMeshes == 0 and cnode.mNumChildren == 0:
            logger.log("The root node has nothing readable.")
            raise Exception("The root node has nothing readable.")

        newModel._directory = path.dirname(filepath)
        newModel.filetitle = path.basename(filepath)
        try:
            newModel.cacheMaterials(scene.mMaterials)
        except Exception as ex:
            logger.log('Error caching materials: ' + str(ex))
            raise

        if scene.mNumAnimations > 0 and not forceStatic:
            try:
                newModel._getAnimations(scene.mAnimations)
            except Exception as ex:
                ex.message = 'Error extracting animations: ' + ex.message
                logger.log(ex.message)
                raise
            try:
                # bnode = newModel.__getSkeletonRoot(scene.rootnode)
                bnode = scene.mRootNode
                newModel.skeleton = Skeleton(bnode, newModel.animations)
                newModel.hasBones = True
            except Exception as ex:
                ex.message = 'Error building model\'s skeleton: ' + ex.message
                logger.log(ex.message)
                raise

        world = mat4.identity()

        try:
            newModel.rootNode = Node.fromAssimpNode(cnode, scene, world, newModel.materials, useChannel0AsUVChannel,
                                                    lastUVs, uvsFilled, newModel.boneDict, forceStatic, scene.mMeshes)

            if pretransformAccuracy >= 0:
                logger.meassure('Pre calculating animation frames')
                for a in newModel.animations.values():
                    newModel.__preTransformNode(newModel.rootNode, a, pretransformAccuracy)

            newModel.boundingBox = BoundingBox()
            newModel.__get_bounding_box(newModel.boundingBox)

        except Exception as ex:
            ex.args = ('ModelClass - Error creating root node: ' + str(ex),)
            logger.log(str(ex))
            raise

        logger.meassure('Model import finished.')
        return newModel

    def __get_bounding_box(self, bb):
        self.__get_bounding_box_for_node(self.rootNode, bb)

    @staticmethod
    def __get_bounding_box_for_node(node, bbox):
        for mesh in node._meshes:
            bbox.addPoint(vec3(mesh._minmax[0]))
            bbox.addPoint(vec3(mesh._minmax[1]))

        for child in node._childNodes:
            Model.__get_bounding_box_for_node(child, bbox)

    def __getSkeletonRoot(self, bnode):
        for c in bnode.children:
            if c.name in self.boneDict.keys():
                return c
            return self.__getSkeletonRoot(c)

    def __preTransformNode(self, node, a, acc):
        for mesh in node._meshes:
            exp = 10 ** acc
            fran = range(int(a.duration * exp))
            for time in fran:
                self.skeleton.getAnimationTranformations(a, time / float(exp), mesh)

        for c in node._childNodes:
            self.__preTransformNode(c, a, acc)

    def _getAnimations(self, anims):
        for a in anims:
            nanim = Animation(a)
            self.animations[a.mName] = nanim
            nanim.printIt()
            bb = 0
            for b in nanim.boneKeys.keys():
                if b not in self.boneDict:
                    self.boneDict[b] = bb
                    bb += 1

    def cacheMaterials(self, materialsList):
        logger.meassure('material caching starts({0} materials)'.format(str(len(materialsList))))

        def tryDecode(properties):
            newDict = {}
            for n, v in properties.items():
                try:
                    n = n.decode()
                except AttributeError:
                    pass
                try:
                    v = v.decode()
                except AttributeError:
                    pass
                newDict[n] = v
            return newDict

        for mtl in materialsList:
            matdict = tryDecode(mtl.properties)
            glMaterial = Material()
            for prop, val in matdict.items():
                if 'NAME' in prop:
                    glMaterial._ID = val
                elif 'OPACITY' in prop:
                    glMaterial.opacity = val
                # elif 'clr.ambient' in prop:
                    # glMaterial.ambientColor = self.checkcolor(val)
                elif 'COLOR_DIFFUSE' in prop:
                    glMaterial.diffuseColor = self.checkcolor(val)
                elif 'COLOR_EMISSIVE' in prop:
                    glMaterial.emissiveColor = self.checkcolor(val)
                elif 'COLOR_SPECULAR' in prop:
                    glMaterial.specularColor = self.checkcolor(val)
                elif 'SHININNESS' in prop:
                    glMaterial.specularPower = val
                elif 'TEXTURE_BASE' in prop:
                    tp = path.abspath(val)
                    if not path.exists(tp):
                        tp = path.join(self._directory, path.basename(val))
                    if not path.exists(tp):
                        logger.log('Material error in {0}:\n{1}'.format(tp, 'File not found.'), 1)
                        glMaterial.diffuseTextureID = "default"
                        glMaterial.useDiffuseTexture = True
                    try:
                        self._textures.loadTexture(tp, tp)
                        glMaterial.diffuseTextureID = tp
                    except Exception as ex:
                        logger.log('Material error in {0}:\n{1}'.format(val, ex.message), 1)
                        glMaterial.diffuseTextureID = "default"
                    finally:
                        glMaterial.useDiffuseTexture = True

            self.materials.append(glMaterial)

        logger.meassure('material caching ends')

    @staticmethod
    def checkcolor(col):
        if not isinstance(col, list):
            lcol = col.tolist()
        else:
            lcol = col
        if len(lcol) == 4:
            lcol.pop()
        return lcol

    @staticmethod
    def fromGeometryModel(engine, ID, gtype, constructInfoDict):
        """

        @type constructInfoDict: dict
        """

        verts, inds, bbox, uvs = getObjectInfo(gtype, constructInfoDict)
        model = Model(engine)
        model.rootNode = Node(ID)
        model.boundingBox = bbox
        model.materials.append(Material())
        minmax = bbox.getBounds()
        uvsList = [[]] * 8
        uvsList[0] = uvs

        if gtype in [geomTypeEnum.sphere, geomTypeEnum.torusKnot]:
            model._preShape = bodyShapesEnum.sphere
            nct = NormalsCalculationTypeEnum.smooth
        elif gtype == geomTypeEnum.icosphere:
            model._preShape = bodyShapesEnum.sphere
            uvsList = UVCalculationTypeEnum.spherical
            nct = NormalsCalculationTypeEnum.smooth
        elif gtype == geomTypeEnum.box:
            model._preShape = bodyShapesEnum.box
            uvsList = UVCalculationTypeEnum.box
            nct = NormalsCalculationTypeEnum.hard
        elif gtype == geomTypeEnum.plane:
            model._preShape = bodyShapesEnum.box
            nct = NormalsCalculationTypeEnum.hard
        else:
            uvsList = UVCalculationTypeEnum.spherical
            nct = NormalsCalculationTypeEnum.smooth

        try:
            mesh = Mesh.fromObjectInfo(verts, inds, minmax, uvsList, nct, forceReIndexing=True)
        except Exception as ex:
            ex.message = 'Error creating mesh from info: ' + ex.message
            raise

        model.rootNode._meshes.append(mesh)
        return model
