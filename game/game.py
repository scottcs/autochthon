"""Main game class."""
import logging
from pathlib import Path
from typing import Optional
import time

import esper

from game import VERSION
from game.component.attack import (AttackDodgeModifier, ImmuneToDodge, AttackBlockModifier,
                                   ImmuneToBlock, AttackDeflectModifier, ImmuneToDeflect)
from game.dataloader import DataLoader
from game.events import GameOverEvent, PlayerActedEvent, RefreshMapEvent, GameLogEvent
from game.map import ClassicMap
from game.processor.ai import AIProcessor
from game.processor.attack import (AttackHitProcessor, AttackTargetingProcessor,
                                   AttackMissProcessor, AttackDefenseProcessor)
from game.processor.attribute import HPProcessor
from game.processor.damage import DamageBludgeoningMitigationProcessor, DamageBludgeoningProcessor
from game.processor.gamelog import GameLogProcessor
from game.processor.movement import MovementProcessor
from game.processor.player_bump import PlayerBumpProcessor
from game.processor.player_input import PlayerInputProcessor
from game.processor.psychopomps import Psychopomps
from game.processor.time import TimeProcessor
from game.types import EventType, GameState, Priority, ProcessGroup
from game.utils.factory import make_player, make_enemy
from game.utils.language import Verb
from game.world import World
from gamedata.base_engine_values import DODGE_CHANCE, BLOCK_CHANCE, DEFLECT_CHANCE

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def setup_morgue(base_dir: str, player: str) -> logging.Logger:
    """Set up the morgue log."""
    morgue_dir = Path(base_dir) / Path(player)
    morgue_dir.mkdir(parents=True, exist_ok=True)
    log_file = morgue_dir / Path(f'{time.time()}.morgue')
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(message)s'))
    morgue_log = logging.getLogger('morgue')
    morgue_log.setLevel(logging.INFO)
    for old_handler in morgue_log.handlers[:]:
        log.removeHandler(old_handler)
    morgue_log.addHandler(handler)
    morgue_log.propagate = False
    return morgue_log


class Game:
    """Main game object."""

    def __init__(self, render_processor: esper.Processor, config: Optional[dict]=None) -> None:
        self.config: dict = config or {}
        self.game_over: bool = False
        self.player_acted: bool = False
        self.world: World = World()
        self.state: GameState = GameState.PLAYING
        self.morgue = setup_morgue(config['morgue']['directory'], 'UNKNOWN')
        version_string = f'* {config["title"]} version {VERSION}'
        log.info(version_string)
        self.morgue.info(version_string)

        GameLogEvent.handle(self._on_game_log)
        GameOverEvent.handle(self._on_game_over)
        PlayerActedEvent.handle(self._on_player_acted)
        RefreshMapEvent.handle(self._on_refresh_map)

        loader = DataLoader()
        loader.load_all_json()

        dodge_processor = AttackDefenseProcessor(
            Verb('dodges', 'dodged'), AttackDodgeModifier, ImmuneToDodge, DODGE_CHANCE)
        block_processor = AttackDefenseProcessor(
            Verb('blocks', 'blocked'), AttackBlockModifier, ImmuneToBlock, BLOCK_CHANCE)
        deflect_processor = AttackDefenseProcessor(
            Verb('deflects', 'deflected'), AttackDeflectModifier, ImmuneToDeflect, DEFLECT_CHANCE)

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
        self.world.add_processor(AttackMissProcessor(), priority=Priority.attack_miss)
        self.world.add_processor(dodge_processor, priority=Priority.attack_dodge)
        self.world.add_processor(block_processor, priority=Priority.attack_block)
        self.world.add_processor(deflect_processor, priority=Priority.attack_deflect)
        self.world.add_processor(AttackHitProcessor(), priority=Priority.attack_hit)
        self.world.add_processor(DamageBludgeoningMitigationProcessor(), priority=Priority.defense)
        self.world.add_processor(DamageBludgeoningProcessor(), priority=Priority.damage_resolution)
        self.world.add_processor(MovementProcessor(), priority=Priority.movement)
        self.world.add_processor(HPProcessor(), priority=Priority.attributes)
        self.world.add_processor(GameLogProcessor(), priority=Priority.gamelog)
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

        make_player(loader, self.world, current_map.start_pos, ['Orc'])
        make_enemy(loader, self.world, current_map.start_pos, ['Crab'])
        make_enemy(loader, self.world, current_map.start_pos, ['Crab'])
        make_enemy(loader, self.world, current_map.start_pos, ['Crab'])
        make_enemy(loader, self.world, current_map.start_pos, ['Crab'])
        make_enemy(loader, self.world, current_map.start_pos, ['Crab'])

    def _on_refresh_map(self, _event: EventType) -> None:
        self.world.process_group(ProcessGroup.render)

    def _on_player_acted(self, _event: EventType) -> None:
        self.player_acted = True

    def _on_game_log(self, event: EventType) -> None:
        for line in event['lines']:
            self.morgue.info(line.message)
        
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
