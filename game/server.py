"""Autochthon server."""
from typing import Optional, Any, Union

import tornado.ioloop
import tornado.web
import tornado.websocket

from game.events import InputEvent, WebsocketWriteAllEvent
from game.game import Game, MOMENTS_PER_TURN
from game.processor.render import WebRenderProcessor
from game.state import GameState
from game.types import EventType


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
        self.game_callback: GameCallback = GameCallback()
        self.game_callback.start()
        WebsocketWriteAllEvent.handle(self.on_websocket_write_all)

    def open(self, *args: Any, **kwargs: Any) -> None:
        """Open a connection."""
        self.connections.add(self)
        self.set_nodelay(True)

    def on_websocket_write_all(self, event: EventType) -> None:
        """Handle WebsocketWriteAllEvent"""
        binary: bool = event.pop('binary', False)
        message: Union[str, bytes] = event.pop('message', None)
        if message:
            self.write_all(message, binary=binary)

    def write_all(self, *args: Any, **kwargs: Any) -> None:
        """Write to all connections."""
        for client in self.connections:
            client.write_message(*args, **kwargs)

    def on_message(self, message: Union[str, bytes]) -> None:
        """Called when a message is received over the connection."""
        if isinstance(message, bytes):
            # byte 0: event type
            # byte 1: modifiers
            # byte 2: key/button code
            # byte 3-4: x coordinate
            # byte 5-6: y coordinate
            InputEvent({
                'event': message[0],
                'modifiers': message[1],
                'code': message[2],
                'x_coord': int.from_bytes(message[3:5], byteorder='big'),
                'y_coord': int.from_bytes(message[5:7], byteorder='big'),
                'state': self.game_callback.get_game_state(),
            })

    def on_close(self) -> None:
        """Called when closing a connection."""
        self.connections.remove(self)

    def get_compression_options(self) -> Optional[dict]:
        """Override default class to turn on compression.

        Returning None disables compression. Returning a dict enables it,
        even if the dict is empty. Possibly want to mess with `compression_level`
        in the dict.

        """
        return None


def make_app() -> tornado.web.Application:
    """Make a new tornado app."""
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/websocket', GameWebSocket),
    ],
        static_path='static',
        template_path='templates',
        compress_response=False)


def run_server(config: dict) -> None:
    """Run the game as a websockets server."""
    port: int = config['server']['port']
    host: str = config['server']['host']
    app: tornado.web.Application = make_app()
    app.listen(port, address=host)
    print(f'Listening on {host}:{port}...')
    tornado.ioloop.IOLoop.current().start()
