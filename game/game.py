"""Main game class."""
import esper

from game.component.renderable import Renderable
from game.input import InputHandler
from game.processor.playermovement import PlayerMovementProcessor
from game.state import GameState

MOMENTS_PER_TURN = 10


class Game:
    """Main game object."""

    def __init__(self, render_processor):
        self.game_over = False
        self.events = []
        self.world = esper.World()
        self.input_handler = InputHandler()
        self.state = GameState.PLAYING
        self.player = self.world.create_entity(Renderable(
            1,
            40, 10,
            0xff3333,
            0
        ))
        self.crab = self.world.create_entity(Renderable(
            39,
            10, 10,
            0xffff33,
            1
        ))

        self.world.add_processor(render_processor)
        self.world.add_processor(PlayerMovementProcessor(self.player))

    def update(self):
        """Update the game world."""
        self.world.process()
