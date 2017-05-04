from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP, SDL_MOUSEMOTION, SDL_MOUSEWHEEL, \
    SDL_WINDOWEVENT, SDL_FINGERDOWN, SDL_FINGERUP, SDL_FINGERMOTION, SDL_TEXTEDITING, SDL_TEXTINPUT, SDL_PumpEvents

from e3d.events_processing.eventClasses import KeyEvent, MouseEvent, WindowEvent, FingerEvent, Event


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
        etype = event.type
        # myEvent = None
        if etype in [SDL_KEYDOWN, SDL_KEYUP]:
            myEvent = KeyEvent(event.key, etype)
            self.onKeyEvent(myEvent)
        elif etype in [SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP, SDL_MOUSEMOTION, SDL_MOUSEWHEEL]:
            myEvent = MouseEvent(event)
            self.onMouseEvent(myEvent)
        elif etype == SDL_WINDOWEVENT:
            myEvent = WindowEvent(event.window)
            self.onWindowEvent(myEvent)
        elif etype in [SDL_FINGERDOWN, SDL_FINGERUP, SDL_FINGERMOTION]:
            myEvent = FingerEvent(event)
        elif etype in [SDL_TEXTEDITING, SDL_TEXTINPUT]:
            # print('text input/edit', etype, event.text.text)
            SDL_PumpEvents()
            return True
        else:
            if isinstance(event, Event):
                self.onCustomEvent(event)
                return event.discarded
            else:
                # print('Unhandled event etype: ' + str(etype))
                return False
        return myEvent.discarded
