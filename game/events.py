"""Game Events."""
from __future__ import annotations
from typing import Dict, Optional, List

from game.types import EventHandler, EventType


class Event:
    """Event class.

    Events should not be used for game logic! That's what systems and components are for!

    Rather than a list or a set, this uses a dict to keep track of handlers.
    Only the dict's keys are used, which will be unique, and in Python 3.7 are
    also guaranteed to be ordered.

    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.handlers: Dict[EventHandler, bool] = dict()
        self._to_unhandle: List[EventHandler] = []

    def handle(self, handler: EventHandler) -> Event:
        """Register a handler."""
        self.handlers[handler] = True
        return self

    def unhandle(self, handler: EventHandler) -> Event:
        """Unregister a handler."""
        self._to_unhandle.append(handler)
        return self

    def _remove_handlers(self) -> None:
        while self._to_unhandle:
            handler = self._to_unhandle.pop()
            try:
                del self.handlers[handler]
            except KeyError:
                raise ValueError("Handler is not handling this event, so cannot unhandle it.")

    def fire(self, event: Optional[EventType] = None) -> None:
        """Fire the event."""
        print(f"FIRE {self} {event}")
        if event and "bytearray" in event:
            print(f"{len(event['bytearray'])}")
        for handler in self.handlers.keys():
            handler(event or {})
        self._remove_handlers()

    def num_handlers(self) -> int:
        """Get the number of handlers."""
        return len(self.handlers)

    def __repr__(self) -> str:
        return f"<{self.name}>"

    __call__ = fire
    __len__ = num_handlers


ChoiceFromListEvent = Event("ChoiceFromListEvent")
ChooseFromListEvent = Event("ChooseFromListEvent")
GameLogEvent: Event = Event("GameLogEvent")
GameOverEvent: Event = Event("GameOverEvent")
InputEvent: Event = Event("InputEvent")
RefreshMapEvent: Event = Event("RefreshMapEvent")
PlayerActedEvent: Event = Event("PlayerActedEvent")
UpdateMapRenderEvent: Event = Event("UpdateMapRenderEvent")
