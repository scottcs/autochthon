"""Main game class."""
import esper

from game.component.renderable import Renderable
from game.events import GameOverEvent, InputEvent, PlayerMovementEvent
from game.input import InputHandler
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
        # TODO: Make this a processor?
        PlayerMovementEvent.handle(self.player_movement)

    def update(self):
        """Update the game world."""
        self.world.process()

    def player_movement(self, dx, dy):
        """Move the player."""
        player_renderable = self.world.component_for_entity(self.player, Renderable)
        crab_renderable = self.world.component_for_entity(self.crab, Renderable)
        player_renderable.x += dx
        player_renderable.y += dy
        crab_renderable.x = player_renderable.x
        crab_renderable.y = player_renderable.y
