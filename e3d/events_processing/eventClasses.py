from sdl2.events import *
from sdl2 import SDL_WINDOWEVENT_SIZE_CHANGED, SDL_WINDOWEVENT_CLOSE, SDL_WINDOWEVENT_FOCUS_GAINED, \
    SDL_WINDOWEVENT_FOCUS_LOST, SDL_WINDOWEVENT_EXPOSED, SDL_WINDOWEVENT_ENTER, SDL_WINDOWEVENT_HIDDEN, \
    SDL_WINDOWEVENT_LEAVE, SDL_WINDOWEVENT_MOVED, SDL_WINDOWEVENT_MAXIMIZED, SDL_WINDOWEVENT_MINIMIZED, \
    SDL_WINDOWEVENT_SHOWN, SDL_WINDOWEVENT_RESTORED, SDL_WINDOWEVENT_RESIZED
from sdl2.mouse import *
from sdl2.keyboard import *

# Note: some Touchpads may disable while keys are pressed.
# Is fixed by setting 'Palmcheck','Palm sensitivity' to off.


class EventType(object):
    mouse = 'mouse'
    key = 'key'
    window = 'window'
    user = 'user'
    finger = 'finger'
    custom = 'custom'
    text = 'text'

    def __init__(self):
        pass


class Event(object):
    def __init__(self, etype):
        """

        @etype etype: EventType
        """
        self.type = etype
        self.discarded = False
        self.eventName = ''

    def __repr__(self):
        return '{} event: {}'.format(self.type, self.eventName)


class windowEventName(object):
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
    sizeChanged = 'sizeChanged'

    def __init__(self):
        pass


class WindowEvent(Event):
    def __init__(self, event):
        """

        @rtype : WindowEvent
        """
        super(WindowEvent, self).__init__(EventType.window)
        self.code = event.event
        if self.code == SDL_WINDOWEVENT_SIZE_CHANGED:
            self.eventName = windowEventName.sizeChanged
            self.w = event.data1
            self.h = event.data2
        elif self.code == SDL_WINDOWEVENT_CLOSE:
            self.eventName = windowEventName.close
        elif self.code == SDL_WINDOWEVENT_FOCUS_GAINED:
            self.eventName = windowEventName.focusGained
        elif self.code == SDL_WINDOWEVENT_FOCUS_LOST:
            self.eventName = windowEventName.focusLost
        elif self.code == SDL_WINDOWEVENT_EXPOSED:
            self.eventName = windowEventName.exposed
        elif self.code == SDL_WINDOWEVENT_ENTER:
            self.eventName = windowEventName.enter
        elif self.code == SDL_WINDOWEVENT_HIDDEN:
            self.eventName = windowEventName.hidden
        elif self.code == SDL_WINDOWEVENT_LEAVE:
            self.eventName = windowEventName.leave
        elif self.code == SDL_WINDOWEVENT_MOVED:
            self.eventName = windowEventName.moved
            self.x = event.data1
            self.y = event.data2
        elif self.code == SDL_WINDOWEVENT_MAXIMIZED:
            self.eventName = windowEventName.maximized
        elif self.code == SDL_WINDOWEVENT_MINIMIZED:
            self.eventName = windowEventName.minimized
        elif self.code == SDL_WINDOWEVENT_SHOWN:
            self.eventName = windowEventName.shown
        elif self.code == SDL_WINDOWEVENT_RESTORED:
            self.eventName = windowEventName.restored
        elif self.code == SDL_WINDOWEVENT_RESIZED:
            self.eventName = windowEventName.resized
            self.w = event.data1
            self.h = event.data2
        else:
            self.eventName = 'Unhandled window event type: ' + str(self.code)


class KeyEventName(object):
    keyDown = 'keyDown'
    keyUp = 'keyUp'


class KeyEvent(Event):
    def __init__(self, event, etype):
        super(KeyEvent, self).__init__(EventType.key)
        self.keyCode = event.keysym.sym
        # self.keyScanCode = SDL_GetScancodeFromKey(event.keysym.sym)
        self.keyName = SDL_GetKeyName(event.keysym.sym).lower()
        if type(self.keyName) is bytes:
            self.keyName = self.keyName.decode()
        if etype == SDL_KEYDOWN:
            self.eventName = KeyEventName.keyDown
        else:
            self.eventName = KeyEventName.keyUp

    def __repr__(self):
        return super(KeyEvent, self).__repr__() + '({}), name= {}, code= {}'.format(self.eventName, self.keyName,
                                                                                    self.keyCode)


