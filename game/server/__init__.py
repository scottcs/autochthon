"""Autochthon server."""
from typing import Any

import tornado.ioloop
import tornado.web

from game.server.gamewebsocket import GameWebSocket

DEFAULT_PORT = 19999


class MainHandler(tornado.web.RequestHandler):
    """Main server http handler."""

    def get(self, *args: Any, **kwargs: Any) -> None:
        """HTTP Get."""
        self.render('index.html')


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
