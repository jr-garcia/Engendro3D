from abc import ABCMeta, abstractmethod
import sfml as sf
from .eventClasses_sfml import *


class EventsListener(object):
    def __init__(self):
        """
        Inherit from this class and implement the desired on*Event methods to receive event
        notifications. Then invoke your function callbacks accordingly.
        @rtype : EventsListener
        """
        pass

    def onMouseEvent(self, event):
        pass

    def onKeyEvent(self, event):
        pass

    def onJoystickEvent(self, event):
        pass

    def onWindowEvent(self, event):
        pass

    def onCustomEvent(self, event):
        pass

    def _announce(self, event):
        etype = type(event)
        # myEvent = None
        if isinstance(event, sf.KeyEvent):
            myEvent = KeyEvent(event)
            self.onKeyEvent(myEvent)
        elif isinstance(event, (sf.MouseButtonEvent, sf.MouseEvent, sf.MouseMoveEvent, sf.MouseWheelEvent)):
            myEvent = MouseEvent(event)
            self.onMouseEvent(myEvent)
        elif isinstance(event, (sf.FocusEvent, sf.CloseEvent, sf.ResizeEvent)):
            myEvent = WindowEvent(event)
            self.onWindowEvent(myEvent)
        # elif etype in [SDL_FINGERDOWN, SDL_FINGERUP, SDL_FINGERMOTION]:
        #     myEvent = FingerEvent(event)
        elif isinstance(event, sf.TextEvent):
            # print ('text input/edit', etype, event.text.text)
            return True
        else:
            if isinstance(event, Event):
                self.onCustomEvent(event)
                return event.discarded
            else:
                print('Unhandled event etype: ' + str(etype))
                return False
        return myEvent.discarded


class EventsManager(object):
    def __init__(self):
        self._listeners = {}
        keyboardDir = dir(sf.Keyboard)
        self._keyValues = {}
        for kn in keyboardDir:
            val = getattr(sf.Keyboard, kn)
            if not callable(val) and not kn.startswith('_'):
                self._keyValues[kn.lower()] = val

    def addListener(self, ID, listener):
        """


        @type listener: EventsListener
        @type ID: str
        """
        if not issubclass(type(listener), EventsListener) or not isinstance(listener, EventsListener):
            raise TypeError('"listener" object must be of type "EventsListener" or inherith from it.\n'
                            'It is of type: ' + str(type(listener)))
        self._listeners[ID] = listener

    def removeListener(self, ID):
        if ID in self._listeners:
            self._listeners.pop(ID)

    def _announce(self, event):
        for l in self._listeners.values():
            # SDL_PumpEvents()
            if l._announce(event):
                break

    def isKeyPressed(self, keyName):
        keyVal = self._keyValues[keyName]
        sf.Keyboard.is_key_pressed(keyVal)
