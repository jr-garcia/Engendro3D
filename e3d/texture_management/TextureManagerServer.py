from PIL import Image as img

import numpy as np
from glaze.GL import GL_RGB8, GL_RGB, GL_RGBA8, GL_RGBA
from importlib import import_module

# from ParalellServiceClass import ParalellService
# from CubeTextureClass import CubeTexture


class TexturesManagerServer():

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
            pix, w, h, mode1, mode2 = self.getPILpixels(filePath)
            self.ready('loadTexture', [pix, w, h, mode1, mode2, ID, mipmapsNumber, repeat])
        except Exception as ex:
            self.exception(ex)
            raise

    @staticmethod
    def getSFMLpixels(path):
        # image.LoadFromFile(fp)
        image = sfml.Image.from_file(path)
        pix = bytearray(image.pixels.data)
        w, h = image.size[0], image.size[1]
        return pix, w, h, GL_RGBA, GL_RGBA

    @staticmethod
    def getSDLpixels(path):
        raise NotImplementedError('getSDLpixels not working')
        # Surface = sdlimage.IMG_Load(path)
        # if not Surface:
        #     raise RuntimeError('Error loading image in: ' + fp)
        # Mode = GL_RGB
        # if Surface.contents.format.contents.BytesPerPixel == 4:
        #     Mode = GL_RGBA
        # pix = str(Surface.contents)
        # return pix, w, h, Mode

    @staticmethod
    def getPILpixels(path):
        try:
            im = img.open(path)
            w, h = im.size[0], im.size[1]

            if im.mode == 'RGB':
                mode1 = GL_RGB8
                mode2 = GL_RGB
            else:
                mode1 = GL_RGBA8
                mode2 = GL_RGBA

            pix = np.array(im, np.uint8).flatten()
            im.close()
            return pix, w, h, mode1, mode2
        except Exception:
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
                folderPath = self.manfred.io.findPath(folderPath)
            if not folderPath:
                logger.log('Error loading cube texture {0}:\n{1}'.format(folderPath, 'Folder not found.'), 1)

            cube = CubeTexture(self.manfred, ID)
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
