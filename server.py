"""Autochthon server."""
import json

import tornado.ioloop
import tornado.web
import tornado.websocket

from game.game import Game


class MainHandler(tornado.web.RequestHandler):
    """Main server http handler."""

    def get(self):
        """HTTP Get."""
        self.render('index.html')


class GameWebSocket(tornado.websocket.WebSocketHandler):
    """Websocket handler."""
    connections = set()
    game = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.game is None:
            self.game = Game()

    def open(self):
        """Open a connection."""
        self.connections.add(self)

    def on_message(self, message: str):
        """Called when a message is received over the connection.

        :param message: Message received.

        """
        message_dict = json.loads(message)
        keys = message_dict.get('keys')
        mouse = message_dict.get('mouse')
        result = {}

        if keys:
            print(f'got keys {keys}')
            result = self.game.on_keyboard_input(keys)
        elif mouse:
            print(f'got mouse {mouse}')
            result = self.game.on_mouse_input(mouse)

        game_over = result.get('game_over')
        map_deltas = result.get('map_deltas')

        if game_over:
            print('game over')
            return

        # TODO: keep track of map, update change set, send change set
        if map_deltas:
            [client.write_message({'deltas': map_deltas}) for client in self.connections]

    def on_close(self):
        """Called when closing a connection."""
        self.connections.remove(self)
        # TODO: save game?


def make_app() -> tornado.web.Application:
    """Make a new tornado app."""
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/websocket', GameWebSocket),
    ],
        static_path='static',
        template_path='templates')


if __name__ == '__main__':
    app = make_app()
    app.listen(19999)
    tornado.ioloop.IOLoop.current().start()
