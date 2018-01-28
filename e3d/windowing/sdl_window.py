from __future__ import print_function
import ctypes as ct
import os
from sdl2 import *

from . import Window_Base
from ..Logging import logLevelsEnum


class Window(Window_Base):
    """
    Class for starting an SDL2 based Engendro3D Window.

    """

    def _createInternalWindow(self, title, engine, fullscreen):
        flags = SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE
        if fullscreen:
            flags = flags | SDL_WINDOW_FULLSCREEN

        try:
            title = title.encode()
        except Exception:
            pass
        self._SDL_Window = SDL_CreateWindow(title, 0, 0, self._size[0], self._size[1], flags)
        if not self._SDL_Window:
            sdlerr = SDL_GetError()
            msg = u'Error creating window for \'{}\': {}'.format(self.gameName, sdlerr)
            self._engine.log(msg, log)
            raise Exception(msg)
        _, self._context = engine._getNewContext(self._SDL_Window)

        SDL_GL_MakeCurrent(self._SDL_Window, self._context)

    @property
    def windowID(self):
        return SDL_GetWindowID(self._SDL_Window)

    def setFullScreen(self, setfull):
        if setfull:
            f = SDL_WINDOW_FULLSCREEN
        else:
            f = 0
        # todo: resize if size != fullscreensize

        SDL_SetWindowFullscreen(self._SDL_Window, f)
        self._isFull = setfull

    def _getMouseMode(self):
        return SDL_GetRelativeMouseMode()

    def _setMouseMode(self, value):
        # todo: move cursor to window center before changing this
        SDL_SetRelativeMouseMode(value)

    mouseLock = property(_getMouseMode, _setMouseMode)

    @property
    def gamma(self):
        return SDL_GetWindowBrightness(self._SDL_Window)

    @gamma.setter
    def gamma(self, value):
        """
        Set int value for this window's gamma.
        @type vakue: int
        # SDL_SetWindowBrightness
        """
        if (not isinstance(value, int) and not isinstance(value, float)) or value <= 0:
            raise ValueError('Gamma value must be a float > 0.')
        if SDL_SetWindowBrightness(self._SDL_Window, value) != 0:
            raise Exception('Error setting Gamma: ' + SDL_GetError())

    @property
    def size(self):
        w = ct.pointer(ct.c_int(0))
        h = ct.pointer(ct.c_int(0))
        SDL_GetWindowSize(self._SDL_Window, w, h)

        return w.contents.value, h.contents.value

    @size.setter
    def size(self, val):
        self._previousSize = self.size
        w, h = val
        if not self._isFull:
            SDL_SetWindowSize(self._SDL_Window, ct.c_int(w), ct.c_int(h))
        else:
            SDL_SetWindowDisplayMode(_SDL_Window, SDL_DisplayMode(w, h))
            self._fullscreenSize = (w, h)
        self._sizeChanged(w, h)

    @property
    def title(self):
        """

        @rtype : str
        """
        t = SDL_GetWindowTitle(self._SDL_Window)
        return t

    @title.setter
    def title(self, value):
        """

        @type value: str
        """
        try:
            value = value.encode()
        except Exception:
            pass
        SDL_SetWindowTitle(self._SDL_Window, value)

    @property
    def vsynch(self):
        ret = SDL_GL_GetSwapInterval()
        if ret != 0:
            return True
        else:
            return False

    @vsynch.setter
    def vsynch(self, val):
        if bool(val):
            if SDL_GL_SetSwapInterval(-1) == -1:
                SDL_GL_SetSwapInterval(1)
        else:
            SDL_GL_SetSwapInterval(0)

    def setIcon(self, path):
        aPath = os.path.abspath(path)
        if not os.path.exists(aPath):
            self._engine.log('Window.setIcon error: File {} not found. Skipping.'.format(aPath))
            return
        try:
            from PIL import Image
            im = Image.open(aPath)
            w, h = im.size[0], im.size[1]
            if im.mode == 'RGB':
                alphamask = 0
                depth = 24
            else:
                alphamask = 0xFF000000
                depth = 32
            try:
                pix = im.tobytes()
                im.close()
            except Exception:
                raise

            surface = SDL_CreateRGBSurfaceFrom(pix, w, h, depth, w * 4, 0x000000FF, 0x0000FF00, 0x00FF0000, alphamask)
            SDL_SetWindowIcon(self._SDL_Window, surface)
            SDL_FreeSurface(surface)

        except Exception as ex:
            self._engine.log('Window.setIcon error: ' + str(ex), logLevelsEnum.debug)
            raise

    def getMultiSampleNumber(self):
        # res = ct.pointer(ct.c_long(0))
        # if not SDL_GL_GetAttribute(SDL_GL_MULTISAMPLESAMPLES, res):
        #     return res.contents.value
        # else:
        #     return 0
        print('Not implemented.')
        return -1

    def _pollEvents(self):
        event = SDL_Event()
        while SDL_PollEvent(event):
            if event.type == SDL_QUIT:
                self.close()
            elif event.type == SDL_WINDOWEVENT:
                winev = event.window.event
                evWinId = event.window.windowID
                if evWinId == self.windowID:
                    if winev == SDL_WINDOWEVENT_RESIZED:
                        self._sizeChanged(event.window.data1, event.window.data2)
                    if winev == SDL_WINDOWEVENT_CLOSE:
                        self.close()
            self.events._announce(event)

    def _makeContextCurrent(self):
        SDL_GL_MakeCurrent(self._SDL_Window, self._context)

    def _performSwap(self):
        SDL_GL_SwapWindow(self._SDL_Window)

    def close(self):
        SDL_GL_DeleteContext(self._context)
        SDL_DestroyWindow(self._SDL_Window)
        Window_Base.close(self)

    def getCurrentDPIs(self):
        h = ct.pointer(ct.c_float(0))
        v = ct.pointer(ct.c_float(0))
        d = ct.pointer(ct.c_float(0))
        SDL_GetDisplayDPI(0, d, h, v)  # fixme: should consider real monitor index
        return int(h.contents.value), int(v.contents.value)

    def saveScreenShot(self, filePath=''):
        def slugify(value):
            """
            Based on https://github.com/django/django/blob/master/django/utils/text.py#L413

            Copyright (c) Django Software Foundation and individual contributors.
            All rights reserved.

            Redistribution and use in source and binary forms, with or without modification,
            are permitted provided that the following conditions are met:

                1. Redistributions of source code must retain the above copyright notice,
                   this list of conditions and the following disclaimer.

                2. Redistributions in binary form must reproduce the above copyright
                   notice, this list of conditions and the following disclaimer in the
                   documentation and/or other materials provided with the distribution.

                3. Neither the name of Django nor the names of its contributors may be used
                   to endorse or promote products derived from this software without
                   specific prior written permission.

            THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
            ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
            WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
            DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
            ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
            (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
            LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
            ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
            (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
            SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
            """
            import unicodedata, re
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
            value = re.sub(r'[^\w\s-]', '', value).strip().lower()

            return value

        w, h = self.size

        import numpy as np
        dest = np.empty(w * h * 3, np.uint8)
        self.backend.getBackBufferContent(w, h, dest)
        # Now the file creation
        if filePath == '':
            from datetime import datetime
            ind = 0
            basePath = os.path.abspath(os.curdir)
            now = datetime.now()
            date = str(datetime.date(now))
            timeNow = datetime.time(now)
            time = '{}-{}-{}'.format(timeNow.hour, timeNow.minute, timeNow.second)
            baseName = slugify(self.gameName) + '_' + date + '_' + time
            filePath = os.path.join(basePath, baseName)
            filePath = filePath + '.png'
            while os.path.exists(filePath):
                filePath = os.path.join(basePath, baseName + str(ind))
                filePath = filePath + '.png'
                ind += 1

        from PIL.Image import fromarray, merge
        from PIL.ImageOps import flip
        image = fromarray(dest.reshape(h, w, 3))
        image = flip(image)
        b, g, r = image.split()
        image = merge("RGB", (r, g, b))
        image.save(filePath)
