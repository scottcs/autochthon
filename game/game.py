"""Main game class."""
from typing import Optional

import esper

from game.component.playercontrolled import PlayerControlled
from game.component.position import Position
from game.component.renderable import Renderable
from game.component.velocity import Velocity
from game.events import (GameOverEvent, ServerNeedsUpdateEvent, WorkEnqueueEvent, TimePassedEvent,
                         WorldNeedsUpdateEvent)
from game.map import ClassicMap
from game.processor.input import InputProcessor
from game.processor.movement import MovementProcessor
from game.state import GameState
from game.types import EventType, Entity, RenderLayer
from game.utils.time import GameTime


class Game:
    """Main game object."""

    def __init__(self, render_processor: esper.Processor, config: Optional[dict]=None) -> None:
        self.config: dict = config or {}
        self.game_over: bool = False
        self.world: esper.World = esper.World()
        self.state: GameState = GameState.PLAYING
        self.work_to_process: list = []
        self.game_time: GameTime = GameTime()
        self.needs_update: bool = True

        self.world.current_map = ClassicMap(self.config['map']['max_tiles_w'],
                                            self.config['map']['max_tiles_h'],
                                            self.world)
        self.world.current_map.create()

        self.world.create_entity(
            PlayerControlled(),
            Renderable(1, 0xffff33, RenderLayer.PLAYER),
            Position(self.world.current_map.start_pos.x, self.world.current_map.start_pos.y),
            Velocity(0, 0, GameTime()),
        )
        # crab
        self.world.create_entity(
            Renderable(39, 0xff3333, RenderLayer.ENEMY),
            Position(10, 10),
            Velocity(0, 0, GameTime()),
        )

        count = 0
        for cell in self.world.current_map:
            count += 1
            if cell.transparent:
                # floor
                self.world.create_entity(
                    Renderable(220, 0x202020, RenderLayer.FLOOR),
                    Position(cell.x, cell.y)
                )
            else:
                # wall
                self.world.create_entity(
                    Renderable(234, 0x332811, RenderLayer.WALL),
                    Position(cell.x, cell.y)
                )

        GameOverEvent.handle(self.shutdown)
        TimePassedEvent.handle(self.on_time_passed)
        WorkEnqueueEvent.handle(self.on_work_enqueue)
        WorldNeedsUpdateEvent.handle(self.on_needs_update)
        self.work_to_process.append('draw')

        self.world.add_processor(InputProcessor(), priority=3)
        self.world.add_processor(MovementProcessor(), priority=2)
        self.world.add_processor(render_processor)

    def on_needs_update(self, event: EventType) -> None:
        """Notification that we need to update."""
        self.needs_update = True

    def update(self) -> None:
        """Update the game world."""
        ServerNeedsUpdateEvent.fire({'render': True})
        # TODO: work is a command
        # TODO: process the command
        # TODO: if anything takes time, process sends a TimePassedEvent and we update the clock
        self.world.process({'game_time': self.game_time})

    def on_work_enqueue(self, event: EventType) -> None:
        """Handle a work unit queue request."""
        self.needs_update = True
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
