import numpy as np
from os import stat, path, listdir
from glaze.GL import *

from .ShaderClass import Shader
from ....LoggerClass import logger, logLevelsEnum
from ...base_backend import CompilationError


class ShadersManager(object):
    class shaderTypesEnum(object):
        vertex = GL_VERTEX_SHADER
        fragment = GL_FRAGMENT_SHADER

        def __init__(self):
            pass

    def __init__(self):
        """



        @rtype : ShadersManager
        """
        self._shadersCache = {}
        self._defaultShader = None
        self._context = None
        self._maxTextureUnits = 0
        self._engine = None
        self._currentShader = None
        self._shaderFiles = {}
        self.ShaderClass = Shader
        self._dissectErrors = _dissectShaderCompilingErrors

    def _setShaderState(self, shader, activeState):
        if activeState:
            if self._currentShader and self._currentShader.ID != shader.ID:
                self._currentShader._isSet = False
            shader.reset()
            glUseProgram(shader)
            shader._isSet = True
            self._currentShader = shader
        else:
            if self._currentShader and self._currentShader.ID == shader.ID:
                glUseProgram(0)
                self._currentShader = None
            if shader:
                shader._isSet = False

    def _getMaxTexts(self):
        """
        Maximum simultaneous textures usable per shader in this computer.
        @rtype : int
        """
        return self._maxTextureUnits

    maxTextureImageUnits = property(_getMaxTexts)

    def initialize(self, engine):
        self._engine = engine
        ret = np.array([0], np.int32)
        glGetIntegerv(GL_MAX_TEXTURE_IMAGE_UNITS, ret)
        self._maxTextureUnits = ret[0]
        # GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS  ->   for all shader stages
        # GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS    ->   for vertex shader stage
        logger.log('Max Texture Units per fragment shader: ' + str(self._maxTextureUnits), logLevelsEnum.debug)
        dire = path.join(self._engine.path, 'defaults', 'shaders')
        vs = path.join(dire, "defaultVS.glsl")
        fs = path.join(dire, "defaultFS.glsl")
        # vs = path.join(dire, "lightVS.vs")
        # fs = path.join(dire, "lightFS.fs")
        try:
            self.loadShader(vs, fs, "default")
            self._defaultShader = self._shadersCache.get('default')
        except Exception:
            raise

    def loadShader(self, VSfilename, FSfilename, ID):
        """




        @type ID: str
        @type FSfilename: str
        @type VSfilename: str
        @param VSfilename:Vertex Shader Filename
        @param FSfilename:Fragment Shader Filename
        @param ID:Name for future reference (should be unique)
        """
        newEffect = self.getShader(ID)

        if newEffect is None:
            try:
                absVSfilename = path.abspath(VSfilename)
                if not path.exists(absVSfilename):
                    logger.log(absVSfilename + ' not found. Searching in default location.', logLevelsEnum.info)
                    absVSfilename = path.join(self._engine.path, 'defaults', 'shaders', VSfilename)
                with open(absVSfilename, 'r') as vs:
                    vertexSource = str.join("", vs.readlines())

                absFSfilename = path.abspath(FSfilename)
                if not path.exists(absFSfilename):
                    logger.log(absFSfilename + ' not found. Searching in default location.', logLevelsEnum.info)
                    absFSfilename = path.join(self._engine.path, 'defaults', 'shaders', FSfilename)
                with open(absFSfilename, 'r') as fs:
                    fragmentSource = str.join("", fs.readlines())

                try:
                    glProg = nativeCompile(vertexSource, fragmentSource)
                    newEffect = Shader(glProg, ID, self)
                except CompilationError as ex:
                    parsed = _dissectShaderCompilingErrors(ex.args[1], self._engine.globals.oglversionraw)
                    vsfs = "in \'{}\' {} SHADER: \n".format(ID, ex.args[0].upper()) + parsed
                    raise CompilationError(vsfs)

            except Exception:
                raise
            self._shaderFiles[ID] = (ShaderFile(absVSfilename), ShaderFile(absFSfilename))
            self._shadersCache[ID] = newEffect

        return newEffect

    def refreshShader(self, ID, absVSfilename, absFSfilename):
        vs = open(absVSfilename, 'r')
        vertexSource = str.join("", vs.readlines())
        vs.close()

        fs = open(absFSfilename, 'r')
        fragmentSource = str.join("", fs.readlines())
        fs.close()

        try:
            glProg = nativeCompile(vertexSource, fragmentSource)
            newEffect = Shader(glProg, ID, self)
            self._shadersCache[ID].terminate()
            self._shadersCache[ID] = newEffect
            vsfs = "shader \'{}\' refreshed".format(ID)
            logger.log(vsfs, logLevelsEnum.info)
        except CompilationError as ex:
            parsed = _dissectShaderCompilingErrors(ex.args[1], self._engine.globals.oglversionraw)
            vsfs = "Error refreshing \'{}\' {} SHADER: \n".format(ID, ex.args[0].upper()) + parsed
            logger.log(CompilationError(vsfs), logLevelsEnum.error)

    @staticmethod
    def checkAndCompile(source, shaderType):
        glGetError()
        shaderObject = createShader(shaderType)

        uploadSource(shaderObject, source)

        typestr = 'vertex' if shaderType == GL_VERTEX_SHADER else 'fragment'
        compileShader(shaderObject, typestr)

        return shaderObject

    @staticmethod
    def compileProgram(fragmentShaderObject, vertexShaderObject):
        ProgramObject = glCreateProgram()
        glAttachShader(ProgramObject, vertexShaderObject)
        glAttachShader(ProgramObject, fragmentShaderObject)
        glLinkProgram(ProgramObject)
        error = glGetError()
        if error:
            raise RuntimeError('glLinkProgram error ' + glErrorFromCode(error))
        ret = checkStatus(ProgramObject, GL_LINK_STATUS)
        if ret:
            raise CompilationError('', 'shader link failure: ' + ret)
        return ProgramObject

    def shaderExists(self, ID):
        return ID in self._shadersCache

    def getShader(self, ID):
        """


        @type ID: str
        @rtype : Shader
        """
        return self._shadersCache.get(ID)

    def update(self):
        self.checkForChanges()

    def checkForChanges(self):
        for ID, files in self._shaderFiles.items():
            VSfile, FSfile = files
            if VSfile.isModified() or FSfile.isModified():
                self.refreshShader(ID, VSfile.filePath, FSfile.filePath)

    def terminate(self):
        for e in self._shadersCache.values():
            e.terminate()


