"""Main game class."""
from typing import Optional

import esper

from game.component.actor import Actor
from game.component.ai_simplemind import AISimpleMind
from game.component.hp import HP
from game.component.playercontrolled import PlayerControlled
from game.component.position import Position
from game.component.renderable import Renderable
from game.component.solid import Solid
# from game.component.toggleable import Toggleable
from game.events import GameOverEvent, RefreshMapEvent
from game.map import ClassicMap, Map
from game.processor import Priority
from game.processor.ai import AIProcessor
from game.processor.input import InputProcessor
from game.processor.movement import MovementProcessor
from game.processor.time import TimeProcessor
from game.state import GameState
from game.types import EventType, RenderLayer


class Game:
    """Main game object."""

    def __init__(self, render_processor: esper.Processor, config: Optional[dict]=None) -> None:
        self.render_processor = render_processor
        self.config: dict = config or {}
        self.game_over: bool = False
        self.world: esper.World = esper.World()
        self.state: GameState = GameState.PLAYING

        RefreshMapEvent.handle(self.on_refresh_map)

        self.world.add_processor(InputProcessor(), priority=Priority.input)
        self.world.add_processor(AIProcessor(), priority=Priority.ai)
        # TODO: anything else that can change whether time passed
        self.world.add_processor(TimeProcessor(), priority=Priority.time)
        self.world.add_processor(MovementProcessor(), priority=Priority.movement)
        self.world.add_processor(self.render_processor, priority=Priority.render)

        current_map = ClassicMap(self.config['map']['max_tiles_w'],
                                 self.config['map']['max_tiles_h'],
                                 self.world)
        current_map.create()

        self.make_player(current_map)
        self.make_enemy(current_map, 39, 0xff3333, 200)
        self.make_enemy(current_map, 39, 0x33ff33, 5)
        self.make_enemy(current_map, 39, 0xff33ff, 500)
        self.make_enemy(current_map, 39, 0x33ffff, 110)
        self.make_enemy(current_map, 39, 0x33ffbb, 90)
        self.make_enemy(current_map, 39, 0x33ffdd, 100)

        count = 0
        for cell in current_map:
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
                    Solid(),
                    Position(cell.x, cell.y)
                )

        GameOverEvent.handle(self.shutdown)

    def make_player(self, game_map: Map) -> None:
        """Make a player entity."""
        self.world.create_entity(
            Actor(),
            Solid(),
            HP(10),
            PlayerControlled(),
            Renderable(1, 0xffff33, RenderLayer.PLAYER),
            Position(game_map.start_pos.x, game_map.start_pos.y),
        )

    def make_enemy(self, game_map: Map, tile: int, color: int, speed: int) -> None:
        """Make an enemy entity."""
        self.world.create_entity(
            Actor(),
            Solid(),
            HP(10),
            AISimpleMind(speed),
            Renderable(tile, color, RenderLayer.ENEMY),
            Position(game_map.start_pos.x, game_map.start_pos.y),
        )

    def on_refresh_map(self, _event: EventType) -> None:
        """Handle OnRefreshMapEvent."""
        self.render_processor.process({'time_passed': True})

    def update(self) -> None:
        """Update the game world."""
        self.world.process({'time_passed': False})

    def shutdown(self, event: EventType) -> None:
        """Shut down the game."""
        if event.get('shutdown'):
            print('Shutting down.')
            self.game_over = True
