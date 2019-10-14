"""Game Events."""
from __future__ import annotations

import typing

import game.types


class Event:
    """Event class.

    Events should not be used for game logic! That's what systems and components are for!

    Rather than a list or a set, this uses a dict to keep track of handlers.
    Only the dict's keys are used, which will be unique, and in Python 3.7 are
    also guaranteed to be ordered.

    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.handlers: typing.Dict[game.types.EventHandler, bool] = dict()
        self._to_unhandle: typing.List[game.types.EventHandler] = []
        self._to_handle: typing.List[game.types.EventHandler] = []

    def handle(self, handler: game.types.EventHandler) -> Event:
        """Register a handler."""
        self.handlers[handler] = True
        self._to_handle.append(handler)
        return self

    def unhandle(self, handler: game.types.EventHandler) -> Event:
        """Unregister a handler."""
        self._to_unhandle.append(handler)
        return self

    def _remove_unhandled_handlers(self) -> None:
        while self._to_unhandle:
            handler = self._to_unhandle.pop()
            if handler in self._to_handle:
                # it's been added at some point after we wanted to remove it, so don't remove it
                continue
            try:
                del self.handlers[handler]
            except KeyError:
                raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        self._to_handle.clear()

    def fire(self, event: typing.Optional[game.types.Event] = None) -> None:
        """Fire the event."""
        self._remove_unhandled_handlers()
        to_iterate = list(self.handlers.keys())
        for handler in to_iterate:
            handler(event or {})
        self._remove_unhandled_handlers()

    def num_handlers(self) -> int:
        """Get the number of handlers."""
        return len(self.handlers)

    def __repr__(self) -> str:
        return f"<{self.name} ({len(self.handlers.keys())})>"

    __call__ = fire
    __len__ = num_handlers


ChoiceFromList: Event = Event("ChoiceFromList")
ChooseFromList: Event = Event("ChooseFromList")
ChoiceAccepted: Event = Event("ChoiceAccepted")
ChoiceDeclined: Event = Event("ChoiceDeclined")
Describe: Event = Event("Describe")
GameLog: Event = Event("GameLog")
GameOver: Event = Event("GameOver")
ShutDown: Event = Event("Shutdown")
Input: Event = Event("Input")
MenuClosed: Event = Event("MenuClosed")
SubMenuClosed: Event = Event("SubMenuClosed")
RenderEntities: Event = Event("RenderEntities")
RenderMap: Event = Event("RenderMap")
