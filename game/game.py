"""Main game class."""
import logging
from typing import Optional

import esper

from game.component.action import Actor
from game.component.ai import AISimpleMind
from game.component.attack import AttackCostModifier
from game.component.attribute import HP
from game.component.damage import (ImmuneDamageBludgeoning, ModifierDamageBludgeoning,
                                   ResistDamageBludgeoning)
from game.component.movement import Position, MoveCostModifier
from game.component.player import PlayerControlled
from game.component.render import Renderable
from game.component.status import Solid
from game.events import GameOverEvent, PlayerActedEvent, RefreshMapEvent
from game.map import ClassicMap, Map
from game.processor.ai import AIProcessor
from game.processor.attack import AttackHitProcessor, AttackTargetingProcessor
from game.processor.attribute import HPProcessor
from game.processor.damage import DamageBludgeoningMitigationProcessor, DamageBludgeoningProcessor
from game.processor.movement import MovementProcessor
from game.processor.player_bump import PlayerBumpProcessor
from game.processor.player_input import PlayerInputProcessor
from game.processor.psychopomps import Psychopomps
from game.processor.time import TimeProcessor
from game.types import Entity, EventType, GameState, Priority, ProcessGroup, RenderLayer
from game.world import World
from gamedata.palette import Palette

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Game:
    """Main game object."""

    def __init__(self, render_processor: esper.Processor, config: Optional[dict]=None) -> None:
        self.config: dict = config or {}
        self.game_over: bool = False
        self.player_acted: bool = False
        self.world: World = World()
        self.state: GameState = GameState.PLAYING

        GameOverEvent.handle(self._on_game_over)
        PlayerActedEvent.handle(self._on_player_acted)
        RefreshMapEvent.handle(self._on_refresh_map)

        self.world.add_processor(PlayerInputProcessor(),
                                 priority=Priority.player_input,
                                 group=ProcessGroup.player)
        self.world.add_processor(PlayerBumpProcessor(),
                                 priority=Priority.player_bump,
                                 group=ProcessGroup.player)
        self.world.add_processor(TimeProcessor(),
                                 priority=Priority.time,
                                 group=ProcessGroup.time)
        self.world.add_processor(AIProcessor(), priority=Priority.ai)
        self.world.add_processor(AttackTargetingProcessor(), priority=Priority.targeting)
        self.world.add_processor(AttackHitProcessor(), priority=Priority.attack)
        self.world.add_processor(DamageBludgeoningMitigationProcessor(), priority=Priority.defense)
        self.world.add_processor(DamageBludgeoningProcessor(), priority=Priority.damage_resolution)
        self.world.add_processor(MovementProcessor(), priority=Priority.movement)
        self.world.add_processor(HPProcessor(), priority=Priority.attributes)
        self.world.add_processor(render_processor,
                                 priority=Priority.render,
                                 group=ProcessGroup.render)
        self.world.add_processor(Psychopomps(),
                                 priority=Priority.psychopomps,
                                 group=ProcessGroup.render)

        current_map = ClassicMap(self.config['map']['max_tiles_w'],
                                 self.config['map']['max_tiles_h'],
                                 self.world)
        current_map.create()
        self.world.map = current_map

        self.make_player(current_map)
        self.make_enemy(current_map, 39, Palette.red, 200)
        self.make_enemy(current_map, 39, Palette.purple, 500)
        self.make_enemy(current_map, 39, Palette.orange, 110)
        cyan = self.make_enemy(current_map, 39, Palette.cyan, 90)
        green = self.make_enemy(current_map, 39, Palette.green, 100)
        self.world.add_component(cyan, ResistDamageBludgeoning(factor=0.5))
        self.world.add_component(green, ImmuneDamageBludgeoning())

    def make_player(self, game_map: Map) -> None:
        """Make a player entity."""
        self.world.create_entity(
            Actor(),
            AttackCostModifier(factor=0.9),
            Solid(),
            HP(10),
            ModifierDamageBludgeoning(5),
            PlayerControlled(),
            Renderable(1, Palette.yellow, RenderLayer.PLAYER),
            Position(game_map.start_pos.x, game_map.start_pos.y),
        )

    def make_enemy(self, game_map: Map, tile: int, color: int, speed: int) -> Entity:
        """Make an enemy entity."""
        return self.world.create_entity(
            Actor(-100),
            MoveCostModifier(speed),
            Solid(),
            HP(10),
            AISimpleMind(),
            Renderable(tile, color, RenderLayer.ENEMY),
            Position(game_map.start_pos.x, game_map.start_pos.y),
        )

    def _on_refresh_map(self, _event: EventType) -> None:
        self.world.process_group(ProcessGroup.render)

    def _on_player_acted(self, _event: EventType) -> None:
        self.player_acted = True

    def _on_game_over(self, event: EventType) -> None:
        if event.get('shutdown'):
            log.info('Shutting down.')
            self.game_over = True

    def update(self) -> None:
        """Update the game world."""
        self.player_acted = False
        self.world.process_group(ProcessGroup.player)
        if self.player_acted:
            self.world.process_group(ProcessGroup.time)
        actors_could_act = self.world.any_actors_can_act()
        self.world.process_group(ProcessGroup.default)
        if actors_could_act and not self.world.any_actors_can_act():
            self.world.process_group(ProcessGroup.render)
