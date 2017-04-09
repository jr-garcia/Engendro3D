import sfml as sf

# Note: some Touchpads may get disable while keys are pressed.
# Is fixed by setting 'Palmcheck','Palm sensitivity' to off.


keyboardDir = dir(sf.Keyboard)
keyValues = {}
for kn in keyboardDir:
    val = getattr(sf.Keyboard, kn)
    if not callable(val) and not kn.startswith('_'):
        keyValues[val] = kn.lower()

class EventType(object):
    mouse = 'mouse'
    key = 'key'
    window = 'window'
    user = 'user'
    finger = 'finger'
    custom = 'custom'

    def __init__(self):
        pass


class Event(object):
    def __init__(self, etype):
        """

        @etype etype: EventType
        """
        self.type = etype
        self.discarded = False
        self.name = ''

    def __repr__(self):
        return '{} event: {}'.format(self.type, self.name)


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
        self.code = event.type
        if isinstance(event, sf.ResizeEvent):
            self.name = windowEventName.sizeChanged
        elif isinstance(event, sf.CloseEvent):
            self.name = windowEventName.close
        elif isinstance(event, sf.FocusEvent):
            self.name = windowEventName.focusGained
            self.name = windowEventName.focusLost
        # elif self.code == SDL_WINDOWEVENT_EXPOSED:
        #     self.name = windowEventName.exposed
        # elif self.code == SDL_WINDOWEVENT_ENTER:
        #     self.name = windowEventName.enter
        # elif self.code == SDL_WINDOWEVENT_HIDDEN:
        #     self.name = windowEventName.hidden
        # elif self.code == SDL_WINDOWEVENT_LEAVE:
        #     self.name = windowEventName.leave
        # elif self.code == SDL_WINDOWEVENT_MOVED:
        #     self.name = windowEventName.moved
        # elif self.code == SDL_WINDOWEVENT_MAXIMIZED:
        #     self.name = windowEventName.maximized
        # elif self.code == SDL_WINDOWEVENT_MINIMIZED:
        #     self.name = windowEventName.minimized
        # elif self.code == SDL_WINDOWEVENT_SHOWN:
        #     self.name = windowEventName.shown
        # elif self.code == SDL_WINDOWEVENT_RESTORED:
        #     self.name = windowEventName.restored
        # elif self.code == SDL_WINDOWEVENT_RESIZED:
        #     self.name = windowEventName.resized
        else:
            self.name = 'Unhandled window event type: ' + str(type(event)) + str(self.code)


class KeyEventName(object):
    keyDown = 'keyDown'
    keyUp = 'keyUp'


class KeyEvent(Event):
    def __init__(self, event):
        super(KeyEvent, self).__init__(EventType.key)
        self.keyCode = event.code
        self.keyName = keyValues.get(self.keyCode, 'unknown_' + str(self.keyCode))
        if event.pressed:
            self.name = KeyEventName.keyDown
        else:
            self.name = KeyEventName.keyUp

    def __repr__(self):
        return super(KeyEvent, self).__repr__() + '({}), name= {}, code= {}'.format(self.name, self.keyName,
                                                                                     self.keyCode)


class MouseEventName(object):
    buttonDown = 'buttonDown'
    buttonUp = 'buttonUp'
    motion = 'motion'
    wheel = 'wheel'


class MouseEvent(Event):
    def __init__(self, event):
        self._buttons = {2: 'middle', 1: 'right', 0: 'left',
                         }
        super(MouseEvent, self).__init__(EventType.mouse)
        self.code = event.type
        self.x = None
        self.y = None
        self.xRel = None
        self.yRel = None
        self.button = None
        if isinstance(event, sf.MouseButtonEvent):
            specEvent = event.button
            self.button = self._buttons[specEvent]
            self.x = event.position.x
            self.y = event.position.y
            if event.pressed:
                self.name = MouseEventName.buttonDown
            else:
                self.name = MouseEventName.buttonUp
        elif isinstance(event, sf.MouseMoveEvent):
            specEvent = event.position
            self.x = specEvent.x
            self.y = specEvent.y
            self.name = MouseEventName.motion
        elif isinstance(event, sf.MouseWheelEvent):
            self.name = MouseEventName.wheel
            self.delta = event.delta
            self.pos = [event.position.x, event.position.y]
        # elif isinstance(event, sf.MouseEvent):
        #     pass
        else:
            self.name = 'Unhandled mouse event type: ' + str(self.code)
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
                self.name = FingerEventName.fingerDown
            else:
                self.name = FingerEventName.fingerUp
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
            self.name = MouseEventName.motion
        elif self.code == SDL_MOUSEWHEEL:
            specEvent = event.wheel
            self.name = MouseEventName.wheel
        else:
            self.name = 'Unhandled mouse event type: ' + str(self.code)
            return