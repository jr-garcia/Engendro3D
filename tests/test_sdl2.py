import unittest
from ctypes import ArgumentError

from sdl2 import *


def getSDLError():
    sderr = SDL_GetError()
    try:
        sderr = sderr.decode()
    except Exception:
        pass
    return sderr


class SDLTester(unittest.TestCase):

    def setUp(self):
        if SDL_Init(SDL_INIT_EVERYTHING) != 0:
            self.fail(getSDLError())

    def test_set_attribs_buffer(self):
        SDL_GL_SetAttribute(SDL_GL_RED_SIZE, 8)
        SDL_GL_SetAttribute(SDL_GL_GREEN_SIZE, 8)
        SDL_GL_SetAttribute(SDL_GL_BLUE_SIZE, 8)
        SDL_GL_SetAttribute(SDL_GL_ALPHA_SIZE, 8)
        SDL_GL_SetAttribute(SDL_GL_BUFFER_SIZE, 24)

    def test_set_attribs_depth(self):
        for depth in [24, 16]:
            if SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, depth) == 0:
                break
            else:
                if depth == 16:
                    error = 'Error setting depth size: ' + getSDLError()
                    self.fail(error)

    def test_set_attribs_restrict_Context(self):
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 2)
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 1)

        # SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG)
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)
        errStr = getSDLError()
        if errStr != '':
            self.fail(errStr)

    def test_set_attribs_use_debug(self):
        res = SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_DEBUG_FLAG)
        if res != 0:
            error = 'Error setting SDL debug context flag: ' + getSDLError()
            self.fail(error)

    def test_set_attribs_share_context(self):
        if SDL_GL_SetAttribute(SDL_GL_SHARE_WITH_CURRENT_CONTEXT, 1) != 0:
            error = 'Error setting SDL shared context flag: ' + getSDLError()
            self.fail(error)

    def test_set_attribs_set_double_buffer(self):
        isDoubleBuffered = not SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1)
        if not isDoubleBuffered:
            self.fail('Error setting SDL double buffer flag: ' + getSDLError())

    def test_set_attribs_set_multisample(self):
        from warnings import warn
        warn('Multisample is not implemented')      

    def test_open_window(self):
        flags = SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE
        try:
            self._SDL_Window = SDL_CreateWindow('test window', 100, 100, 200, 200, flags)
        except ArgumentError:
            self._SDL_Window = SDL_CreateWindow(b'test window', 100, 100, 200, 200, flags)
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

        SDL_GL_MakeCurrent(self._SDL_Window, self._context)
