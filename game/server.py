"""Autochthon server."""
import json
from typing import Optional

import esper
import tornado.ioloop
import tornado.web
import tornado.websocket

from game.game import Game, MOMENTS_PER_TURN
from game.component.renderable import Renderable

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
        self.game_callback.input_events.append(json.loads(message))

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


class WebRenderProcessor(esper.Processor):
    """Game render processor for web socket."""

    def __init__(self, socket):
        super().__init__()
        self.socket = socket

    def process(self):
        """Process all renderables."""
        # cell.id
        # cell.x, cell.y
        # cell.tileset
        # cell.tile
        # cell.tint
        map_data = {}
        cells = []
        for ent, renderable in sorted(self.world.get_component(Renderable),
                                      key=lambda x: x[1].layer):
            cells.append([ent, renderable.x, renderable.y, renderable.tile_id, renderable.tint])
        map_data['cells'] = cells
        self.socket.write_all({'map': map_data})


class GameCallback(tornado.ioloop.PeriodicCallback):
    """Hook the game loop into tornado's io loop."""
    game = None

    def __init__(self, websocket: GameWebSocket):
        ms = 1000 // MOMENTS_PER_TURN
        if GameCallback.game is None:
            GameCallback.game = Game(WebRenderProcessor(websocket))
        self.input_events = []
        super().__init__(self.process_events, ms)

    def process_events(self):
        """Send game events to the game."""
        while self.input_events:
            GameCallback.game.process_input_event(self.input_events.pop())
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
