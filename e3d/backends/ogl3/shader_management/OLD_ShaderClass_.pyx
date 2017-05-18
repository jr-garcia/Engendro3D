from libcpp.vector cimport vector
import cython
from OpenGL.GL import *

from ...base_backend import ShaderStruct
# import numpy as np
# cimport numpy as np

from .ShaderParametersHelper import getActiveUniforms, getActiveAttribs
from glaze.cGL cimport glUniformMatrix4fv, glUniformMatrix3fv, glUniform3fv, glUniform4fv, glUniform1i, \
                             glUniform1f, glUniform1i, glBindTexture, GL_TEXTURE_2D, gladLoadGL

IF UNAME_SYSNAME == u"Windows":
    from cross_unordered_map.unordered_mapW cimport unordered_map
ELIF UNAME_SYSNAME == u"Darwin":
    from libcpp.unordered_map cimport unordered_map
ELIF UNAME_SYSNAME == u"Linux":
    from libcpp.unordered_map cimport unordered_map

# <<<<<<<<<<<<<<<<<<

ctypedef fused shader_value:
    int
    long
    float
    vector[float]

ctypedef fused anyInt:
    int
    long


cdef class Shader:
    cdef int _maxBones
    cdef int _maxTextureUnits
    cdef readonly int _program
    cdef str _iID
    cdef vector[int] _unitsCache
    cdef readonly dict _attributesHandlesCache
    cdef dict _uniformsHandlesCache
    cdef unordered_map _uniformLastValueI[int, int]
    cdef unordered_map _uniformLastValueF[int, float]
    cdef unordered_map _uniformLastValueV[int, vector[float]]
    cdef int _textureUnitsUsed
    cdef int _lastActiveUnit
    cdef public bint _isSet
    cdef object _sman
    cdef dict _textureLastValues
    cdef public bint _reportInactive

    # cdef tempArr = arr
    
    def _getisSet(self):
        return self._isSet
    isSet = property(_getisSet)

    def _getID(self):
        return self._iID
    ID = property(fget=_getID)

    cdef void _fill_unitsCache(self):
        cdef list uc = [getattr(OpenGL.GL, 'GL_TEXTURE{}'.format(unit)) for unit
                        in range(0, self._maxTextureUnits)]
        cdef int i = 0
        for i in range(len(uc)):
            self._unitsCache.push_back(uc[i])

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
        # self.tempArr = arr

        if not gladLoadGL():
            raise RuntimeError('Glad failed to initialize')
        self._reportInactive = False
        self._fill_unitsCache()

        uniforms = getActiveUniforms(GLSL_program)
        for u in uniforms:
            self._uniformsHandlesCache[u[2]] = u[0]

        attribs = getActiveAttribs(GLSL_program)
        for a in attribs:
            self._attributesHandlesCache[a[2]] = a[0]

    def __repr__(self):
        return self._iID

    def isUniformUsed(self, paramName):
        return paramName in self._uniformsHandlesCache.keys()

    @staticmethod
    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    cdef bint compareVectors(vector[float] a, vector[float] b) nogil:
        cdef int i
        if a.size() != b.size():
            return False
        else:
            for i in xrange(a.size()):
                if a[i] != b[i]:
                    return False
            return True

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    cdef bint isSame(self, int handle, shader_value newValue) nogil except *:
        cdef vector[float] oldV
        cdef float oldF
        cdef int oldI
        cdef unordered_map[int, vector[float]].iterator itV
        cdef unordered_map[int, float].iterator itF
        cdef unordered_map[int, int].iterator itI
        cdef bint isequal = False
        if shader_value is vector[float]:
            itV = self._uniformLastValueV.find(handle)
            if itV == self._uniformLastValueV.end():
                self._uniformLastValueV[handle] = newValue
            else:
                oldV = self._uniformLastValueV[handle]
                isequal = Shader.compareVectors(oldV, newValue)
                if not isequal:
                    self._uniformLastValueV[handle] = newValue
        elif shader_value is float:
            itF = self._uniformLastValueF.find(handle)
            if itF == self._uniformLastValueF.end():
                self._uniformLastValueF[handle] = newValue
            else:
                oldF = self._uniformLastValueF[handle]
                isequal = (oldF == newValue)
                if not isequal:
                    self._uniformLastValueF[handle] = newValue
        elif shader_value in anyInt:
            itI = self._uniformLastValueI.find(handle)
            if itI == self._uniformLastValueI.end():
                self._uniformLastValueI[handle] = newValue
            else:
                oldI = self._uniformLastValueI[handle]
                isequal = (oldI == newValue)
                if not isequal:
                    self._uniformLastValueI[handle] = newValue
        return isequal

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    cpdef void setUniformValue(self, str paramName, object paramValue):
        cdef vector[float] vecVal
        cdef int n = 1
        cdef int intval, vecLen
        cdef float floatval
        cdef int paramHandle = self._uniformsHandlesCache.get(paramName, -1)
        if paramHandle == -1:
            if self._reportInactive:
                print('Parameter \'{}\' not active or undefined in shader \'{}\'.'.format(
                      paramName, self._iID))
            return
        if paramValue is None:
            print('{} value is \'None\'. Ignored for shader \'{}\'.'.format(paramName, self._iID))
            return
        try:
            if isinstance(paramValue, int) or isinstance(paramValue, long):
                intval = paramValue
                with nogil:
                    if not self.isSame(paramHandle, intval):
                        glUniform1i(paramHandle, intval)
            elif isinstance(paramValue, float):
                floatval = paramValue
                with nogil:
                    if not self.isSame(paramHandle, floatval):
                        glUniform1f(paramHandle, floatval)
            elif 'mat4' in str(type(paramValue)):
                vecVal = paramValue.toList()
                with nogil:
                    if not self.isSame(paramHandle, vecVal):
                        glUniformMatrix4fv(paramHandle, n, 0, &vecVal[0])
            elif 'mat3' in str(type(paramValue)):
                vecVal = paramValue.toList()
                with nogil:
                    if not self.isSame(paramHandle, vecVal):
                        glUniformMatrix3fv(paramHandle, n, 0, &vecVal[0])
            else:
                vecVal = list(paramValue)
                vecLen = vecVal.size()
                with nogil:
                    if not self.isSame(paramHandle, vecVal):
                        if vecLen == 3:
                            glUniform3fv(paramHandle, n, &vecVal[0])
                        else:
                            glUniform4fv(paramHandle, n, &vecVal[0])
        except Exception, ex:
            raise RuntimeError('SetUniformValue error in shader '
                               '\'{}\': {}|{}|{}.'.format(self._iID,
                                                                   paramName,
                                                                   str(type(paramValue)),
                                                                   ex.message))

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
            except Exception, ex:
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

    def setUniformsList(Shader self, list paramsListTupples):
        cdef int i = 0
        cdef str name
        cdef object value
        cdef int paramsLen = len(paramsListTupples)
        for i in range(paramsLen):
            name = paramsListTupples[i][0]
            value = paramsListTupples[i][1]
            self.setUniformValue(name, value)

    def setTexture(self, str samplerName, int value):
        cdef long handle
        cdef int unit
        if value is None or value < 1:
            raise ValueError('Wrong value for texture')
        if self._textureUnitsUsed <= self._maxTextureUnits:
            handle = self._uniformsHandlesCache.get(samplerName, -1)
            if handle > -1:
                if self._textureLastValues.get(handle) == value:
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
        self._sman._setCurrentShaderState(self, 1)

    def unSet(self):
        self._sman._setCurrentShaderState(self, 0)

    def buildBoneTransf(self, dict bonetrans, dict boneDict):
        cdef vector[float] vecVal
        cdef int boneTransHandle
        cdef int boneTransITHandle
        cdef tuple b
        cdef int bth = self._uniformsHandlesCache['BoneTransforms[0]']
        cdef int btith = self._uniformsHandlesCache.get('BoneTransformsIT[0]')
        for b in bonetrans.iteritems():
            boneTransHandle = bth + boneDict[b[0]]
            vecVal = b[1].toList()
            with nogil:
                glUniformMatrix4fv(boneTransHandle, 1, 0, &vecVal[0])
            if btith:
                boneTransITHandle = btith + boneDict[b[0]]
                vecVal = b[1].transposed().inversed().toList()
                with nogil:
                    glUniformMatrix4fv(boneTransITHandle, 1, 0, &vecVal[0])

    def buildBoneTransfMulti(self, bonetrans, boneDict):
        boneTransHandle = self._uniformsHandlesCache['BoneTransforms[0]']
        boneTransITHandle = self._uniformsHandlesCache.get('BoneTransformsIT[0]', -1)
        buildBoneTransfC(bonetrans, boneDict, boneTransHandle, boneTransITHandle, self._tempBoneArray,
                         self._tempBoneITArray)
        # for b in bonetrans.iteritems():
        # self._tempBoneArray[boneDict[b[0]]] = b[1].toList()
        #     self._tempBoneITArray[boneDict[b[0]]] = b[1].transposed().inversed().toList()
        # self.setMultipleValues(boneTransHandle, self._tempBoneArray)
        # self.setMultipleValues(boneTransITHandle, self._tempBoneITArray)

    def terminate(self):
        try:
            if glDeleteProgram:
                glDeleteProgram(self._program)
        except:
            pass