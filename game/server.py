"""Autochthon server."""
import json
from typing import Optional

import tornado.ioloop
import tornado.web
import tornado.websocket

from game.game import Game, MOMENTS_PER_TURN

DEFAULT_PORT = 19999


class MainHandler(tornado.web.RequestHandler):
    """Main server http handler."""

    def get(self):
        """HTTP Get."""
        self.render('index.html')


class GameWebSocket(tornado.websocket.WebSocketHandler):
    """Websocket handler."""
    connections = set()
    game_callback = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.game_callback is None:
            self.game_callback = GameCallback(self)
            self.game_callback.start()

    def open(self):
        """Open a connection."""
        self.connections.add(self)

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


class GameCallback(tornado.ioloop.PeriodicCallback):
    """Hook the game loop into tornado's io loop."""

    def __init__(self, websocket: GameWebSocket):
        ms = 1000 // MOMENTS_PER_TURN
        super().__init__(self.process_events, ms)
        self.websocket = websocket
        self.game = Game()
        self.input_events = []
        self.display_events = []

    def process_events(self):
        """Send game events to the game."""
        while self.input_events:
            self.process_input_event(self.input_events.pop())
        while self.display_events:
            self.process_display_event(self.display_events.pop())

    def process_input_event(self, event: dict):
        """Process a single input event."""
        display_event = self.game.process_input_event(event)
        if display_event:
            self.display_events.append(display_event)

    def process_display_event(self, event: dict):
        """Process a single display event."""
        map_deltas = event.get('map_deltas')
        if map_deltas:
            self.websocket.write_all({'deltas': map_deltas})


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
