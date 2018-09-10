"""Autochthon server."""
import json
import logging
from pathlib import Path
from typing import Optional, Any, Union, Mapping

import tornado.ioloop
import tornado.web
import tornado.websocket

from game.events import InputEvent, UpdateMapRenderEvent, RefreshMapEvent, GameLogEvent
from game.core.main import Game
from game.processor.render import WebRenderProcessor
from game.types import EventType, GameState

WEBSOCKET_EVENTS_JSON = Path('data') / Path('websocketevents.json')
DESIRED_FPS = 30
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class MainHandler(tornado.web.RequestHandler):
    """Main server http handler."""

    def get(self, *args: Any, **kwargs: Any) -> None:
        """HTTP Get."""
        self.render('index.html')


class GameCallback(tornado.ioloop.PeriodicCallback):
    """Hook the game loop into tornado's io loop."""
    game: Optional[Game] = None

    def __init__(self, config: Optional[dict]=None) -> None:
        if GameCallback.game is None:
            GameCallback.game = Game(WebRenderProcessor(), config=config)
        super().__init__(self.process_events, 1000 / DESIRED_FPS)

    @staticmethod
    def get_game_state() -> GameState:
        """state property"""
        if GameCallback.game is not None:
            return GameCallback.game.state
        return GameState.unknown

    @staticmethod
    def process_events() -> None:
        """Send game events to the game."""
        if GameCallback.game is not None:
            GameCallback.game.update()


class GameWebSocket(tornado.websocket.WebSocketHandler):
    """Websocket handler."""
    connections: set = set()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        config = kwargs.pop('config', None)
        super().__init__(*args, **kwargs)
        with open(WEBSOCKET_EVENTS_JSON) as f:
            self.socket_events = json.load(f)
        if len(self.connections) == 0:
            # TODO: need some way to determine which connection is the player, even after refresh
            GameLogEvent.handle(self._on_game_log)
            UpdateMapRenderEvent.handle(self._on_update_map_render)
        self.game_callback: GameCallback = GameCallback(config=config)
        self.game_callback.start()

    def open(self, *args: Any, **kwargs: Any) -> None:
        """Open a connection."""
        self.connections.add(self)
        self.set_nodelay(True)

    @staticmethod
    def _get_byte_array_from_event(event: EventType) -> bytearray:
        ba: bytearray = event.pop('bytearray', None)
        if not isinstance(ba, bytearray):
            raise TypeError('Only bytearray is supported over the websocket.')
        return ba

    def _on_update_map_render(self, event: EventType) -> None:
        ba: bytearray = self._get_byte_array_from_event(event)
        ba.insert(0, self.socket_events['FromServer']['UpdateMap'])
        self.write_all(ba)

    def _on_game_log(self, event: EventType) -> None:
        log_string = json.dumps(event)
        ba = bytearray()
        ba.append(self.socket_events['FromServer']['GameLog'])
        ba.extend(log_string.encode('utf-8'))
        self.write_all(ba)

    def write_all(self, ba: bytearray) -> None:
        """Write bytes to all connections."""
        for client in self.connections:
            client.write_message(bytes(ba), binary=True)

    def on_message(self, message: Union[str, bytes]) -> None:
        """Called when a message is received over the connection."""
        if isinstance(message, bytes):
            # ---- refresh event
            if message[0] == self.socket_events['ToServer']['RefreshGraphics']:
                RefreshMapEvent.fire()
            elif message[0] == self.socket_events['ToServer']['GameInput']:
                # ---- input event
                # byte 1: input event flags
                # byte 2: modifiers
                # byte 3: key/button code
                # byte 4-5: x coordinate
                # byte 6-7: y coordinate
                InputEvent.fire({
                    'event': message[1],
                    'modifiers': message[2],
                    'code': message[3],
                    'x_coord': int.from_bytes(message[4:6], byteorder='big'),
                    'y_coord': int.from_bytes(message[6:8], byteorder='big'),
                    'state': self.game_callback.get_game_state(),
                })
            else:
                log.error(f'Unprocessed message type: {message[0]}')

    def on_close(self) -> None:
        """Called when closing a connection."""
        self.connections.remove(self)
        UpdateMapRenderEvent.unhandle(self._on_update_map_render)
        GameLogEvent.unhandle(self._on_game_log)

    def get_compression_options(self) -> Optional[dict]:
        """Override default class to turn on compression.

        Returning None disables compression. Returning a dict enables it,
        even if the dict is empty. Possibly want to mess with `compression_level`
        in the dict.

        """
        return None


def make_app(config: Mapping) -> tornado.web.Application:
    """Make a new tornado app."""
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/websocket', GameWebSocket, {'config': config}),
        (r'/data/(.*)', tornado.web.StaticFileHandler, {'path': 'data'}),
    ],
        static_path='static',
        template_path='templates',
        compress_response=False)


def run_server(config: Mapping) -> None:
    """Run the game as a websockets server."""
    port: int = config['server']['port']
    host: str = config['server']['host']
    app: tornado.web.Application = make_app(config)
    app.listen(port, address=host)
    log.info(f'Listening on {host}:{port}...')
    tornado.ioloop.IOLoop.current().start()
