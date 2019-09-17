"""Autochthon server."""
import json
import logging
import pathlib
import typing

import tornado.ioloop
import tornado.web
import tornado.websocket

import game.core.main
import game.events
import game.processor.player_input
import game.processor.render
import game.types
import gamedata.config

WEBSOCKET_EVENTS_JSON = pathlib.Path("data") / pathlib.Path("websocketevents.json")
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class MainHandler(tornado.web.RequestHandler):
    """Main server http handler."""

    def get(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """HTTP Get."""
        self.render("index.html")


class GameCallback(tornado.ioloop.PeriodicCallback):
    """Hook the game loop into tornado's io loop."""

    game_object: typing.Optional[game.core.main.Game] = None

    def __init__(self, config: typing.Optional[dict] = None) -> None:
        if GameCallback.game_object is None:
            GameCallback.game_object = game.core.main.Game(
                game.processor.render.WebRender(),
                game.processor.player_input.WebPlayerInput(),
                config=config,
            )
        super().__init__(self.process_events, 1)

    @staticmethod
    def get_game_state() -> game.types.GameState:
        """state property"""
        if GameCallback.game_object is not None:
            return GameCallback.game_object.state
        return game.types.GameState.unknown

    @staticmethod
    def process_events() -> None:
        """Send game events to the game."""
        if GameCallback.game_object is not None:
            GameCallback.game_object.update()


class GameWebSocket(tornado.websocket.WebSocketHandler):
    """Websocket handler."""

    connections: set = set()

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        config = kwargs.pop("config", None)
        super().__init__(*args, **kwargs)
        with open(WEBSOCKET_EVENTS_JSON) as f:
            self.socket_events = json.load(f)
        if len(self.connections) == 0:
            # TODO: need some way to determine which connection is the player, even after refresh
            game.events.ChoiceAccepted.handle(self._on_choice_accepted)
            game.events.ChoiceDeclined.handle(self._on_choice_declined)
            game.events.ChooseFromList.handle(self._on_choose_from_list)
            game.events.Describe.handle(self._on_describe)
            game.events.GameLog.handle(self._on_game_log)
            game.events.UpdateMapRender.handle(self._on_update_map_render)
        self.game_callback: GameCallback = GameCallback(config=config)
        self.game_callback.start()

    def open(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Open a connection."""
        self.connections.add(self)
        self.set_nodelay(True)

    @staticmethod
    def _get_byte_array_from_event(event: game.types.EventType) -> bytearray:
        log.debug(f"get byte array from event event: {event}")
        ba: bytearray = event.pop("bytearray", None)
        if not isinstance(ba, bytearray):
            log.debug(f"ba {type(ba)}: {ba}")
            raise TypeError("Only bytearray is supported over the websocket.")
        return ba

    def _on_update_map_render(self, event: game.types.EventType) -> None:
        log.debug(f"update map render handler event: {event}")
        ba: bytearray = self._get_byte_array_from_event(event)
        ba.insert(0, self.socket_events["FromServer"]["UpdateMap"])
        self.write_all(ba)

    def _on_game_log(self, event: game.types.EventType) -> None:
        log_string = json.dumps(event)
        ba: bytearray = bytearray()
        ba.append(self.socket_events["FromServer"]["GameLog"])
        ba.extend(log_string.encode("utf-8"))
        self.write_all(ba)

    def _on_choice_accepted(self, _event: game.types.EventType) -> None:
        ba: bytearray = bytearray()
        ba.append(self.socket_events["FromServer"]["ChoiceAccepted"])
        self.write_all(ba)

    def _on_choice_declined(self, event: game.types.EventType) -> None:
        msg = json.dumps(event)
        ba: bytearray = bytearray()
        ba.append(self.socket_events["FromServer"]["ChoiceDeclined"])
        ba.extend(msg.encode("utf-8"))
        self.write_all(ba)

    def _on_choose_from_list(self, event: game.types.EventType) -> None:
        msg = json.dumps(event)
        ba: bytearray = bytearray()
        ba.append(self.socket_events["FromServer"]["ChooseFromList"])
        ba.extend(msg.encode("utf-8"))
        self.write_all(ba)

    def _on_describe(self, event: game.types.EventType) -> None:
        msg = json.dumps(event)
        ba: bytearray = bytearray()
        ba.append(self.socket_events["FromServer"]["Describe"])
        ba.extend(msg.encode("utf-8"))
        self.write_all(ba)

    def write_all(self, ba: bytearray) -> None:
        """Write bytes to all connections."""
        for client in self.connections:
            client.write_message(bytes(ba), binary=True)

    def on_message(self, message: typing.Union[str, bytes]) -> None:
        """Called when a message is received over the connection."""
        if isinstance(message, bytes):
            if message[0] == self.socket_events["ToServer"]["RefreshGraphics"]:
                # byte 1: full refresh (boolean)
                game.events.RequestRender.fire({"full": bool(message[1])})
            elif message[0] == self.socket_events["ToServer"]["GameInput"]:
                # byte 1: input event flags
                # byte 2: modifiers
                # byte 3: key/button code
                # byte 4-5: x coordinate
                # byte 6-7: y coordinate
                game.events.Input.fire(
                    {
                        "event": message[1],
                        "modifiers": message[2],
                        "code": message[3],
                        "x_coord": int.from_bytes(message[4:6], byteorder="big"),
                        "y_coord": int.from_bytes(message[6:8], byteorder="big"),
                        "state": self.game_callback.get_game_state(),
                    }
                )
            elif message[0] == self.socket_events["ToServer"]["ChoiceFromList"]:
                # byte 1: modifiers
                # byte 2: key/button code
                game.events.ChoiceFromList.fire({"modifiers": message[1], "code": message[2]})
            elif message[0] == self.socket_events["ToServer"]["ModalWasClosed"]:
                game.events.MenuClosed.fire()
            elif message[0] == self.socket_events["ToServer"]["SubModalWasClosed"]:
                game.events.SubMenuClosed.fire()
            else:
                log.error(f"Unprocessed message type: {message[0]}")

    def on_close(self) -> None:
        """Called when closing a connection."""
        log.debug("Closing connection.")
        self.connections.remove(self)
        game.events.UpdateMapRender.unhandle(self._on_update_map_render)
        game.events.GameLog.unhandle(self._on_game_log)
        game.events.ChooseFromList.unhandle(self._on_choose_from_list)
        game.events.ChoiceDeclined.unhandle(self._on_choice_declined)
        game.events.ChoiceAccepted.unhandle(self._on_choice_accepted)

    def get_compression_options(self) -> typing.Optional[dict]:
        """Override default class to turn on compression.

        Returning None disables compression. Returning a dict enables it,
        even if the dict is empty. Possibly want to mess with `compression_level`
        in the dict.

        """
        return None


def make_app(config: typing.Mapping) -> tornado.web.Application:
    """Make a new tornado app."""
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/websocket", GameWebSocket, {"config": config}),
            (r"/data/(.*)", tornado.web.StaticFileHandler, {"path": "data"}),
        ],
        static_path="static",
        template_path="templates",
        compress_response=False,
    )


def run_server() -> None:
    """Run the game as a websockets server."""
    port: int = gamedata.config.CONFIG["server"]["port"]
    host: str = gamedata.config.CONFIG["server"]["host"]
    app: tornado.web.Application = make_app(gamedata.config.CONFIG)
    app.listen(port, address=host)
    log.info(f"Listening on {host}:{port}...")
    tornado.ioloop.IOLoop.current().start()
