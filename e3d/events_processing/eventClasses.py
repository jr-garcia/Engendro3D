from sdl2.events import *
from sdl2 import SDL_WINDOWEVENT_SIZE_CHANGED, SDL_WINDOWEVENT_CLOSE, SDL_WINDOWEVENT_FOCUS_GAINED, \
    SDL_WINDOWEVENT_FOCUS_LOST, SDL_WINDOWEVENT_EXPOSED, SDL_WINDOWEVENT_ENTER, SDL_WINDOWEVENT_HIDDEN, \
    SDL_WINDOWEVENT_LEAVE, SDL_WINDOWEVENT_MOVED, SDL_WINDOWEVENT_MAXIMIZED, SDL_WINDOWEVENT_MINIMIZED, \
    SDL_WINDOWEVENT_SHOWN, SDL_WINDOWEVENT_RESTORED, SDL_WINDOWEVENT_RESIZED
from sdl2.mouse import *
from sdl2.keyboard import *

# Note: some Touchpads may disable while keys are pressed.
# Is fixed by setting 'Palmcheck','Palm sensitivity' to off.

from copy import deepcopy


class EventTypes(object):
    Mouse = 'Mouse'
    Key = 'Key'
    Window = 'Window'
    User = 'User'
    Finger = 'Finger'
    Custom = 'Custom'
    Text = 'Text'

    def __init__(self):
        pass


class Event(object):
    def __init__(self, etype):
        """

        @etype etype: Event
        """
        self._type = etype
        self.discarded = False
        self.eventName = ''

    def __repr__(self):
        return '{} event: {}'.format(self._type, self.eventName)

    def _copy(self):
        return deepcopy(self)


class windowEventNames(object):
    close = 'close'
    resized = 'resized'
    focusGained = 'focusGained'
    focusLost = 'focusLost'
    maximized = 'maximized'
    minimized = 'minimized'
    exposed = 'exposed'
    shown = 'shown'
    hidden = 'hidden'
    enter = 'enter'
    leave = 'leave'
    restored = 'restored'
    moved = 'moved'

    def __init__(self):
        pass


class WindowEvent(Event):
    def __init__(self, event):
        """

        @rtype : WindowEvent
        """
        super(WindowEvent, self).__init__(EventTypes.Window)
        self._code = event.event
        self.windowID = event.windowID
        code = self._code
        if code == SDL_WINDOWEVENT_CLOSE:
            self.eventName = windowEventNames.close
        elif code == SDL_WINDOWEVENT_FOCUS_GAINED:
            self.eventName = windowEventNames.focusGained
        elif code == SDL_WINDOWEVENT_FOCUS_LOST:
            self.eventName = windowEventNames.focusLost
        elif code == SDL_WINDOWEVENT_EXPOSED:
            self.eventName = windowEventNames.exposed
        elif code == SDL_WINDOWEVENT_ENTER:
            self.eventName = windowEventNames.enter
        elif code == SDL_WINDOWEVENT_HIDDEN:
            self.eventName = windowEventNames.hidden
        elif code == SDL_WINDOWEVENT_LEAVE:
            self.eventName = windowEventNames.leave
        elif code == SDL_WINDOWEVENT_MOVED:
            self.eventName = windowEventNames.moved
            self.x = event.data1
            self.y = event.data2
        elif code == SDL_WINDOWEVENT_MAXIMIZED:
            self.eventName = windowEventNames.maximized
        elif code == SDL_WINDOWEVENT_MINIMIZED:
            self.eventName = windowEventNames.minimized
        elif code == SDL_WINDOWEVENT_SHOWN:
            self.eventName = windowEventNames.shown
        elif code == SDL_WINDOWEVENT_RESTORED:
            self.eventName = windowEventNames.restored
        elif code == SDL_WINDOWEVENT_RESIZED:
            self.eventName = windowEventNames.resized
            self.w = event.data1
            self.h = event.data2
        else:
            self.eventName = 'Unhandled window event type: ' + str(code)


class KeyEventNames(object):
    keyDown = 'keyDown'
    keyUp = 'keyUp'


class KeyEvent(Event):
    def __init__(self, event, etype):
        super(KeyEvent, self).__init__(EventTypes.Key)
        self.keyCode = event.keysym.sym
        # self.keyScanCode = SDL_GetScancodeFromKey(event.keysym.sym)
        self.keyName = SDL_GetKeyName(event.keysym.sym).lower()
        if type(self.keyName) is bytes:
            self.keyName = self.keyName.decode()
        if etype == SDL_KEYDOWN:
            self.eventName = KeyEventNames.keyDown
        else:
            self.eventName = KeyEventNames.keyUp

    def __repr__(self):
        return super(KeyEvent, self).__repr__() + '({}), name= {}, code= {}'.format(self.eventName, self.keyName,
                                                                                    self.keyCode)


