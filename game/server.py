"""Autochthon server."""
import json
from typing import Optional

import tornado.ioloop
import tornado.web
import tornado.websocket

from game.events import InputEvent
from game.game import Game, MOMENTS_PER_TURN
from game.processor.render import WebRenderProcessor

DEFAULT_PORT = 19999


class MainHandler(tornado.web.RequestHandler):
    """Main server http handler."""

    def get(self):
        """HTTP Get."""
        self.render('index.html')


class GameWebSocket(tornado.websocket.WebSocketHandler):
    """Websocket handler."""
    connections = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_callback = GameCallback(self)
        self.game_callback.start()

    def open(self):
        """Open a connection."""
        self.connections.add(self)
        self.set_nodelay(True)

    def write_all(self, *args, **kwargs):
        """Write to all connections."""
        for client in self.connections:
            client.write_message(*args, **kwargs)

    def on_message(self, message: str):
        """Called when a message is received over the connection.

        :param message: Message received.

        """
        data = json.loads(message)
        keys = data.get('keys')
        mouse = data.get('mouse')
        if keys or mouse:
            InputEvent(keys=keys, mouse=mouse, state=self.game_callback.game.state)

    def on_close(self):
        """Called when closing a connection."""
        self.connections.remove(self)

    def get_compression_options(self):
        """Override default class to turn on compression.

        Returning None disables compression. Returning a dict enables it,
        even if the dict is empty. Possibly want to mess with `compression_level`
        in the dict.

        """
        return {}


class GameCallback(tornado.ioloop.PeriodicCallback):
    """Hook the game loop into tornado's io loop."""
    game = None

    def __init__(self, websocket: GameWebSocket):
        ms = 1000 // MOMENTS_PER_TURN
        if GameCallback.game is None:
            GameCallback.game = Game(WebRenderProcessor(websocket))
        super().__init__(self.process_events, ms)

    @staticmethod
    def process_events():
        """Send game events to the game."""
        GameCallback.game.update()


def make_app() -> tornado.web.Application:
    """Make a new tornado app."""
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/websocket', GameWebSocket),
    ],
        static_path='static',
        template_path='templates')


def run_server(port: Optional[int]=None):
    """Run the game as a websockets server."""
    port = port and int(port) or DEFAULT_PORT
    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    run_server()
