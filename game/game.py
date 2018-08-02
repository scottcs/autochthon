"""Main game class."""
from typing import List

import esper

from game.component.renderable import Renderable
from game.component.positional import Positional
from game.events import GameOverEvent
from game.input import InputHandler
from game.processor.playermovement import PlayerMovementProcessor
from game.state import GameState
from game.types import EventType, Entity

MOMENTS_PER_TURN = 10


class Game:
    """Main game object."""

    def __init__(self, render_processor: esper.Processor) -> None:
        self.game_over: bool = False
        self.world: esper.World = esper.World()
        self.input_handler: InputHandler = InputHandler()
        self.state: GameState = GameState.PLAYING
        self.player: Entity = self.world.create_entity(
            Renderable(1, 0xff3333, 0),
            Positional(40, 10)
        )
        self.crab: Entity = self.world.create_entity(
            Renderable(39, 0xffff33, 1),
            Positional(10, 10)
        )

        GameOverEvent.handle(self.shutdown)

        self.world.add_processor(render_processor)
        self.world.add_processor(PlayerMovementProcessor(self.player))

    def update(self) -> None:
        """Update the game world."""
        self.world.process()

    def shutdown(self, event: EventType) -> None:
        """Shut down the game."""
        if event.get('shutdown'):
            print('Shutting down.')
            self.game_over = True
