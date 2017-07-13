import numpy as np
from cycgkit.cgtypes import vec3
from glaze.GL import *
from glaze.utils import sizeofArray
from os import path

from .RenderTarget_OGL3 import RenderTarget
from .shader_management.ShadersManagerClass import ShadersManager
from ..RenderTargetBase import attachmentTypeEnum, renderTextureTypeEnum
from ..base_backend import BaseBackend, _setObjectUniforms, _setSceneUniforms, setMaterialValues, \
    _setBoneTransformationsForMesh
from ...fse_management.FSEManagerClass import FSEManager, FullScreenEffect


class OGL3Backend(BaseBackend):
    def __init__(self, engine, window):
        super(OGL3Backend, self).__init__()
        self._engine = engine
        self._currentRenderTarget = None
        self.fullScreenEffects = FSEManager(engine,
                                            self)  # todo: move FSEManager to engine?, so all fseffects are shared
        # among windows
        self._defaultClearColor = vec3(0.50, 0.50, 0.50)
        self._lastClearColor = None
        self._setClearColor(self._defaultClearColor)
        self.shaders = engine.shaders
        self.textures = self._engine.textures
        self._poliCount = 0
        self.drawingData = None
        self._window = window
        self._shaderOverride = None
        self._currentFSE = None
        self._lastShader = None

        self.vertexBuffers = {}
        self.indexBuffers = {}

        self.cube_array = np.array([[-1, 1, 1, 0], [-1, 1, -1, 1], [1, 1, -1, 2],

                                    [-1, 1, 1, 3], [1, 1, -1, 4], [1, 1, 1, 5],

                                    [-1, -1, 1, 0], [-1, 1, 1, 1], [1, 1, 1, 2],

                                    [-1, -1, 1, 3], [1, 1, 1, 4], [1, -1, 1, 5],

                                    [1, -1, 1, 0], [1, 1, 1, 1], [1, 1, -1, 2],

                                    [1, -1, 1, 3], [1, 1, -1, 4], [1, -1, -1, 5],

                                    [1, -1, -1, 0], [1, 1, -1, 1], [-1, 1, -1, 2],

                                    [1, -1, -1, 3], [-1, 1, -1, 4], [-1, -1, -1, 5],

                                    [-1, -1, -1, 0], [-1, 1, -1, 1], [-1, 1, 1, 2],

                                    [-1, -1, -1, 3], [-1, 1, 1, 4], [-1, -1, 1, 5],

                                    [-1, -1, 1, 0], [1, -1, 1, 1], [1, -1, -1, 2],

                                    [-1, -1, 1, 3], [1, -1, -1, 4], [-1, -1, -1, 5]], dtype=np.float32).flatten()

        self._cubeVBO = None

        self.screenQuad_array = np.array([[-1, -1, -0.1], [1, -1, -0.1], [-1, 1, -0.1],

                                          [1, -1, -0.1], [1, 1, -0.1], [-1, 1, -0.1]], dtype=np.float32).flatten()

        self._screenQuadVBO = None

        self.screenQuadShader = None

        # debug>>>>>>>>>>>>>>>
        self.__isDebugEnabled = False
        self.wireShader = None
        # <<<<<<<<<<<<<<<<<<<<

        glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS)
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        # glDepthMask(GL_FALSE)
        glDepthFunc(GL_LEQUAL)
        # glDepthFunc(GL_LESS)

        glDepthRange(0, 1.0)

        glEnable(GL_CULL_FACE)  # <<<<<<<<<<<< Culling
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)

        glEnable(GL_BLEND)
        glEnable(GL_SAMPLE_ALPHA_TO_COVERAGE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glClearDepth(1.0)

    @staticmethod
    def getShadersManager():
        return ShadersManager

    @staticmethod
    def getRenderTarget():
        return RenderTarget

    def _setClearColor(self, color):
        """

        @type color: vec3
        """
        if not self._lastClearColor or self._lastClearColor != color:
            r, g, b = color
            glClearColor(r, g, b, 1.0)
            self._lastClearColor = color

    def drawAll(self, drawingData):
        self.drawingData = drawingData
        self._poliCount = 0
        # postUsed = False
        sceneNeeded = False

        allEffects = self.fullScreenEffects._orderedEffects

        effectsRange = range(allEffects.__len__())

        if effectsRange.__len__() > 0:
            firstEffect = allEffects[0]
            firstPass = firstEffect.getActiveTechnique().passes[0]
            lastEffect = allEffects[effectsRange.__len__() - 1]
            lastTech = lastEffect.getActiveTechnique()
            lastPass = lastTech.passes[lastTech.passes.__len__() - 1]
        else:
            firstEffect = None
            firstPass = None
            # lastEffect = None
            # lastTech = None
            lastPass = None

        for effect in allEffects:
            if effect.getActiveTechnique().needsScene and (
                            effectsRange.__len__() > 1 or len(effect.getActiveTechnique().passes) > 1):
                sceneNeeded = True
                break

        native = self.performScenePass(firstEffect, firstPass, sceneNeeded, lastPass)

        # todo: add skybox target parameter to fse to deactivate colorattachments accordingly before this.
        # if drawingData.sky is not None:
        #     if self._cubeVBO is None:
        #         self.__createCubeVBO()
        #     self._cubeVBO.bind()
        #     self.drawSky(drawingData.sky)
        #     self._cubeVBO.unbind()

        if firstPass is not lastPass:
            for effect in allEffects:
                self._renderFSEffect(effect, (not native), lastPass)
                native = True

    def performScenePass(self, firstEffect, firstPass, sceneNeeded, lastPass):
        if sceneNeeded:
            if not self.fullScreenEffects._sceneRT:
                self.fullScreenEffects._initializeSceneRT()
            self.fullScreenEffects._sceneRT._activate([attachmentTypeEnum.depth], colorIndexes=[0])
            if not self._screenQuadVBO:
                self.__createScreenQuadStuff()

        if firstEffect and '_raw' in firstPass.members['in']:
            self._renderFSEffect(firstEffect, lastPass=lastPass, isScenePass=True)
            return False
        else:
            self.drawScene(0)
            return True

    def _renderFSEffect(self, effect, fromOverride=False, lastPass=None, isScenePass=False):
        tech = effect.getActiveTechnique()
        if tech:
            self._currentFSE = effect
            assert isinstance(effect, FullScreenEffect)

            if isScenePass:
                passRange = [0]
            else:
                passRange = range(len(tech.passes))
            for i in passRange:
                if fromOverride and i == 0:
                    continue
                passOb = tech.passes[i]
                isLastPass = passOb is lastPass
                sid = effect.ID + passOb.members['vertex'] + passOb.members['fragment']
                shader = self.fullScreenEffects._e3dShaders[sid]
                if i == 0 and isScenePass:
                    self._shaderOverride = shader
                else:
                    self._shaderOverride = None
                shader.set()
                for txID in effect.textures2d:
                    tex = self.textures.getTexture(effect.ID + '_' + txID)
                    if tex:
                        shader.setTexture(txID, tex)
                for txID in effect.texturesCube:
                    tex = self.textures.getTextureCube(effect.ID + '_' + txID)
                    if tex:
                        shader.setTexture(txID, tex)

                indexes = []
                aTypes = [attachmentTypeEnum.depth]
                # aTypes = []
                targetsIDs = []
                rt = self.fullScreenEffects._builtRenderTargets.get(effect.ID)

                for outID in passOb.members['out']:
                    if outID not in ['_raw', '_depth', '_stencil', '_scene']:
                        ind = rt._attachments.get(effect.ID + '_' + outID)
                        if ind is not None:
                            indexes.append(ind)
                            targetsIDs.append(outID)

                if len(indexes) > 0:
                    rt._activate(aTypes, indexes)

                for txID in passOb.members['in']:
                    if txID not in ['_raw'] and txID not in targetsIDs:
                        realID = effect.ID + '_' + txID if txID not in ['_scene', '_depth'] else txID
                        if effect.textureType == renderTextureTypeEnum.t2D:
                            value = self.textures.getTexture(realID)
                            shader.setTexture(txID, value)
                        else:
                            pass
                            # shader.setTextureCube(txID, realID)

                for txID in passOb.members['out']:
                    if txID not in ['_scene', '_raw', '_depth', '_stencil'] and txID not in targetsIDs:
                        realID = effect.ID + '_' + txID if txID != '_scene' else txID
                        if effect.textureType == renderTextureTypeEnum.t2D:
                            value = self.textures.getTexture(realID)
                            shader.setTexture(txID, value)
                        else:
                            pass
                            # shader.setTextureCube(txID, realID)

                if isLastPass and self.fullScreenEffects._sceneRT:
                    self.fullScreenEffects._sceneRT._deActivate()

                if '_raw' in passOb.members['in']:
                    self.drawingData.clearColor = passOb.members.get('clear', self.drawingData.clearColor)
                    self.drawScene(passOb.name)
                    if rt:
                        rt._deActivate()
                elif '_scene' in passOb.members['out']:
                    if not isLastPass:
                        self.fullScreenEffects._sceneRT._activate([], colorIndexes=[0])
                    else:
                        self.setRenderTarget()
                    self._drawScreenQuad(shader)

    def drawScene(self, passN):
        self._setClearColor(self.drawingData.clearColor)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # todo: reimplement passN callback
        self.renderMeshes(self.drawingData)

    def drawSkybox(self, sky):
        # self.shader.reset()
        if not sky.shader._isSet:
            sky.shader.set()

        sky._material.setMaterialValues(self.shader)

        stride = 16
        hand = sky.shader._attributesHandlesCache['position']
        glEnableVertexAttribArray(hand)
        glVertexAttribPointer(hand, 4, GL_FLOAT, False, stride, VBO)

        glDrawArrays(GL_TRIANGLES, 0, 36)
        glDisableVertexAttribArray(hand)

    def resize(self, size):
        glViewport(0, 0, size[0], size[1])

    @staticmethod
    def _enableAttribute(shader, attribName, stride, vBuffer):
        """

        @param attribName: "color", "normal", "tangent", "bitangent", "texcoord" 0 -2,
        "boneweights", "boneindexes"
        @type attribName: str
        @param stride: vertex size
        @type stride: int
        @param vBuffer: vbo + offset
        @type vBuffer: vbo
        """
        res = shader._attributesHandlesCache.get(attribName)
        rl = []
        if res is not None:
            rl.append(res)
            glEnableVertexAttribArray(res)
            if attribName.__contains__('texcoord'):
                glVertexAttribPointer(res, 2, GL_FLOAT, False, stride, vBuffer)
            elif attribName.__contains__('boneweights'):
                glVertexAttribPointer(res, 4, GL_FLOAT, False, stride, vBuffer)
            elif attribName.__contains__('boneindexes'):
                if glVertexAttribIPointer:
                    glVertexAttribIPointer(res, 4, GL_INT, stride, vBuffer)
                else:
                    glVertexAttribPointer(res, 4, GL_FLOAT, False, stride, vBuffer)
            else:
                glVertexAttribPointer(res, 3, GL_FLOAT, False, stride, vBuffer)

        return rl

    @staticmethod
    def _disableAttribute(attribName, currentShader):
        res = currentShader._attributesHandlesCache.get(attribName, -1)
        glDisableVertexAttribArray(res)

    def __createCubeVBO(self):
        self._cubeVBO = VBO(data=self.cube_array, target=GL_ARRAY_BUFFER, usage=GL_STATIC_DRAW)

    def __createScreenQuadStuff(self):
        self._screenQuadVBO = VBO(data=self.screenQuad_array, target=GL_ARRAY_BUFFER, usage=GL_STATIC_DRAW)
        shadersPath = self._engine.path.defaults.shaders
        vs = path.join(shadersPath, 'default_sq_VS.vs')
        fs = path.join(shadersPath, 'default_sq_FS.fs')
        self.screenQuadShader = self.shaders.loadShader(vs, fs, 'default_sqShader')

    def renderMeshes(self, drawingData):
        for mesh in drawingData.meshes:
            resetRequired = True
            attribs = []
            meshid = mesh.ID
            renderDataPerInstance = drawingData.instances.get(meshid)
            if renderDataPerInstance is None or len(renderDataPerInstance) < 1:
                continue
            vertexBuffer = self.vertexBuffers.get(meshid)
            if vertexBuffer is None:
                vertexBuffer = VBO(data=mesh._vertexBufferArray, target=GL_ARRAY_BUFFER, usage=GL_STATIC_DRAW)
                self.vertexBuffers[meshid] = vertexBuffer

            indexBuffer = self.indexBuffers.get(meshid)
            if indexBuffer is None:
                indexBuffer = VBO(data=mesh._indexBufferArray, target=GL_ELEMENT_ARRAY_BUFFER, usage=GL_STATIC_DRAW)
            self.indexBuffers[meshid] = indexBuffer

            vertexBuffer.bind()
            indexBuffer.bind()

            if self._shaderOverride:
                currentShader = self._shaderOverride
                _setSceneUniforms(currentShader, drawingData.defaultSceneParams)
            else:
                currentShader = None

            for currentMat, defaultObjectParams, transformations, modelID in renderDataPerInstance:
                if not self._shaderOverride:
                    currentShader = self._engine.shaders._shadersCache[currentMat.shaderID]
                    if currentShader is None:
                        raise RuntimeError('Shader {} not found'.format(currentMat.shaderID))
                if not currentShader._isSet:
                    currentShader.set()
                    _setSceneUniforms(currentShader, drawingData.defaultSceneParams)
                    # attribs = OGL3Backend.enableAttributes(mesh, currentShader)
                if resetRequired:
                    OGL3Backend.disableAttributes(attribs)
                    attribs = OGL3Backend.enableAttributes(mesh, currentShader)
                    currentShader.reset()
                    resetRequired = False

                _setObjectUniforms(currentShader, defaultObjectParams)
                if transformations:
                    _setBoneTransformationsForMesh(currentShader, transformations, drawingData.modelBoneDirs[modelID])
                setMaterialValues(self.textures, currentShader, currentMat)
                self.renderMesh(mesh)

            OGL3Backend.disableAttributes(attribs)
            indexBuffer.unbind()
            vertexBuffer.unbind()
        self._engine.shaders._setShaderState(self._engine.shaders._currentShader, 0)

    @staticmethod
    def enableAttributes(mesh, currentShader):
        stride = int(mesh._stride)
        used_attribs = []
        for dd in mesh._declaration:
            u = OGL3Backend._enableAttribute(currentShader, dd._name, stride, dd._offset)
            used_attribs.extend(u)
        return used_attribs

    @staticmethod
    def disableAttributes(used_attribs):
        while len(used_attribs) > 0:
            glDisableVertexAttribArray(used_attribs.pop())

    def renderMesh(self, mesh):
        self._poliCount += mesh.primitiveCount
        glDrawElements(GL_TRIANGLES, mesh.indexCount, GL_UNSIGNED_INT, 0)  # Using indexing

    def _bindScreenQuad(self):
        if not self._screenQuadVBO:
            self.__createScreenQuadStuff()
        self._screenQuadVBO.bind()

    def _unbindScreenQuad(self):
        self._screenQuadVBO.unbind()

    def _drawScreenQuad(self, shader):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._bindScreenQuad()
        stride = 12
        hand = shader._attributesHandlesCache.get('position', -1)
        glEnableVertexAttribArray(hand)
        glVertexAttribPointer(hand, 3, GL_FLOAT, False, stride, 0)
        if not shader._isSet:
            shader.set()

        glDrawArrays(GL_TRIANGLES, 0, 6)
        glDisableVertexAttribArray(hand)

    @staticmethod
    def createOGL2DTexture(ID, mipmapsNumber, pix, w, h, mode1, mode2, repeat=True):
        glGetError()
        tex = np.array([0], np.uint32)
        glGenTextures(1, tex)
        glerr = glGetError()
        tex = tex[0]
        if tex < 1:
            raise RuntimeError('Unknown error {} when creating GL texture.'.format(glerr))
        glBindTexture(GL_TEXTURE_2D, tex)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        if mipmapsNumber < 0:
            mipmapsNumber = 0

        # MANDATORY  >>>>>>>>>>>
        if repeat:
            edgeMode = GL_REPEAT
        else:
            edgeMode = GL_CLAMP_TO_EDGE

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, edgeMode)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, edgeMode)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        if mipmapsNumber > 0 and repeat:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        else:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        # <<<<<<<<<<<<<<<<<<<<<<
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
        if mipmapsNumber > 0 and repeat:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, mipmapsNumber - 1)
            # glHint(GL_GENERATE_MIPMAP_HINT, GL_NICEST)
        else:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)

        glTexImage2D(GL_TEXTURE_2D, 0, mode1, w, h, 0, mode2, GL_UNSIGNED_BYTE, pix)
        glerr = glGetError()
        if glerr:
            raise RuntimeError('Unknown error {} when creating GL texture.'.format(glerr))

        if mipmapsNumber > 0 and repeat:
            try:
                glEnable(GL_TEXTURE_2D)
                glGenerateMipmap(GL_TEXTURE_2D)
            except Exception:
                self._engine.log('Error generating mipmaps for {}: glerror {}'.format(ID, glGetError()),
                           logLevelsEnum.warning)
                # glBindTexture(GL_TEXTURE_2D, 0) #Raises shader compiling error on intel GMA 965 + Windows
        # glFlush()
        return tex

    def setRenderTarget(self, rTarget=None, attachmentTypes=None, colorIndexes=None):
        """

        @type rTarget: RenderTarget
        """
        if not rTarget:
            self.unsetRenderTarget()
            return
        if not colorIndexes:
            colorIndexes = []
        if not attachmentTypes:
            attachmentTypes = []

        if self._currentRenderTarget is not rTarget:
            self._currentRenderTarget = rTarget

        try:
            rTarget._act(attachmentTypes, colorIndexes)
        except:
            self.unsetRenderTarget()
            raise

    def unsetRenderTarget(self, rTarget=None):
        """

        @type rTarget: RenderTarget
        """

        if rTarget:
            if self._currentRenderTarget is rTarget:
                self._currentRenderTarget = None
                rTarget._isActive = False
                glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
            rTarget._isActive = False
        else:
            glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
            self._currentRenderTarget = None

    def getActiveRenderTarget(self):
        realN = np.array([0], np.int32)
        glGetIntegerv(GL_FRAMEBUFFER_BINDING, realN)
        storedN = self._currentRenderTarget._fbo
        if storedN and real != stored:
            self.setRenderTarget()
            return 0
        else:
            return realN

    def switchMultiSample(self, value):
        if bool(value):
            glEnable(GL_MULTISAMPLE)
        else:
            glDisable(GL_MULTISAMPLE)

    def terminate(self):
        def acum(buffVals):
            for b in buffVals:
                buff, vert = b._get_buff_vert_arr()
                vbos.append(int(buff))
                vaos.append(int(vert))

        vbos = []
        vaos = []

        acum(self.indexBuffers.values())
        acum(self.vertexBuffers.values())
        vboarr = np.asarray(vbos, np.uint32)
        vaoarr = np.asarray(vaos, np.uint32)

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        if len(vboarr) > 0:
            glDeleteBuffers(len(vboarr), vboarr)

        if len(vaoarr) > 0:
            glDeleteVertexArrays(len(vaoarr), vaoarr)

            # todo: delete sky and fsq buffers

    @staticmethod
    def _getMaxColorAttachments():
        ret = np.empty((1,), np.int32)
        glGetIntegerv(GL_MAX_COLOR_ATTACHMENTS, ret)
        return int(ret)


class VBO:
    def __init__(self, data, target, usage):
        vertexbuffer = np.array([0], np.uint32)
        glGenBuffers(1, vertexbuffer)
        glBindBuffer(target, vertexbuffer)
        size = sizeofArray(data)
        glBufferData(target, size, data, usage)
        self.bufferID = vertexbuffer

        VertexArrayID = np.array([0], np.uint32)
        glGenVertexArrays(1, VertexArrayID)
        glBindVertexArray(VertexArrayID)
        self.arrayID = VertexArrayID

        glBindVertexArray(0)
        glBindBuffer(target, 0)

        self.target = target

    def bind(self):
        glBindVertexArray(self.arrayID)
        glBindBuffer(self.target, self.bufferID)

    def unbind(self):
        glBindVertexArray(0)
        glBindBuffer(self.target, 0)

    def terminate(self):
        self.unbind()
        glDeleteBuffers(1, np.asarray(self.bufferID, np.uint32))
        glDeleteVertexArrays(1, np.asarray(self.arrayID, np.uint32))

    def _get_buff_vert_arr(self):
        return self.bufferID, self.arrayID
