"""Game callback class."""
from typing import Optional

import tornado.ioloop

from game.game import Game, MOMENTS_PER_TURN
from game.processor.render import WebRenderProcessor
from game.state import GameState


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
