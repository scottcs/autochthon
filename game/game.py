"""Main game class."""
import logging
from typing import Optional

import esper

from game.component.actor import Actor
from game.component.ai_simplemind import AISimpleMind
from game.component.hp import HP
from game.component.playercontrolled import PlayerControlled
from game.component.position import Position
from game.component.renderable import Renderable
from game.component.solid import Solid
from game.events import GameOverEvent, RefreshMapEvent
from game.map import ClassicMap, Map
from game.processor.ai import AIProcessor
from game.processor.ai_action import AIActionProcessor
from game.processor.input import InputProcessor
from game.processor.movement import MovementProcessor
from game.processor.player_action import PlayerActionProcessor
from game.types import EventType, RenderLayer, Priority, ProcessGroup, GameState
from game.utils.time import GameTime
from game.world import World
from gamedata.palette import Palette

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Game:
    """Main game object."""

    def __init__(self, render_processor: esper.Processor, config: Optional[dict]=None) -> None:
        self.render_processor = render_processor
        self.input_processor = InputProcessor()
        self.config: dict = config or {}
        self.game_over: bool = False
        self.world: World = World()
        self.state: GameState = GameState.PLAYING

        RefreshMapEvent.handle(self.on_refresh_map)

        self.world.add_processor(self.input_processor, priority=Priority.input,
                                 group=ProcessGroup.player)
        self.world.add_processor(PlayerActionProcessor(), priority=Priority.player_action,
                                 group=ProcessGroup.player)
        self.world.add_processor(AIProcessor(), priority=Priority.ai)
        self.world.add_processor(AIActionProcessor(), priority=Priority.ai_action)
        self.world.add_processor(MovementProcessor(), priority=Priority.movement)
        self.world.add_processor(self.render_processor, priority=Priority.render,
                                 group=ProcessGroup.post_turn)

        current_map = ClassicMap(self.config['map']['max_tiles_w'],
                                 self.config['map']['max_tiles_h'],
                                 self.world)
        current_map.create()

        self.make_player(current_map)
        self.make_enemy(current_map, 39, Palette.red, 200)
        self.make_enemy(current_map, 39, Palette.purple, 500)
        self.make_enemy(current_map, 39, Palette.orange, 110)
        self.make_enemy(current_map, 39, Palette.cyan, 90)
        self.make_enemy(current_map, 39, Palette.cyan, 100)

        count = 0
        for cell in current_map:
            count += 1
            if cell.transparent:
                # floor
                self.world.create_entity(
                    Renderable(220, Palette.dark_grey, RenderLayer.FLOOR),
                    Position(cell.x, cell.y)
                )
            else:
                # wall
                self.world.create_entity(
                    Renderable(234, Palette.brown, RenderLayer.WALL),
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
            Renderable(1, Palette.yellow, RenderLayer.PLAYER),
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

    def _actors_have_time_left(self) -> bool:
        for ent, actor in self.world.get_component(Actor):
            log.debug(f'E: {ent}   A:{actor}')
            if actor.time_units > 0:
                return True
        return False

    def _get_player_time_units(self) -> GameTime:
        units = GameTime(0)
        for ent, components in self.world.get_components(Actor, PlayerControlled):
            units += components[0].time_units
        return units

    def _non_player_time_units_available(self) -> bool:
        for ent, actor in self.world.get_component(Actor):
            if self.world.has_component(ent, PlayerControlled):
                continue
            if actor.time_units > 0:
                return True
        return False

    def _give_everyone_time_units(self) -> None:
        for ent, actor in self.world.get_component(Actor):
            actor.time_units += actor.rate

    def update(self) -> None:
        """Update the game world."""
        if self._get_player_time_units() >= 0:
            if self.input_processor.input_queue:
                self.world.process_group(ProcessGroup.player)
                self.world.process_group(ProcessGroup.turn)
        else:
            self._give_everyone_time_units()
        while self._non_player_time_units_available():
            self.world.process_group(ProcessGroup.turn)
        self.world.process_group(ProcessGroup.post_turn)

    def shutdown(self, event: EventType) -> None:
        """Shut down the game."""
        if event.get('shutdown'):
            log.info('Shutting down.')
            self.game_over = True
