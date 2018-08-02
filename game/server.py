"""Autochthon server."""
import json
from typing import Optional, Any

import tornado.ioloop
import tornado.web
import tornado.websocket

from game.events import InputEvent, WebsocketWriteAllEvent
from game.game import Game, MOMENTS_PER_TURN
from game.processor.render import WebRenderProcessor
from game.state import GameState
from game.types import EventType

DEFAULT_PORT = 19999


class MainHandler(tornado.web.RequestHandler):
    """Main server http handler."""

    def get(self, *args: Any, **kwargs: Any) -> None:
        """HTTP Get."""
        self.render('index.html')


class GameCallback(tornado.ioloop.PeriodicCallback):
    """Hook the game loop into tornado's io loop."""
    game: Optional[Game] = None

    def __init__(self) -> None:
        ms = 1000 // MOMENTS_PER_TURN
        if GameCallback.game is None:
            GameCallback.game = Game(WebRenderProcessor())
        super().__init__(self.process_events, ms)

    @staticmethod
    def get_game_state() -> GameState:
        """state property"""
        if GameCallback.game is not None:
            return GameCallback.game.state
        return GameState.UNKNOWN

    @staticmethod
    def process_events() -> None:
        """Send game events to the game."""
        if GameCallback.game is not None:
            GameCallback.game.update()


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


def make_app() -> tornado.web.Application:
    """Make a new tornado app."""
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/websocket', GameWebSocket),
    ],
        static_path='static',
        template_path='templates',
        compress_response=True)


def run_server(config: dict) -> None:
    """Run the game as a websockets server."""
    port = config['server'].get('port', DEFAULT_PORT)
    app = make_app()
    app.listen(port)
    print(f'Listening on port {port}...')
    tornado.ioloop.IOLoop.current().start()
