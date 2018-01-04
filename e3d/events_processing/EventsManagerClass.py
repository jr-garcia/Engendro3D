from sdl2 import SDL_GetKeyboardState, SDL_PumpEvents, SDL_GetKeyFromName, SDL_GetScancodeFromKey
from collections import OrderedDict
from ctypes import ArgumentError

from .EventsListenerClass import EventsListener
from .eventClasses import *


class EventsManager(object):
    def __init__(self):
        self._listeners = OrderedDict()
        self._keysState = SDL_GetKeyboardState(None)
        self._lastX = -1
        self._lastY = -1

    def addListener(self, ID, listener):
        """


        @type listener: e3d.events_processing.EventsListenerClass.EventsListener
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
        clickEvent = None
        for listener in self._listeners.values():
            etype = event.type
            # myEvent = None
            if etype in [SDL_KEYDOWN, SDL_KEYUP]:
                myEvent = KeyEvent(event.key, etype)
                listener.onKeyEvent(myEvent)
            elif etype in [SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP, SDL_MOUSEMOTION, SDL_MOUSEWHEEL]:
                myEvent = MouseEvent(event)
                currentX = myEvent.x
                currentY = myEvent.y
                if etype == SDL_MOUSEBUTTONDOWN:
                    self._lastX = currentX
                    self._lastY = currentY
                if etype == SDL_MOUSEBUTTONUP:
                    if self._lastX == currentX and self._lastY == currentY:
                        clickEvent = MouseEvent(event)
                        if clickEvent._clicks == 1:
                            clickEvent.eventName = MouseEventNames.click
                        else:
                            clickEvent.eventName = MouseEventNames.doubleClick
                listener.onMouseEvent(myEvent)
            elif etype == SDL_WINDOWEVENT:
                myEvent = WindowEvent(event.window)
                listener.onWindowEvent(myEvent)
            elif etype in [SDL_FINGERDOWN, SDL_FINGERUP, SDL_FINGERMOTION]:
                myEvent = FingerEvent(event)
            elif etype in [SDL_TEXTEDITING, SDL_TEXTINPUT]:
                # print('text input/edit', etype, event.text.text)
                SDL_PumpEvents()
                return True
            else:
                if isinstance(event, Event):
                    listener.onCustomEvent(event)
                    return event.discarded
                else:
                    # print('Unhandled event etype: ' + str(etype))
                    return False
            if myEvent.discarded:
                break
        if clickEvent is not None:
            for listener in self._listeners.values():
                listener.onMouseEvent(clickEvent)
                if clickEvent.discarded:
                    break

    def isKeyPressed(self, keyName):
        SDL_PumpEvents()
        try:
            key = SDL_GetKeyFromName(keyName)
        except TypeError:
            key = SDL_GetKeyFromName(keyName.encode())
        except ArgumentError as ar:
            if 'TypeError' in str(ar):
                key = SDL_GetKeyFromName(keyName.encode())
        scan = SDL_GetScancodeFromKey(key)
        return self._keysState[scan]
