"""Main game class."""
from random import randint

import esper

from game.component.renderable import Renderable
from game.component.positional import Positional
from game.events import GameOverEvent, ServerNeedsUpdateEvent
from game.input import InputHandler
from game.map import ClassicMap
from game.processor.enemymovement import EnemyMovementProcessor
from game.processor.playermovement import PlayerMovementProcessor
from game.state import GameState
from game.types import EventType, Entity, RenderLayer

MOMENTS_PER_TURN = 10


class Game:
    """Main game object."""

    def __init__(self, render_processor: esper.Processor) -> None:
        self.game_over: bool = False
        self.world: esper.World = esper.World()
        self.input_handler: InputHandler = InputHandler()
        self.state: GameState = GameState.PLAYING
        self.moment: int = 0
        self.turn: int = 0
        self.anim_tick: int = 0

        self.map = ClassicMap(100, 100, self.world)
        self.map.create()

        self.player: Entity = self.world.create_entity(
            Renderable(1, 0xffff33, RenderLayer.PLAYER),
            # Positional(self.map.start_pos.x, self.map.start_pos.y)
            Positional(40, 10)
        )
        self.crab: Entity = self.world.create_entity(
            Renderable(39, 0xff3333, RenderLayer.ENEMY),
            Positional(10, 10)
        )
        for _ in range(10000):
            self.world.create_entity(
                Renderable(randint(2, 38), randint(0, 0x888888), RenderLayer.FLOOR),
                Positional(randint(0, 99), randint(0, 99))
            )
        GameOverEvent.handle(self.shutdown)

        self.world.add_processor(render_processor)
        self.world.add_processor(PlayerMovementProcessor(self.player))
        self.world.add_processor(EnemyMovementProcessor(self.player))

    def update(self) -> None:
        """Update the game world."""
        # TODO: Possibly complicate this; only if key pressed or animation needs to happen.
        ServerNeedsUpdateEvent.fire({'render': True})
        self.world.process()

    def shutdown(self, event: EventType) -> None:
        """Shut down the game."""
        if event.get('shutdown'):
            print('Shutting down.')
            self.game_over = True
