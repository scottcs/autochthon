"""Game websocket class."""
import json
from typing import Any

import tornado.websocket

from game.events import InputEvent, WebsocketWriteAllEvent
from game.server.gamecallback import GameCallback
from game.types import EventType


class GameWebSocket(tornado.websocket.WebSocketHandler):
    """Websocket handler."""
    connections: set = set()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.game_callback = GameCallback()
        self.game_callback.start()
        WebsocketWriteAllEvent.handle(self.on_websocket_write_all)

    def open(self, *args: Any, **kwargs: Any) -> None:
        """Open a connection."""
        self.connections.add(self)
        self.set_nodelay(True)

    def on_websocket_write_all(self, event: EventType) -> None:
        """Handle WebsocketWriteAllEvent"""
        self.write_all(event)

    def write_all(self, *args: Any, **kwargs: Any) -> None:
        """Write to all connections."""
        for client in self.connections:
            client.write_message(*args, **kwargs)

    def on_message(self, message: str) -> None:
        """Called when a message is received over the connection.

        :param message: Message received.

        """
        data = json.loads(message)
        keys = data.get('keys')
        mouse = data.get('mouse')
        if keys or mouse:
            InputEvent(dict(keys=keys, mouse=mouse, state=self.game_callback.get_game_state()))

    def on_close(self) -> None:
        """Called when closing a connection."""
        self.connections.remove(self)

    def get_compression_options(self) -> dict:
        """Override default class to turn on compression.

        Returning None disables compression. Returning a dict enables it,
        even if the dict is empty. Possibly want to mess with `compression_level`
        in the dict.

        """
        return {}
