from glaze.GL import *
from glaze import GL
import numpy as np

from ..RenderTargetBase import *


class textureFormatEnum(object):
    rgba = GL_RGBA
    rgb32f = GL_RGB32F
    r32f = GL_R32F
    d24s8 = GL_DEPTH24_STENCIL8


class RenderTarget(RTBase):
    def createDepthAttachment(self, size):
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self._fbo)
        # comp = GL_DEPTH24_STENCIL8  # GL_DEPTH_COMPONENT
        # ftype = GL_BYTE # GL_FLOAT
        comp = GL_DEPTH_COMPONENT
        ftype = GL_FLOAT

        if '_depth' not in self._textures._textureCache:
            texture = np.empty((1,), np.uint32)
            glGenTextures(1, texture)
            self._textures._textureCache['_depth'] = texture
        else:
            texture = self._textures._textureCache['_depth']

        self._addAtachmentToFrameBuffer(self.textureType, size, comp, ftype, GL_DEPTH_ATTACHMENT, texture)
        res = self._isStatusWrong()
        # glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        if not res:
            self._hasDepth = True
        else:
            raise RuntimeError('createDepthAttachment error: ' + str(res))

    def __init__(self, engine, backend, textureType, hasDepth=False):
        """
        Object that allows render to texture.

        @param colorIndexes: List containig the required color atachments for the RenderTarget.
                             Defaults to 0. Maximum value must be <= RenderTarget.maxColorAtachments
        @type textureType: renderTextureTypeEnum
        @type colorIndexes: list
        @type engine: ManagersReferenceHolder
        @rtype : RenderTargetBaseClass
        """
        RTBase.__init__(self, engine, textureType, hasDepth)
        self._backend = backend

        self._fbo = np.empty((1,), np.uint32)
        glGenFramebuffers(1, self._fbo)

        # if hasStencil:
        #     comp = GL_DEPTH_COMPONENT
        #     type = GL_FLOAT
        #     self._addAtachmentToFrameBuffer(textureType, comp, type, GL_STENCIL_ATTACHMENT, textures)
        res = self._isStatusWrong()
        if res:
            raise RuntimeError("Error creating the RenderTarget: " + res)
        # glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        # glBindTexture(GL_TEXTURE_2D, 0)

    def _isStatusWrong(self):
        e = glCheckFramebufferStatus(GL_DRAW_FRAMEBUFFER)
        if e != GL_FRAMEBUFFER_COMPLETE:
            return glGetError()
        else:
            return None

    def _addAtachmentToFrameBuffer(self, textureType, size, comp, type, atachType, texture):
        width, height = size
        if textureType == renderTextureTypeEnum.t2D:
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexImage2D(GL_TEXTURE_2D, 0, comp, width, height, 0, comp, type, None)
            glFramebufferTexture2D(GL_DRAW_FRAMEBUFFER, atachType, GL_TEXTURE_2D, texture, 0)
            glBindTexture(GL_TEXTURE_2D, 0)
            self._texturesDict[atachType] = texture
        elif textureType == renderTextureTypeEnum.cube:
            raise NotImplementedError('')
            # void glFramebufferTexture3D(GLenum target, GLenum attachment, GLenum textarget, GLuint texture,
            # GLint level, GLint layer)
            #   Parameters:
            #     target: GL_DRAW_FRAMEBUFFER, GL_READ_FRAMEBUFFER, or GL_FRAMEBUFFER. GL_FRAMEBUFFER is equivalent to
            #             GL_DRAW_FRAMEBUFFER;
            #     attachment: GL_COLOR_ATTACHMENTi, GL_DEPTH_ATTACHMENT, GL_STENCIL_ATTACHMENT or
            #                 GL_DEPTH_STENCIL_ATTACHMMENT;
            #     textarget: the type of texture to attatch, can be the face of a cube map;
            #     texture: the texture name. If zero then the previously attached texture is detached;
            #     level: the selected mipmap level;
            #     layer: the selected layer.
        else:
            raise AttributeError('Wrong textureType')

    def getSizeAsList(self):
        return [self.__width, self.__height]

    def _activate(self, atachmentTypes=None, colorIndexes=None):
        self._backend.setRenderTarget(self, atachmentTypes, colorIndexes)

    def _act(self, atachmentTypes=None, colorIndexes=None):
        """

        @param atachmentTypes:  Members of attachmentTypeEnum to activate
        @type atachmentTypes: list
        @param colorIndexes: Set to -1 to activate all color atachments
        @type colorIndexes:  list
        """
        # Todo:make this process dependent of backend to avoid confusion
        if not isinstance(atachmentTypes, list):
            atachmentTypes = [atachmentTypes]

        if not isinstance(colorIndexes, list):
            colorIndexes = [colorIndexes]

        if colorIndexes is None and atachmentTypes is None:
            return # todo: set here all color targets to ativate them

        attachments = []

        # if atachmentTypes and attachmentTypeEnum.depth in atachmentTypes and self._hasDepth:
        #     attachments.append(GL_DEPTH_ATTACHMENT)

        for unit in colorIndexes:
            attachments.append(getattr(GL, 'GL_COLOR_ATTACHMENT' + str(unit)))

        size = len(attachments)
        att = np.array(attachments, dtype=np.uint32)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self._fbo)
        glDrawBuffers(size, att)

        res = self._isStatusWrong()
        if res:
            raise RuntimeError('Error activating RenderTarget: ' + res)

    def _deActivate(self):
        # glDrawBuffers(0, None)
        self._backend.unsetRenderTarget(self)

    def destroy(self):
        glDeleteFramebuffers(self._fbo)

    def getTexture(self, atachmentType, colorIndex=0):
        """


        @type colorIndex: int
        @type atachmentType: attachmentTypeEnum
        """
        if atachmentType == attachmentTypeEnum.color:
            atachType = getattr(GL, 'GL_COLOR_ATTACHMENT' + str(colorIndex))
        elif atachmentType == attachmentTypeEnum.depth:
            atachType = GL_DEPTH_ATTACHMENT
        elif atachmentType == attachmentTypeEnum.stencil:
            atachType = GL_STENCIL_ATTACHMENT
        else:
            raise TypeError('Wrong atachmentType.')

        return self._texturesDict[atachType]

    def createColorAttachments(self, colorIDs, sizes):
        """


        @type sizes: list
        @type colorIDs: list
        """
        if isinstance(colorIDs, str):
            colorIDs = [colorIDs]
        if isinstance(colorIDs, int):
            sizes = [sizes]
        finals = []
        colorIndexes = range(colorIDs.__len__())
        for i in colorIndexes:
            col = colorIndexes[i]
            # if col not in self._attachments.keys():
            finals.append((col, sizes[i], colorIDs[i]))
            self._attachments[colorIDs[i]] = col

        texturesSize = len(finals)

        # if texturesSize == 0:
        #     raise AttributeError('Error in createColorAttachments: All specified colorIndexes exist already.')

        textures = np.empty((texturesSize,), np.uint32)
        glGenTextures(texturesSize, textures)

        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self._fbo)

        tIDs = []

        for unit, size, ID in finals:
            attachType = getattr(GL, 'GL_COLOR_ATTACHMENT' + str(unit))
            comp = GL_RGBA
            ttype = GL_UNSIGNED_BYTE
            texun = textures[unit]
            self._addAtachmentToFrameBuffer(self.textureType, size, comp, ttype, attachType, texun)
            tIDs.append((ID, texun))

        self._textures._addTextureIDs(tIDs)

        res = self._isStatusWrong()
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        if res:
            raise RuntimeError('createColorAttachments error: ' + res)

    def resize(self):
        raise NotImplementedError('resize RT')

    def __del__(self):
        self._delete()

    def _terminate(self):
        if self._fbo:
            glDeleteFramebuffers(self._fbo)

    def getNumber(self):
        return self._fbo
