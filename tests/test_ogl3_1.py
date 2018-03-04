import unittest
from ctypes import ArgumentError
import os

import numpy as np
from sdl2 import *
from glaze.GL import *

BASEPATH = 'shots_results'


def getSDLError():
    sderr = SDL_GetError()
    try:
        sderr = sderr.decode()
    except Exception:
        pass
    return sderr


class OGL3Tester(unittest.TestCase):

    def setUp(self):
        self.addCleanup(self.close)
        if SDL_Init(SDL_INIT_EVERYTHING) != 0:
            self.fail(getSDLError())

    # set_attribs_buffer
        SDL_GL_SetAttribute(SDL_GL_RED_SIZE, 8)
        SDL_GL_SetAttribute(SDL_GL_GREEN_SIZE, 8)
        SDL_GL_SetAttribute(SDL_GL_BLUE_SIZE, 8)
        SDL_GL_SetAttribute(SDL_GL_ALPHA_SIZE, 8)
        SDL_GL_SetAttribute(SDL_GL_BUFFER_SIZE, 24)

    # set_attribs_depth
        for depth in [24, 16]:
            if SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, depth) == 0:
                break
            else:
                if depth == 16:
                    error = 'Error setting depth size: ' + getSDLError()
                    self.fail(error)

    # set_attribs_restrict_Context
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 2)
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 1)

    # SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG)
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)
        errStr = getSDLError()
        if errStr != '':
            self.fail(errStr)

    # set_attribs_use_debug
        res = SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_DEBUG_FLAG)
        if res != 0:
            error = 'Error setting SDL debug context flag: ' + getSDLError()
            self.fail(error)

    # set_attribs_share_context
        if SDL_GL_SetAttribute(SDL_GL_SHARE_WITH_CURRENT_CONTEXT, 1) != 0:
            error = 'Error setting SDL shared context flag: ' + getSDLError()
            self.fail(error)

    # set_attribs_set_double_buffer
        isDoubleBuffered = not SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1)
        if not isDoubleBuffered:
            self.fail('Error setting SDL double buffer flag: ' + getSDLError())

    # set_attribs_set_multisample
    #     from warnings import warn
    #     warn('Multisample is not implemented')

    # open_window
        self.size = w, h = 400, 400
        flags = SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE | SDL_WINDOW_HIDDEN
        try:
            self._SDL_Window = SDL_CreateWindow('test window', 200, 200, w, h, flags)
        except ArgumentError:
            self._SDL_Window = SDL_CreateWindow(b'test window', 200, 200, w, h, flags)
        except Exception as err:
            self.fail('error creating sdl window: ' + str(err))

        if not self._SDL_Window:
            sdlerr = SDL_GetError()
            msg = 'Error creating window {}'.format(sdlerr)
            self.fail(msg)

        self._context = newContext = SDL_GL_CreateContext(self._SDL_Window)
        if not newContext:
            sdlerr = getSDLError()
            error = 'Error creating context: ' + sdlerr
            self.fail(error)

        self.windowID = SDL_GetWindowID(self._SDL_Window)

        loadGL()

    def _pollEvents(self):
        event = SDL_Event()
        while SDL_PollEvent(event):
            pass
        
    def GLClear(self):
        glClearColor(.1, .3, .8, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

    def GLPresent(self):
        SDL_GL_SwapWindow(self._SDL_Window)
        self._pollEvents()

    def test_clear_screen(self):
        self.GLClear()
        self.GLPresent()
        self.compareScreenShot('clearScreen')

    def test_draw_triangle_color(self):
        self.GLClear()
        self.drawTriangle(True)
        self.GLPresent()
        self.compareScreenShot('drawColorTriangle')

    def drawTriangle(self, useShader):
        # An array of 3 vectors which represents 3 vertices
        g_vertex_buffer_data = np.array([-1.0, -1.0, 0.0, 1.0, -1.0, 0.0, 0.0, 1.0, 0.0], np.float32)
        # This will identify our vertex buffer
        vertexbuffer = np.array([0], np.uint32)
        # Generate 1 buffer, put the resulting identifier in vertexbuffer
        glGenBuffers(1, vertexbuffer)
        # The following commands will talk about our 'vertexbuffer' buffer
        glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer)
        # Give our vertices to OpenGL.
        glBufferData(GL_ARRAY_BUFFER, g_vertex_buffer_data.strides[0] * len(g_vertex_buffer_data),
                     # todo: replace with sizeof
                     g_vertex_buffer_data, GL_STATIC_DRAW)

        VertexArrayID = np.array([0], np.uint32)
        glGenVertexArrays(1, VertexArrayID)
        glBindVertexArray(VertexArrayID)
        if useShader:
            programID = LoadShaders()
            glUseProgram(programID)

        # Draw triangle...
        # 1rst attribute buffer : vertices
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer)
        glVertexAttribPointer(0,
                              3,  # size
                              GL_FLOAT,  # type
                              GL_FALSE,  # normalized?
                              0,  # stride
                              0)  # array buffer offset)
        # Draw the triangle !
        glDrawArrays(GL_TRIANGLES, 0, 3)  # Starting from vertex 0 3 vertices total -> 1 triangle
        glDisableVertexAttribArray(0)
        # end the current frame (internally swaps the front and back buffers)
        glDeleteBuffers(1, vertexbuffer)

    def compareScreenShot(self, testName):
        w, h = self.size

        dest = np.empty(w * h * 3, np.uint8)
        self.getBackBufferContent(w, h, dest)

        filePath = os.path.join(BASEPATH, testName + '.png')

        from PIL.Image import fromarray, merge, open
        from PIL.ImageOps import flip
        capture = fromarray(dest.reshape(h, w, 3))
        capture = flip(capture)
        b, g, r = capture.split()
        capture = merge("RGB", (r, g, b))
        if not os.path.exists(filePath):
            capture.save(filePath)
        else:
            stored = open(filePath)
            isEqual = np.all(np.asarray(capture) == np.asarray(stored))
            self.assertTrue(isEqual)

    def getBackBufferContent(self, w, h, destBuffer):
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        glReadPixels(0, 0, w, h, GL_BGR, GL_UNSIGNED_BYTE, destBuffer)

    def close(self):
        SDL_GL_DeleteContext(self._context)
        SDL_DestroyWindow(self._SDL_Window)


