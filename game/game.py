"""Main game class."""
from random import randint

import esper

from game.component.renderable import Renderable
from game.component.positional import Positional
from game.events import GameOverEvent, ServerNeedsUpdateEvent, QueueWorkEvent
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
        self.work_to_process: list = []
        self.moment: int = 0
        self.turn: int = 0
        self.anim_tick: int = 0

        self.map = ClassicMap(100, 100, self.world)
        self.map.create()

        self.world.player: Entity = self.world.create_entity(
            Renderable(1, 0xffff33, RenderLayer.PLAYER),
            Positional(self.map.start_pos.x, self.map.start_pos.y)
        )
        self.crab: Entity = self.world.create_entity(
            Renderable(39, 0xff3333, RenderLayer.ENEMY),
            Positional(10, 10)
        )

        for cell in self.map:
            if cell.transparent:
                # floor
                self.world.create_entity(
                    Renderable(220, 0x202020, RenderLayer.FLOOR),
                    Positional(cell.x, cell.y)
                )
            else:
                # wall
                self.world.create_entity(
                    Renderable(234, 0x332811, RenderLayer.WALL),
                    Positional(cell.x, cell.y)
                )

        # for _ in range(10000):
        #     self.world.create_entity(
        #         Renderable(randint(2, 38), randint(0, 0x888888), RenderLayer.FLOOR),
        #         Positional(randint(0, 99), randint(0, 99))
        #     )

        GameOverEvent.handle(self.shutdown)
        QueueWorkEvent.handle(self.on_queue_work)
        self.work_to_process.append('draw')

        self.world.add_processor(render_processor)
        self.world.add_processor(PlayerMovementProcessor())
        # self.world.add_processor(EnemyMovementProcessor())

    def update(self) -> None:
        """Update the game world."""
        ServerNeedsUpdateEvent.fire({'render': True})
        if self.work_to_process:
            work = self.work_to_process.pop()
            self.tick()
            self.world.process({
                'turn': self.turn,
                'moment': self.moment,
                'work': work,
            })

    def tick(self) -> None:
        """Update moment/turn counters."""
        self.moment += 1
        if self.moment > 10:
            self.moment = 0
            self.turn += 1

    def on_queue_work(self, event: EventType) -> None:
        """Handle a work unit queue request."""
        work = event.get('work', None)
        if work:
            self.work_to_process.append(work)

    def shutdown(self, event: EventType) -> None:
        """Shut down the game."""
        if event.get('shutdown'):
            print('Shutting down.')
            self.game_over = True
