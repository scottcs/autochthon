"""Game Events."""


class Event:
    """Event class.

    Rather than a list or a set, this uses a dict to keep track of handlers.
    Only the dict's keys are used, which will be unique, and in Python 3.7 are
    also guaranteed to be ordered.

    """
    def __init__(self):
        self.handlers = dict()

    def handle(self, handler):
        """Register a handler."""
        self.handlers[handler] = True
        return self

    def unhandle(self, handler):
        """Unregister a handler."""
        try:
            del self.handlers[handler]
        except KeyError:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def fire(self, *args, **kwargs):
        """Fire the event."""
        for handler in self.handlers.keys():
            handler(*args, **kwargs)

    def num_handlers(self):
        """Get the number of handlers."""
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__ = num_handlers


InputEvent = Event()
GameOverEvent = Event()
PlayerMovementEvent = Event()
