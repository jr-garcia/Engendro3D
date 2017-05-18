from cycgkit.cgtypes import mat4
from .MeshClass import Mesh


class Node(object):
    def __init__(self, ID=''):
        """


        @type ID: str
        @rtype : Node
        """
        self._childNodes = []
        self._meshes = []
        self._ID = ID
        self.visible = True
        self.transformation = mat4.identity()

    @staticmethod
    def fromAssimpNode(cnode, scene, parentTransform, matcache, useChannel0AsUVChannel, lastUVs, uvsfilled,
                       boneDict, forceStatic, meshes):
        """





        @param forceStatic:
        @type parentTransform: cycgkit.cgtypes.mat4
        @type cnode: pyassimp.structs.Node
        @rtype : Node
        """
        self = Node(cnode.mName)
        # self.transformation = mat4(cnode.transformation).transpose() * parentTransform
        self.transformation = mat4(cnode.mTransformation) * parentTransform
        # self.transformation = parentTransform * mat4(cnode.transformation).transpose()

        if useChannel0AsUVChannel > 0:
            if not uvsfilled:
                if cnode.mNumMeshes > 0:
                    for m in scene.mMeshes:
                        try:
                            tv = m.mTexturecoords[0]
                        except Exception:
                            tv = None
                        if tv is None:
                            raise AttributeError("The model is not fully UV mapped.")
                        lastind = len(lastUVs) - 1
                        if lastind == 0:
                            lastind = -1
                        lastind += 1
                        f = 0
                        k = lastind
                        while k <= lastind + len(tv) - 1:
                            lastUVs.append(tv[f])
                            f += 1
                            k += 1
                    if len(cnode.mChildren) > 0:
                        for cn in cnode.mChildren:
                            _ = Node.fromAssimpNode(cn, scene, device, self.transformation, matcache,
                                                    useChannel0AsUVChannel, lastUVs,
                                                    uvsfilled, forceStatic, meshes)
                return
        if cnode.mNumMeshes > 0:
            for mi in cnode.mMeshes:
                mesh = Mesh.fromAssimpMesh(meshes[mi], self.transformation, useChannel0AsUVChannel,
                                           lastUVs, boneDict, forceStatic)
                self._meshes.append(mesh)
        if cnode.mNumChildren > 0:
            for cn in cnode.mChildren:
                n = Node.fromAssimpNode(cn, scene, self.transformation, matcache, useChannel0AsUVChannel, lastUVs,
                                        uvsfilled, boneDict, forceStatic, meshes)
                if (len(n._meshes) > 0) | (len(n._childNodes) > 0):
                    self._childNodes.append(n)

        return self