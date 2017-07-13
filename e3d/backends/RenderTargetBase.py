class renderTextureTypeEnum(object):
    cube = 'cube'
    t2D = '2d'


class attachmentTypeEnum(object):
    color = 'color'
    depth = 'depth'
    stencil = 'stencil'


class RTBase:
    def createDepthAttachment(self, size):
        pass

    def __init__(self, engine, textureType, hasDepth=False):
        """
        Object that allows render to texture.

        @type textureType: renderTextureTypeEnum
        @type engine: Engine
        @rtype : RTBase
        """
        self._attachments = {}
        self._engine = engine
        self.textureType = textureType
        self._textures = engine.textures
        self._isActive = False

        self._hasDepth = hasDepth

        self._texturesDict = {}

    def __repr__(self):
        return 'colors={}, depth={}, active={}'.format(len(self._attachments), self._hasDepth,
                                                       str(self._isActive).upper())

    def _addAtachmentToFrameBuffer(self, textureType, size, comp, type, atachType, texture):
        pass

    def getSizeAsList(self):
        return [self.__width, self.__height]

    def _activate(self, atachmentTypes=None, colorIndexes=None):
        pass

    def _act(self, atachmentTypes=None, colorIndexes=None):
        """

        @param atachmentTypes:  Members of attachmentTypeEnum to activate
        @type atachmentTypes: list
        @param colorIndexes: Set to -1 to activate all color atachments
        @type colorIndexes:  list
        """
        pass

    def _deActivate(self):
        pass

    def destroy(self):
        pass

    def getTexture(self, atachmentType, colorIndex=0):
        pass

    def createColorAttachments(self, colorIDs, sizes):
        """


        @type sizes: list
        @type colorIDs: list
        """
        pass

    def resize(self):
        pass

    def __del__(self):
        self._delete()

    def _delete(self):
        pass

    def _terminate(self):
        pass

    def getNumber(self):
        pass