def getShaderInfoLog(sObject):
    length = np.array([1], np.int32)
    glGetShaderiv(sObject, GL_INFO_LOG_LENGTH, length)
    message = np.array([0] * int(length[0]), np.int8)
    glGetShaderInfoLog(sObject, len(message), length, message)
    return ''.join([chr(c) for c in message])


def getProgramInfoLog(sObject):
    length = np.array([1], np.int32)
    glGetProgramiv(sObject, GL_INFO_LOG_LENGTH, length)
    message = np.array([0] * int(length[0]), np.int8)
    glGetProgramInfoLog(sObject, len(message), length, message)
    return ''.join([chr(c) for c in message])


def glErrorFromCode(code):  # todo: move to glaze
    import glaze.GL
    glDir = dir(glaze.GL)
    for v in glDir:
        val = getattr(glaze.GL, v)
        if val == code:
            return v


def createShader(stype):
    return glCreateShader(stype)


def uploadSource(shader, source):
    vlength = np.array([len(source)], np.int32)
    glShaderSource(shader, 1, [source], vlength)
    error = glGetError()
    if error:
        raise RuntimeError('glShaderSource error ' + glErrorFromCode(error))


def compileShader(sObject, typeStr):
    glCompileShader(sObject)
    error = glGetError()
    if error:
        raise RuntimeError('glCompileShader error ' + glErrorFromCode(error))

    ret = checkStatus(sObject, GL_COMPILE_STATUS)
    if ret:
        raise CompilationError(typeStr, 'shader compile failure: ' + ret)


def checkStatus(sObject, what):
    res = np.array([0], np.int32)
    if what == GL_COMPILE_STATUS:
        glGetShaderiv(sObject, what, res)
    else:
        glGetProgramiv(sObject, what, res)

    if res[0] == GL_FALSE:
        if what == GL_COMPILE_STATUS:
            message = getShaderInfoLog(sObject)
        else:
            message = getProgramInfoLog(sObject)
    else:
        message = ''
    return message


def nativeCompile(vertexSource, fragmentSource):
    glGetError()

    vertexShaderObject = ShadersManager.checkAndCompile(vertexSource, GL_VERTEX_SHADER)
    fragmentShaderObject = ShadersManager.checkAndCompile(fragmentSource, GL_FRAGMENT_SHADER)

    ProgramObject = ShadersManager.compileProgram(fragmentShaderObject, vertexShaderObject)

    try:
        glDetachShader(ProgramObject, fragmentShaderObject)
        glDetachShader(ProgramObject, vertexShaderObject)
        glDeleteShader(fragmentShaderObject)
        glDeleteShader(vertexShaderObject)  # todo: move to shader terminate?
    except:
        pass

    return ProgramObject


