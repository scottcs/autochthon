"""Game Events."""
from __future__ import annotations
from typing import Dict, Optional

from game.types import EventHandler, EventType


class Event:
    """Event class.

    Events should not be used for game logic! That's what systems and components are for!

    Rather than a list or a set, this uses a dict to keep track of handlers.
    Only the dict's keys are used, which will be unique, and in Python 3.7 are
    also guaranteed to be ordered.

    """
    def __init__(self) -> None:
        self.handlers: Dict[EventHandler, bool] = dict()

    def handle(self, handler: EventHandler) -> Event:
        """Register a handler."""
        self.handlers[handler] = True
        return self

    def unhandle(self, handler: EventHandler) -> Event:
        """Unregister a handler."""
        try:
            del self.handlers[handler]
        except KeyError:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def fire(self, event: Optional[EventType]=None) -> None:
        """Fire the event."""
        for handler in self.handlers.keys():
            handler(event or {})

    def num_handlers(self) -> int:
        """Get the number of handlers."""
        return len(self.handlers)

    __call__ = fire
    __len__ = num_handlers


GameOverEvent: Event = Event()
InputEvent: Event = Event()
RefreshMapEvent: Event = Event()
PlayerActedEvent: Event = Event()
WebsocketWriteAllEvent: Event = Event()
