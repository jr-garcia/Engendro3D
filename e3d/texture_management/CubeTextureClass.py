from os import listdir, path
import numpy as np
from glaze.GL import glGenTextures, glDeleteTextures, glTexParameteri, glTexImage2D, glBindTexture, GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_TEXTURE_MIN_FILTER, \
    GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_UNSIGNED_BYTE, GL_CLAMP_TO_EDGE, GL_TEXTURE_WRAP_R, GL_TEXTURE_CUBE_MAP_POSITIVE_X, GL_TEXTURE_CUBE_MAP_NEGATIVE_X, \
    GL_TEXTURE_CUBE_MAP_POSITIVE_Y, GL_TEXTURE_CUBE_MAP_NEGATIVE_Y, GL_TEXTURE_CUBE_MAP_POSITIVE_Z, \
    GL_TEXTURE_CUBE_MAP_NEGATIVE_Z, GL_TEXTURE_CUBE_MAP


class CubeTexture(object):
    def __init__(self, engine, ID):
        self.engine = engine
        self.__xNeg = ''
        self.__yNeg = ''
        self.__xPos = ''
        self.__yPos = ''
        self.__zPos = ''
        self.__zNeg = ''
        self._nativeTexture = -1
        self.ID = ID
        # TODO: add ID existence check
        # TODO: inherit from base3Dobject3

    def loadFromFolder(self, folderPath, getPixels):
        # todo: move to backend
        files = {}

        sides = [
            GL_TEXTURE_CUBE_MAP_POSITIVE_X,  # right
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X,  # left
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y,  # top
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,  # bottom
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z,  # back
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z  # front
        ]

        filenames = ['posx', 'negx', 'posy', 'negy', 'posz', 'negz']
        filesInDir2 = listdir(folderPath)
        filesInDir = []
        for rf in filesInDir2:
            rff = path.join(folderPath, rf)
            if path.isfile(rff):
                filesInDir.append(rff)
        if len(filesInDir) < 6:
            raise AttributeError('Not enough files in folder:\n' + folderPath)
        for f in filesInDir:
            if len(files) == 6:
                break
            filename = path.basename(f)
            for k in filenames:
                if filename.lower().__contains__(k):
                    files[k] = f
                    break

        if len(files) < 6:
            raise RuntimeError('Not enough \'valid\' files in folder.')

        self.__xNeg = files['negx']
        self.__xPos = files['posx']
        self.__yNeg = files['negy']
        self.__yPos = files['posy']
        self.__zNeg = files['negz']
        self.__zPos = files['posz']
        tex = -1
        try:

            tex = np.empty((1,), np.uint32)
            glGenTextures(1, tex)
            # glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            # glActiveTexture(GL_TEXTURE0)
            # glEnable(GL_TEXTURE_CUBE_MAP)
            glBindTexture(GL_TEXTURE_CUBE_MAP, tex)

            # NO OPTIONAL>>>>>>>>>>>
            glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
            # <<<<<<<<<<<<<<<<<<<<<<

            for name in filenames:
                index = filenames.index(name)
                pix, w, h, mode1, mode2 = getPixels(files[name])
                'glTexImage2D(unsigned int target, int level, int internalformat, int width, int height, int border, ' \
                'unsigned int format, unsigned int type, voidpable pixels)'
                glTexImage2D(sides[index], 0, mode1, w, h, 0, mode2, GL_UNSIGNED_BYTE, pix)

            self._nativeTexture = tex
        except Exception:
            try:
                glDeleteTextures(tex)
            except:
                pass
            raise