def LoadShaders():
        # Create the shaders
        VertexShaderID = glCreateShader(GL_VERTEX_SHADER)
        FragmentShaderID = glCreateShader(GL_FRAGMENT_SHADER)

        # Vertex Shader code
        VertexShaderCode = '''#version 120
        varying vec3 pos;
        attribute vec3 position;
    void main(){
    pos = position;
    gl_Position.xyz = position;
      gl_Position.w = 1.0;
    }
    '''
        # Fragment Shader code
        FragmentShaderCode = '''#version 120
    varying vec3 pos;
    void main(){
      gl_FragColor = vec4(vec3(pos + 0.25), 1);
    }
    '''
        result = np.array([GL_FALSE], np.int32)
        InfoLogLength = np.array([0], np.int32)

        # Compile Vertex Shader
        VertexSourcePointer = stringToArray(VertexShaderCode)
        glShaderSource(VertexShaderID, 1, VertexSourcePointer, None)
        glCompileShader(VertexShaderID)

        # Check Vertex Shader
        glGetShaderiv(VertexShaderID, GL_COMPILE_STATUS, result)
        if result[0] == GL_FALSE:
            glGetShaderiv(VertexShaderID, GL_INFO_LOG_LENGTH, InfoLogLength)
            VertexShaderErrorMessage = np.empty((InfoLogLength[0],), np.int8)
            glGetShaderInfoLog(VertexShaderID, InfoLogLength, None, VertexShaderErrorMessage)
            raise RuntimeError('Compiling vertex shader: ' + arrayToString(VertexShaderErrorMessage))

        # Compile Fragment Shader
        FragmentSourcePointer = stringToArray(FragmentShaderCode)
        glShaderSource(FragmentShaderID, 1, FragmentSourcePointer, None)
        glCompileShader(FragmentShaderID)

        # Check Fragment Shader
        glGetShaderiv(FragmentShaderID, GL_COMPILE_STATUS, result)
        if result[0] == GL_FALSE:
            glGetShaderiv(FragmentShaderID, GL_INFO_LOG_LENGTH, InfoLogLength)
            FragmentShaderErrorMessage = np.empty((InfoLogLength[0],), np.int8)
            glGetShaderInfoLog(FragmentShaderID, InfoLogLength, None, FragmentShaderErrorMessage)
            raise RuntimeError('Compiling fragment shader: ' + arrayToString(FragmentShaderErrorMessage))

        # Link the program
        ProgramID = glCreateProgram()
        glAttachShader(ProgramID, VertexShaderID)
        glAttachShader(ProgramID, FragmentShaderID)
        glLinkProgram(ProgramID)

        # Check the program
        glGetProgramiv(ProgramID, GL_LINK_STATUS, result)
        if result[0] == GL_FALSE:
            glGetProgramiv(ProgramID, GL_INFO_LOG_LENGTH, InfoLogLength)
            ProgramErrorMessage = np.empty((InfoLogLength[0],), np.int8)
            glGetProgramInfoLog(ProgramID, InfoLogLength, None, ProgramErrorMessage)
            RuntimeError('Linking program: ' + arrayToString(ProgramErrorMessage))

        glDetachShader(ProgramID, VertexShaderID)
        glDetachShader(ProgramID, FragmentShaderID)

        glDeleteShader(VertexShaderID)
        glDeleteShader(FragmentShaderID)

        return ProgramID


def stringToArray(string):
    return [string]


def arrayToString(array):
    strList = [0] * len(array)
    for i in range(len(array)):
        strList[i] = chr(array[i])
    return ''.join(strList)