class MouseEventName(object):
    buttonDown = 'buttonDown'
    buttonUp = 'buttonUp'
    motion = 'motion'
    wheel = 'wheel'


class MouseEvent(Event):
    def __init__(self, event):
        self._buttons = {SDL_BUTTON_MIDDLE: 'middle', SDL_BUTTON_RIGHT: 'right', SDL_BUTTON_LEFT: 'left', 0: 'unknown0',
                         SDL_BUTTON_X1: 'x1', SDL_BUTTON_X2: 'x2', SDL_BUTTON_X1MASK: 'x1Mask',
                         SDL_BUTTON_X2MASK: 'x2Mask', 6: 'unknown6', 7: 'unknown7'}
        super(MouseEvent, self).__init__(EventType.mouse)
        self.code = event.type
        self.x = None
        self.y = None
        self.xRel = None
        self.yRel = None
        self.button = None
        if self.code in [SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP]:
            specEvent = event.button
            self.button = self._buttons[specEvent.button]
            self.x = specEvent.x
            self.y = specEvent.y
            if self.code == SDL_MOUSEBUTTONDOWN:
                self.eventName = MouseEventName.buttonDown
            else:
                self.eventName = MouseEventName.buttonUp
        elif self.code == SDL_MOUSEMOTION:
            specEvent = event.motion
            self.x = specEvent.x
            self.y = specEvent.y
            if self.xRel is None and (specEvent.xrel == specEvent.x or specEvent.yrel == specEvent.y):
                self.xRel = 0
                self.yRel = 0
            else:
                self.xRel = specEvent.xrel
                self.yRel = specEvent.yrel
            self.eventName = MouseEventName.motion
        elif self.code == SDL_MOUSEWHEEL:
            specEvent = event.wheel
            self.eventName = MouseEventName.wheel
        else:
            self.eventName = 'Unhandled mouse event type: ' + str(self.code)
            return

    def __repr__(self):
        fstr = []
        if self.button:
            fstr.append(str(self.button))
        if self.x:
            fstr.append('x ' + str(self.x))
        if self.xRel:
            fstr.append('xRel ' + str(self.xRel))
        if self.y:
            fstr.append('y ' + str(self.y))
        if self.yRel:
            fstr.append('yRel ' + str(self.yRel))

        return super(MouseEvent, self).__repr__() + ', ' + ', '.join(fstr)


class FingerEventName(object):
    fingerDown = 'fingerDown'
    fingerUp = 'fingerUp'
    motion = 'motion'


class FingerEvent(Event):
    def __init__(self, event):
        super(FingerEvent, self).__init__(EventType.finger)
        self.code = event.type
        self.x = None
        self.y = None
        self.xRel = None
        self.yRel = None
        if self.code in [SDL_FINGERDOWN, SDL_FINGERUP]:
            specEvent = event.button
            self.button = self._buttons[specEvent.button]
            self.x = specEvent.x
            self.y = specEvent.y
            if self.code == SDL_FINGERDOWN:
                self.eventName = FingerEventName.fingerDown
            else:
                self.eventName = FingerEventName.fingerUp
        elif self.code == SDL_FINGERMOTION:
            specEvent = event.motion
            self.x = specEvent.x
            self.y = specEvent.y
            if self.xRel is None and (specEvent.xrel == specEvent.x or specEvent.yrel == specEvent.y):
                self.xRel = 0
                self.yRel = 0
            else:
                self.xRel = specEvent.xrel
                self.yRel = specEvent.yrel
            self.eventName = MouseEventName.motion
        elif self.code == SDL_MOUSEWHEEL:
            specEvent = event.wheel
            self.eventName = MouseEventName.wheel
        else:
            self.eventName = 'Unhandled mouse event type: ' + str(self.code)
            return


class TextEventName(object):
    textEdit = 'textEdit'
    textInput = 'textInput'


class TextEvent(Event):
    def __init__(self, event, etype):
        super(KeyEvent, self).__init__(EventType.text)
        self.text = event.text.text
        if etype == SDL_TEXTEDITING:
            self.eventName = TextEventName.textEdit
        else:
            self.eventName = TextEventName.textInput

    def __repr__(self):
        return super(TextEvent, self).__repr__() + '({}), name= {}, text= {}'.format(self.eventName, self.text)
