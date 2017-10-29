# from ParalellServiceClass import ParalellService
# from CubeTextureClass import CubeTexture


class TexturesManagerServer(object):

    def loadTexture(self, filePath, ID, mipmapsNumber, repeat):
        """

        @param mipmapsNumber:
        @type mipmapsNumber:
        @type ID: str
        @type filePath: str
        @rtype : None
        @param filePath:
        @param ID:
        """
        try:
            pix, w, h, mode1, mode2 = self._engine.backend(filePath)
            self.ready('loadTexture', [pix, w, h, mode1, mode2, ID, mipmapsNumber, repeat])
        except Exception as ex:
            self.exception(ex)
            raise

    def loadCubeTexture(self, folderPath, ID):
        """

        @type ID: str
        @param ID:
        @param folderPath:
        @type folderPath: str
        @rtype : None
        """

        cube = self._cubeTexCache.get(ID)
        if not cube:
            if not os.path.exists(folderPath):
                folderPath = self.engine.io.findPath(folderPath)
            if not folderPath:
                self._engine.log('Error loading cube texture {0}:\n{1}'.format(folderPath, 'Folder not found.'), 1)

            cube = CubeTexture(self.engine, ID)
            cube.loadFromFolder(folderPath, self._engine.backend.getPILpixels)

        return cube


def serve(remotequeue, localqueue):
    """

    @param localqueue:
    @type localqueue: multiprocessing.Queue
    @type remotequeue: multiprocessing.Queue
    """
    texMan = TexturesManagerServer(remotequeue, localqueue)
    texMan.start()