class MouseEventNames(object):
    buttonDown = 'buttonDown'
    buttonUp = 'buttonUp'
    motion = 'motion'
    wheel = 'wheel'
    click = 'click'
    doubleClick = 'doubleClick'
    enter = 'enter'
    leave = 'leave'


class MouseEvent(Event):
    def __init__(self, event):
        self._buttons = {SDL_BUTTON_MIDDLE: 'middle', SDL_BUTTON_RIGHT: 'right', SDL_BUTTON_LEFT: 'left', 0: 'unknown0',
                         SDL_BUTTON_X1: 'x1', SDL_BUTTON_X2: 'x2', SDL_BUTTON_X1MASK: 'x1Mask',
                         SDL_BUTTON_X2MASK: 'x2Mask', 6: 'unknown6', 7: 'unknown7'}
        super(MouseEvent, self).__init__(EventTypes.Mouse)
        self._code = event.type
        self.x = None
        self.y = None
        self.xRel = None
        self.yRel = None
        self.button = None
        self.direction = None
        code = self._code
        if code in [SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP]:
            specEvent = event.button
            self.button = self._buttons[specEvent.button]
            self.x = specEvent.x
            self.y = specEvent.y
            self._clicks = specEvent.clicks
            if code == SDL_MOUSEBUTTONDOWN:
                self.eventName = MouseEventNames.buttonDown
            else:
                self.eventName = MouseEventNames.buttonUp
        elif code == SDL_MOUSEMOTION:
            specEvent = event.motion
            self.x = specEvent.x
            self.y = specEvent.y
            if self.xRel is None and (specEvent.xrel == specEvent.x or specEvent.yrel == specEvent.y):
                self.xRel = 0
                self.yRel = 0
            else:
                self.xRel = specEvent.xrel
                self.yRel = specEvent.yrel
            self.eventName = MouseEventNames.motion
        elif code == SDL_MOUSEWHEEL:
            specEvent = event.wheel
            self.x = specEvent.x
            self.y = specEvent.y
            self.direction = specEvent.direction
            self.eventName = MouseEventNames.wheel
        else:
            self.eventName = 'Unhandled mouse event type: ' + str(code)
            return

    def __repr__(self):
        def has(attr):
            return attr is not None

        fstr = []
        if has(self.button):
            fstr.append(str(self.button))
        if has(self.x):
            fstr.append('x ' + str(self.x))
        if has(self.y):
            fstr.append('y ' + str(self.y))
        if has(self.xRel):
            fstr.append('xRel ' + str(self.xRel))
        if has(self.yRel):
            fstr.append('yRel ' + str(self.yRel))
        if has(self.direction):
            fstr.append('direction ' + str(self.direction))

        return super(MouseEvent, self).__repr__() + ', ' + ', '.join(fstr)


class FingerEventNames(object):
    fingerDown = 'fingerDown'
    fingerUp = 'fingerUp'
    motion = 'motion'


class FingerEvent(Event):
    def __init__(self, event):
        super(FingerEvent, self).__init__(EventTypes.Finger)
        self._code = event.type
        self.x = None
        self.y = None
        self.xRel = None
        self.yRel = None
        code = self._code
        if code in [SDL_FINGERDOWN, SDL_FINGERUP]:
            specEvent = event.button
            self.button = self._buttons[specEvent.button]
            self.x = specEvent.x
            self.y = specEvent.y
            if code == SDL_FINGERDOWN:
                self.eventName = FingerEventNames.fingerDown
            else:
                self.eventName = FingerEventNames.fingerUp
        elif code == SDL_FINGERMOTION:
            specEvent = event.motion
            self.x = specEvent.x
            self.y = specEvent.y
            if self.xRel is None and (specEvent.xrel == specEvent.x or specEvent.yrel == specEvent.y):
                self.xRel = 0
                self.yRel = 0
            else:
                self.xRel = specEvent.xrel
                self.yRel = specEvent.yrel
            self.eventName = MouseEventNames.motion
        elif code == SDL_MOUSEWHEEL:
            specEvent = event.wheel
            self.x = specEvent.x
            self.y = specEvent.y
            self.direction = specEvent.direction
            self.eventName = MouseEventNames.wheel
        else:
            self.eventName = 'Unhandled mouse event type: ' + str(code)
            return


class TextEventNames(object):
    textEdit = 'textEdit'
    textInput = 'textInput'


class TextEvent(Event):
    def __init__(self, event, etype):
        super(TextEvent, self).__init__(EventTypes.Text)
        self.text = event.text.text
        if etype == SDL_TEXTEDITING:
            self.eventName = TextEventNames.textEdit
        else:
            self.eventName = TextEventNames.textInput

    def __repr__(self):
        return super(TextEvent, self).__repr__() + '({}), name= {}, text= {}'.format(self.eventName, self.text)