def _dissectShaderCompilingErrors(mess, driverName):
    """

    @type driverName: str
    """
    lname = driverName.lower()
    if 'nvidia' in lname:
        return _dissectShaderCompilingErrorsNvidia(mess)
    elif 'mesa' in lname or 'intel' in lname:
        return _dissectShaderCompilingErrorsMesa(mess)
    else:
        raise NotImplementedError('Shader compile error dissection not implemented for {}'.format(driverName))


def _dissectShaderCompilingErrorsNvidia(mess):
    """


    @rtype : str
    @type mess: str
    """
    errorlist = mess.split('\n')
    errstr = ''
    cerr = ''
    lastline = ''

    for ind in range(len(errorlist)):
        i = errorlist[ind]
        if i == '':
            errorlist.remove(i)
        else:
            i = i.replace('"', "'")
            i = i.replace("`", "'")
            errorlist[ind] = i

    for i in errorlist:
        if i.lower().__contains__("shader compile failure"):
            i = i[i.find(': ', 10) + 2: len(i)]
            i = i.replace('\\', '')
        ct = i.split(': ')
        currline = ct[1] if ct[0].lower().__contains__('error') else ct[0]
        if currline.startswith('0'):
            lc = currline.strip().split('(')[1].strip(')')  # todo: add character location
        else:
            lc = lastline

        if not lc == lastline:
            lastline = lc
            if errstr != '':
                errstr += '\n\n'
            cerr = 'Line {}: '.format(lc)
        else:
            if errstr != '':
                errstr += '\n\t'
        if len(ct) > 2:
            cerr += ct[2]
        elif len(ct) > 1:
            cerr += ct[1]
        else:
            cerr += ct[0]
        if len(ct) > 3:
            cerr += ': ' + ct[3]
        errstr += cerr
        cerr = ''

    if errstr == '':
        errstr = cerr
    return errstr


def _dissectShaderCompilingErrorsMesa(mess):
    """


    @rtype : str
    @type mess: str
    """
    errorlist = mess.split('\n')
    errstr = ''
    cerr = ''
    lastline = ''

    for ind in range(len(errorlist)):
        i = errorlist[ind]
        if i == '':
            errorlist.remove(i)
        else:
            i = i.replace('"', "'")
            i = i.replace("`", "'")
            errorlist[ind] = i

    for i in errorlist:
        if i.lower().__contains__("shader compile failure"):
            i = i[i.find(': ', 10) + 2: len(i)]
            i = i.replace('\\', '')
        ct = i.split(': ')
        currline = ct[1] if ct[0].__contains__('ERROR') or ct[0].__contains__('error') else ct[0]
        lc = currline.strip().strip(')').split(':')
        if len(lc) > 1:
            if lc[1].__contains__('('):
                lc = lc[1].split('(')
            else:
                lc.append('0')
                if lc[0].__contains__('('):
                    lc[0] = lc[0].split('(')[1]
                    lc[0] = lc[0].strip(') ')
        else:
            lc2 = list(lc)
            lc = list()
            lc.append(lc2[0].split('(')[1])
            lc.append('')

        if not lc[0] == lastline:
            lastline = lc[0]
            if errstr != '':
                errstr += '\n\n'
            if lc[1] != '':
                chrstr = ', char ' + lc[1]
            else:
                chrstr = ''
            cerr = 'Line {}{}: '.format(lc[0], chrstr)
        else:
            lastChar = lc[1]
            if errstr != '':
                errstr += '\n'
            if lastChar != lc[1]:
                cerr = 'char ' + lc[1] + ':'

        cerr += ct[2]
        if len(ct) > 3:
            cerr += ': ' + ct[3]
        errstr += cerr
        cerr = ''

    if errstr == '':
        errstr = cerr
    return errstr


class ShaderFile:
    def __init__(self, filepath):
        self.filePath = filepath
        self.lastmodTime = stat(self.filePath).st_mtime

    def isModified(self):
        vsres = stat(self.filePath)
        if vsres.st_mtime != self.lastmodTime:
            self.lastmodTime = vsres.st_mtime
            return True
        else:
            return False
