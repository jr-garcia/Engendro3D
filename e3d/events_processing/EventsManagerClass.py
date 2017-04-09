from sdl2 import SDL_GetKeyboardState, SDL_PumpEvents, SDL_GetKeyFromName, SDL_GetScancodeFromKey

from .EventsListenerClass import EventsListener
from .eventClasses import *


class EventsManager(object):
    def __init__(self):
        self._listeners = {}
        self._keysState = SDL_GetKeyboardState(None)

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
        for l in self._listeners.values():
            # SDL_PumpEvents()
            if l._announce(event):
                break

    def isKeyPressed(self, keyName):
        SDL_PumpEvents()
        try:
            key = SDL_GetKeyFromName(keyName)
        except:
            key = SDL_GetKeyFromName(keyName.encode())
        scan = SDL_GetScancodeFromKey(key)
        return self._keysState[scan]