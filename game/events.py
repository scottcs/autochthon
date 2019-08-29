"""Game Events."""
from __future__ import annotations

from typing import Dict, List, Optional

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
        self._to_handle: List[EventHandler] = []

    def handle(self, handler: EventHandler) -> Event:
        """Register a handler."""
        self.handlers[handler] = True
        self._to_handle.append(handler)
        # print(f"{self} added handler")
        return self

    def unhandle(self, handler: EventHandler) -> Event:
        """Unregister a handler."""
        self._to_unhandle.append(handler)
        # print(f"{self} unhandle")
        return self

    def _remove_handlers(self) -> None:
        while self._to_unhandle:
            handler = self._to_unhandle.pop()
            if handler in self._to_handle:
                # it's been added at some point after we wanted to remove it, so don't remove it
                continue
            try:
                # print(f"{self} removed handler")
                del self.handlers[handler]
            except KeyError:
                raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        self._to_handle.clear()

    def fire(self, event: Optional[EventType] = None) -> None:
        """Fire the event."""
        self._remove_handlers()
        # print(f"{self} fire event: {event}")
        for handler in self.handlers.keys():
            handler(event or {})
        self._remove_handlers()

    def num_handlers(self) -> int:
        """Get the number of handlers."""
        return len(self.handlers)

    def __repr__(self) -> str:
        return f"<{self.name} ({len(self.handlers.keys())})>"

    __call__ = fire
    __len__ = num_handlers


ChoiceFromListEvent: Event = Event("ChoiceFromListEvent")
ChooseFromListEvent: Event = Event("ChooseFromListEvent")
ChoiceAcceptedEvent: Event = Event("ChooseFromListEvent")
ChoiceDeclinedEvent: Event = Event("ChooseFromListEvent")
DescribeEvent: Event = Event("DescribeEvent")
GameLogEvent: Event = Event("GameLogEvent")
GameOverEvent: Event = Event("GameOverEvent")
InputEvent: Event = Event("InputEvent")
MenuClosedEvent: Event = Event("MenuClosedEvent")
SubMenuClosedEvent: Event = Event("SubMenuClosedEvent")
RenderEntitiesEvent: Event = Event("RenderEntitiesEvent")
RenderMapEvent: Event = Event("RenderMapEvent")
RequestRenderEvent: Event = Event("RequestRenderEvent")
UpdateMapRenderEvent: Event = Event("UpdateMapRenderEvent")
