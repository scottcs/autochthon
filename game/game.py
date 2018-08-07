"""Main game class."""
from typing import Optional

import esper

from game.component.renderable import Renderable
from game.component.positional import Positional
from game.events import GameOverEvent, ServerNeedsUpdateEvent, WorkEnqueueEvent, TimePassedEvent
from game.input import InputHandler
from game.map import ClassicMap
# from game.processor.enemymovement import EnemyMovementProcessor
from game.processor.playermovement import PlayerMovementProcessor
from game.state import GameState
from game.types import EventType, Entity, RenderLayer
from game.utils.time import GameTime

MOMENTS_PER_TURN = 10


class Game:
    """Main game object."""

    def __init__(self, render_processor: esper.Processor, config: Optional[dict]=None) -> None:
        self.config: dict = config or {}
        self.game_over: bool = False
        self.world: esper.World = esper.World()
        self.input_handler: InputHandler = InputHandler()
        self.state: GameState = GameState.PLAYING
        self.work_to_process: list = []
        self.game_time: GameTime = GameTime()

        self.world.current_map = ClassicMap(self.config['map']['max_tiles_w'],
                                            self.config['map']['max_tiles_h'],
                                            self.world)
        self.world.current_map.create()

        self.world.player = self.world.create_entity(
            Renderable(1, 0xffff33, RenderLayer.PLAYER),
            Positional(self.world.current_map.start_pos.x, self.world.current_map.start_pos.y)
        )
        self.crab: Entity = self.world.create_entity(
            Renderable(39, 0xff3333, RenderLayer.ENEMY),
            Positional(10, 10)
        )

        count = 0
        for cell in self.world.current_map:
            count += 1
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
        WorkEnqueueEvent.handle(self.on_work_enqueue)
        TimePassedEvent.handle(self.on_time_passed)
        self.work_to_process.append('draw')

        self.world.add_processor(render_processor)
        self.world.add_processor(PlayerMovementProcessor())
        # self.world.add_processor(EnemyMovementProcessor())

    def update(self) -> None:
        """Update the game world."""
        ServerNeedsUpdateEvent.fire({'render': True})
        if self.work_to_process:
            work = self.work_to_process.pop()
            # TODO: work is a command
            # TODO: process the command
            # TODO: if anything takes time, process sends a TimePassedEvent and we update the clock
            self.world.process({
                'game_time': self.game_time,
                'work': work,
            })

    def on_work_enqueue(self, event: EventType) -> None:
        """Handle a work unit queue request."""
        work = event.get('work', None)
        if work:
            self.work_to_process.append(work)

    def on_time_passed(self, event: EventType) -> None:
        """Handle the passage of game time."""
        self.game_time += event.get('time_passed', 0)
        print(f'time is now: {self.game_time}')

    def shutdown(self, event: EventType) -> None:
        """Shut down the game."""
        if event.get('shutdown'):
            print('Shutting down.')
            self.game_over = True
