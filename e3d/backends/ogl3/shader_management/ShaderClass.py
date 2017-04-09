import numpy as np
from glaze.GL import *

from ...base_backend import ShaderStruct
from .ShaderParametersHelper import getActiveUniforms, getActiveAttribs
from ....LoggerClass import logger, logLevelsEnum


class Shader:
    def _getisSet(self):
        return self._isSet

    isSet = property(_getisSet)

    def _getID(self):
        return self._iID

    ID = property(fget=_getID)

    def _fill_unitsCache(self):
        from glaze import GL
        uc = [getattr(GL, 'GL_TEXTURE{}'.format(unit)) for unit in range(0, self._maxTextureUnits)]
        for i in range(len(uc)):
            self._unitsCache.append(uc[i])

    def __init__(self, GLSL_program, ID, shadersManager):
        """
        Handy class to manipulate glsl program's uniform values.


        @rtype : Shader
        @type ID: str
        @type shadersManager: shadersManager
        @type GLSL_program: int
        """
        self._maxBones = 50
        self._maxTextureUnits = shadersManager._maxTextureUnits
        self._program = GLSL_program
        self._iID = ID
        self._attributesHandlesCache = {}
        self._uniformsHandlesCache = {}
        self._textureLastValues = {}
        self._textureUnitsUsed = -1
        self._lastActiveUnit = -1
        self._isSet = False
        self._sman = shadersManager
        self._unitsCache = []
        self._reportInactive = False
        self._fill_unitsCache()
        self._uniformLastValueV = {}
        self._uniformLastValueF = {}
        self._uniformLastValueI = {}

        uniforms = getActiveUniforms(GLSL_program)
        for ulocation, utype, uname in uniforms:
            self._uniformsHandlesCache[uname] = ulocation

        attribs = getActiveAttribs(GLSL_program)
        for alocation, atype, aname in attribs:
            self._attributesHandlesCache[aname] = alocation

        self._activeUniforms = uniforms

    def getActiveUniforms(self):
        return self._activeUniforms

    def __repr__(self):
        return self._iID

    def __int__(self):
        return self._program

    def isUniformUsed(self, paramName):
        return paramName in self._uniformsHandlesCache.keys()

    @staticmethod
    def compareVectors(a, b):
        if len(a) != len(b):
            return False
        else:
            return a == b
            # for i in range(len(a)):
            #     if a[i] != b[i]:
            #         return False
            # return True

    def isSame(self, handle, newValue):
        isequal = False
        if hasattr(newValue, '__getitem__'):
            oldV = self._uniformLastValueV.get(handle)
            if oldV is None:
                self._uniformLastValueV[handle] = newValue
            else:
                isequal = Shader.compareVectors(oldV, newValue)
                if not isequal:
                    self._uniformLastValueV[handle] = newValue
        elif isinstance(newValue, float):
            oldF = self._uniformLastValueF.get(handle)
            if oldF is None:
                self._uniformLastValueF[handle] = newValue
            else:
                oldF = self._uniformLastValueF[handle]
                isequal = (oldF == newValue)
                if not isequal:
                    self._uniformLastValueF[handle] = newValue
        elif isinstance(newValue, int):
            oldI = self._uniformLastValueI.get(handle)
            if oldI is None:
                self._uniformLastValueI[handle] = newValue
            else:
                oldI = self._uniformLastValueI[handle]
                isequal = (oldI == newValue)
                if not isequal:
                    self._uniformLastValueI[handle] = newValue
        return isequal

    def setUniformValue(self, paramName, paramValue):
        paramHandle = self._uniformsHandlesCache.get(paramName, -1)
        if paramHandle == -1:
            if self._reportInactive:
                print('Parameter \'{}\' not active or not defined in shader \'{}\'.'.format(paramName, self._iID))
            return
        if paramValue is None:
            print('{} value is \'None\'. Ignored for shader \'{}\'.'.format(paramName, self._iID))
            return
        try:
            if not self.isSame(paramHandle, paramValue):
                if isinstance(paramValue, int):
                    intval = int(paramValue)
                    glUniform1i(paramHandle, intval)
                elif isinstance(paramValue, float):
                    floatval = float(paramValue)
                    glUniform1f(paramHandle, floatval)
                else:
                    arrType = type(paramValue[0])
                    if arrType == float or 'vec' in str(arrType):
                        vecVal = np.asarray(paramValue, np.float32)
                    elif arrType in [int, bool]:
                        vecVal = np.asarray(paramValue, np.int32)
                    else:
                        raise TypeError('array type {} not supported.'.format(arrType))
                    if 'mat4' in str(type(paramValue)):
                        glUniformMatrix4fv(paramHandle, 1, 0, vecVal.reshape((-1)))
                    elif 'mat3' in str(type(paramValue)):
                        glUniformMatrix3fv(paramHandle, 1, 0, vecVal.reshape((-1)))
                    else:
                        veclen = len(vecVal)
                        if veclen == 3:
                            glUniform3fv(paramHandle, 1, vecVal)
                        elif veclen == 4:
                            glUniform4fv(paramHandle, 1, vecVal)
                        else:
                            if vecVal.dtype == np.int32:
                                glUniform1iv(paramHandle, veclen, vecVal)
                            else:
                                glUniform1fv(paramHandle, veclen, vecVal)
        except Exception as ex:
            logger.log('Error: ' + ex.args[0] +
                       ' -> shader ID={} param:{} value:{}'.format(self._iID, paramName, str(type(paramValue))),
                        logLevelsEnum.error)
            raise

    def setMultipleValues(self, paramHandle, paramValuesArray):
        print('setmulti in ')
        if paramValuesArray is not None and (paramHandle != -1):
            try:
                if len(paramValuesArray[0]) == 16:
                    setValueMat4x4LMulti(paramHandle, paramValuesArray)
                else:
                    if not isinstance(paramValue, list):
                        val = list(paramValue)
                    else:
                        val = paramValue
                    if len(val) == 3:
                        setValueVec3L(paramHandle, val)
                    else:
                        setValueVec4L(paramHandle, val)
            except Exception as ex:
                logger.log('EffectClass "SeMultipletValues" error: ' + ex.message)
        print('setmulti out')

    def _getUniformHandle(self, paramName):
        """


        @rtype : int
        @type paramName: str
        """
        return self._uniformsHandlesCache.get(paramName)

    def getUniformValue(self, eh):
        raise NotImplementedError('Retrieving a value from the shader is not implemented. Please report it.')

    def setUniformsList(self, paramsListTupples):
        paramsLen = len(paramsListTupples)
        for i in range(paramsLen):
            name, value = paramsListTupples[i]
            # value = paramsListTupples[i][1]
            self.setUniformValue(name, value)

    def setTexture(self, samplerName, value):
        if value is None or value < 1:
            raise ValueError('Wrong value for texture')
        if self._textureUnitsUsed <= self._maxTextureUnits:
            handle = self._uniformsHandlesCache.get(samplerName, -1)
            if handle > -1:
                lastValue = self._textureLastValues.get(handle)
                if lastValue is not None and lastValue == value:
                    return
                self._textureUnitsUsed += 1
                unit = self._textureUnitsUsed
                if unit != self._lastActiveUnit:
                    glActiveTexture(self._unitsCache[unit])
                    self._lastActiveUnit = unit
                # with nogil:
                glBindTexture(GL_TEXTURE_2D, value)
                glUniform1i(handle, unit)
                self._textureLastValues[handle] = value
        else:
            logger.log('Error: Max fragment textures units reached ({0})'.format(str(self._maxTextureUnits)),
                       logLevelsEnum.warning)

    def setStruct(self, structParamName, struct):
        """


        @type structParamName: str
        @type struct: ShaderStruct
        """
        for it in struct.items():
            name, val = it
            paramName = structParamName + '.' + name
            if isinstance(val, list):
                print('setStruct list', paramName)
                # handle = self._uniformsHandlesCache.get(paramName, -1)
                # if handle >= 0:
                #     self.setMultipleValues(handle, val)
            elif isinstance(val, ShaderStruct):
                self.setStruct(paramName, val)
            else:
                self.setUniformValue(paramName, val)

    def reset(self):
        self._textureLastValues.clear()
        self._textureUnitsUsed = -1
        self._lastActiveUnit = -1

    def set(self):
        self._sman._setShaderState(self, 1)

    def unSet(self):
        self._sman._setShaderState(self, 0)

    def buildBoneTransf(self, bonetrans, boneDir):
        bth = self._uniformsHandlesCache['BoneTransforms[0]']
        btith = self._uniformsHandlesCache.get('BoneTransformsIT[0]')
        for b in bonetrans.items():
            boneTransHandle = bth + boneDir[b[0]]
            vecVal = b[1].toList()
            glUniformMatrix4fv(boneTransHandle, 1, 0, vecVal)
            if btith:
                boneTransITHandle = btith + boneDir[b[0]]
                vecVal = b[1].transpose().inverse().toList()
                glUniformMatrix4fv(boneTransITHandle, 1, 0, vecVal)

    def buildBoneTransfMulti(self, bonetrans, boneDir):
        boneTransHandle = self._uniformsHandlesCache['BoneTransforms[0]']
        boneTransITHandle = self._uniformsHandlesCache.get('BoneTransformsIT[0]', -1)
        buildBoneTransfC(bonetrans, boneDir, boneTransHandle, boneTransITHandle, self._tempBoneArray,
                         self._tempBoneITArray)
        # for b in bonetrans.iteritems():
        # self._tempBoneArray[boneDir[b[0]]] = b[1].toList()
        #     self._tempBoneITArray[boneDir[b[0]]] = b[1].transpose().inverse().toList()
        # self.setMultipleValues(boneTransHandle, self._tempBoneArray)
        # self.setMultipleValues(boneTransITHandle, self._tempBoneITArray)

    def terminate(self):
        try:
            if glDeleteProgram:
                glDeleteProgram(self._program)
        except:
            pass
