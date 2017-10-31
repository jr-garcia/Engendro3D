from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP, SDL_MOUSEMOTION, SDL_MOUSEWHEEL, \
    SDL_WINDOWEVENT, SDL_FINGERDOWN, SDL_FINGERUP, SDL_FINGERMOTION, SDL_TEXTEDITING, SDL_TEXTINPUT, SDL_PumpEvents

from e3d.events_processing.eventClasses import KeyEvent, MouseEvent, WindowEvent, FingerEvent, Event


class EventsListener(object):
    def __init__(self):
        """
        Inherit from this class and implement the desired on*Event methods to respond to event
        notifications.
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
