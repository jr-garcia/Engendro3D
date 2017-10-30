from PIL import Image
import numpy as np
# from ParalellServiceClass import ParalellService
# from CubeTextureClass import CubeTexture


class TexturesManagerServer(object):
    @staticmethod
    def getPILpixels(path):
        try:
            im = Image.open(path)
            w, h = im.size[0], im.size[1]

            if im.mode != 'RGBA':
                im = im.convert("RGBA")

            pix = np.array(im, np.uint8)
            im.close()
            red, green, blue, alpha = pix.T
            pix = np.array([blue, green, red, alpha])
            return pix.transpose().flatten(), w, h
        except Exception:
            raise

    def loadTexture(self, filePath, ID, mipmapsNumber, repeat):
        """

        @param mipmapsNumber:
        @type mipmapsNumber:
        @type ID: str
        @type filePath: str
        @rtype : None
        @param filePath:
        @param ID:
        @param repeat:
        @type repeat:
        """
        try:
            pix, w, h = TexturesManagerServer.getPILpixels(filePath)
            self.ready('loadTexture', [pix, w, h, ID, mipmapsNumber, repeat])
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
            cube.loadFromFolder(folderPath, TexturesManagerServer.getPILpixels)

        return cube


def serve(remotequeue, localqueue):
    """

    @param localqueue:
    @type localqueue: multiprocessing.Queue
    @type remotequeue: multiprocessing.Queue
    """
    texMan = TexturesManagerServer(remotequeue, localqueue)
    texMan.start()
