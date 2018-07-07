"""Autochthon server."""
import json

import tornado.ioloop
import tornado.web
import tornado.websocket


class MainHandler(tornado.web.RequestHandler):
    """Main server http handler."""

    def get(self):
        """HTTP Get."""
        self.render('index.html')


class SimpleWebSocket(tornado.websocket.WebSocketHandler):
    """Websocket handler."""
    connections = set()

    def open(self):
        """Open a connection."""
        self.connections.add(self)

    def on_message(self, message: str):
        """Called when a message is received over the connection.

        :param message: Message received.

        """
        message_dict = json.loads(message)
        key = message_dict.get('key')
        print(f'got key {key}')
        # TODO: keep track of map, update change set, send change set
        if key is not None:
            [client.write_message({'message': key}) for client in self.connections]

    def on_close(self):
        """Called when closing a connection."""
        self.connections.remove(self)


def make_app() -> tornado.web.Application:
    """Make a new tornado app."""
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/websocket', SimpleWebSocket),
    ],
        static_path='static',
        template_path='templates')


if __name__ == '__main__':
    app = make_app()
    app.listen(19999)
    tornado.ioloop.IOLoop.current().start()
