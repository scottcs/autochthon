"""Main game class."""
import logging
import time
from pathlib import Path
from typing import Optional

import esper

from game import VERSION
from game.component.action import GUTMyTurn
from game.component.attack import (
    AttackBlockModifier,
    AttackDeflectModifier,
    AttackDodgeModifier,
    ImmuneToBlock,
    ImmuneToDeflect,
    ImmuneToDodge,
)
from game.core.map import ClassicMap
from game.core.world import World
from game.events import (
    GameLogEvent,
    GameOverEvent,
    InputEvent,
    RenderEntitiesEvent,
    RenderMapEvent,
    RequestRenderEvent,
)
from game.processor.ai import AIProcessor
from game.processor.attack import (
    AttackDefenseProcessor,
    AttackHitProcessor,
    AttackMissProcessor,
    AttackTargetingProcessor,
)
from game.processor.attribute import HPProcessor
from game.processor.container import ContainerProcessor
from game.processor.damage import DamageBludgeoningMitigationProcessor, DamageBludgeoningProcessor
from game.processor.gamelog import GameLogProcessor
from game.processor.movement import MovementProcessor
from game.processor.player_bump import PlayerBumpProcessor
from game.processor.player_input import PlayerInputProcessor
from game.processor.psychopomps import Psychopomps
from game.processor.time import TurnProcessor
from game.types import EventType, GameState, Priority, ProcessGroup
from game.utils.dataloader import DataLoader
from game.utils.factory import EnemyFactory, ItemFactory, PlayerFactory
from game.utils.language import Verb
from game.utils.random import RNGCache
from gamedata.base_engine_values import BLOCK_CHANCE, DEFLECT_CHANCE, DODGE_CHANCE

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def setup_morgue(base_dir: str, player: str) -> logging.Logger:
    """Set up the morgue log."""
    morgue_dir = Path(base_dir) / Path(player)
    morgue_dir.mkdir(parents=True, exist_ok=True)
    log_file = morgue_dir / Path(f"{time.time()}.morgue")
    handler = logging.FileHandler(str(log_file))
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(message)s"))
    morgue_log = logging.getLogger("morgue")
    morgue_log.setLevel(logging.INFO)
    for old_handler in morgue_log.handlers[:]:
        log.removeHandler(old_handler)
    morgue_log.addHandler(handler)
    morgue_log.propagate = False
    return morgue_log


class Game:
    """Main game object."""

    def __init__(self, render_processor: esper.Processor, config: Optional[dict] = None) -> None:
        self.config: dict = config or {}
        self.game_over: bool = False
        self.got_player_input: bool = False
        self.world: World = World()
        self.state: GameState = GameState.unknown
        self.morgue: logging.Logger = setup_morgue(self.config["morgue"]["directory"], "UNKNOWN")
        version_string = f'* {self.config["title"]} version {VERSION}'
        log.info(version_string)
        self.morgue.info(version_string)

        # TODO: menu state first
        # TODO: allow player to set seed and pass it here
        self.set_state_playing(render_processor)
        InputEvent.handle(self._on_input)

    def set_state_playing(
        self, render_processor: esper.Processor, seed: Optional[str] = None
    ) -> None:
        """Set the game state to playing."""
        RNGCache.init(seed)
        self.state = GameState.playing

        GameLogEvent.handle(self._on_game_log)
        GameOverEvent.handle(self._on_game_over)
        RequestRenderEvent.handle(self._on_refresh_map)

        loader = DataLoader()
        loader.load_all_json()

        dodge_processor = AttackDefenseProcessor(
            Verb("dodges", "dodged"), AttackDodgeModifier, ImmuneToDodge, DODGE_CHANCE
        )
        block_processor = AttackDefenseProcessor(
            Verb("blocks", "blocked"), AttackBlockModifier, ImmuneToBlock, BLOCK_CHANCE
        )
        deflect_processor = AttackDefenseProcessor(
            Verb("deflects", "deflected"), AttackDeflectModifier, ImmuneToDeflect, DEFLECT_CHANCE
        )

        self.world.add_processor(
            PlayerInputProcessor(), priority=Priority.player_input, group=ProcessGroup.player
        )
        self.world.add_processor(
            PlayerBumpProcessor(), priority=Priority.player_bump, group=ProcessGroup.player
        )
        self.world.add_processor(TurnProcessor(), priority=Priority.turn, group=ProcessGroup.time)
        self.world.add_processor(ContainerProcessor(), priority=Priority.container)
        self.world.add_processor(AIProcessor(), priority=Priority.ai)
        self.world.add_processor(MovementProcessor(), priority=Priority.movement)
        self.world.add_processor(AttackTargetingProcessor(), priority=Priority.targeting)
        self.world.add_processor(AttackMissProcessor(), priority=Priority.attack_miss)
        self.world.add_processor(dodge_processor, priority=Priority.attack_dodge)
        self.world.add_processor(block_processor, priority=Priority.attack_block)
        self.world.add_processor(deflect_processor, priority=Priority.attack_deflect)
        self.world.add_processor(AttackHitProcessor(), priority=Priority.attack_hit)
        self.world.add_processor(DamageBludgeoningMitigationProcessor(), priority=Priority.defense)
        self.world.add_processor(DamageBludgeoningProcessor(), priority=Priority.damage_resolution)
        self.world.add_processor(HPProcessor(), priority=Priority.attributes)
        self.world.add_processor(
            Psychopomps(), priority=Priority.psychopomps, group=ProcessGroup.render
        )
        self.world.add_processor(
            render_processor, priority=Priority.render, group=ProcessGroup.render
        )
        self.world.add_processor(
            GameLogProcessor(), priority=Priority.gamelog, group=ProcessGroup.gamelog
        )

        current_map = ClassicMap(
            self.config["map"]["max_tiles_w"], self.config["map"]["max_tiles_h"]
        )
        current_map.create()
        self.world.map = current_map

        player_factory = PlayerFactory(loader, self.world)
        enemy_factory = EnemyFactory(loader, self.world)
        item_factory = ItemFactory(loader, self.world)
        player = player_factory.make(["Orc"])
        self.world.add_component(player, GUTMyTurn())
        for _ in range(200):
            enemy_factory.make(["TrainingDummy"])
        enemy_factory.make(["Crab"])
        enemy_factory.make(["Boar"])
        enemy_factory.make(["OrcShaman"])
        enemy_factory.make(["OrcBrute"])
        enemy_factory.make(["Firefly"])
        enemy_factory.make(["SebastianBenini"])
        for _ in range(100):
            item_factory.make(["Katana"])
            item_factory.make(["Mace"])
            item_factory.make(["PlateArmor"])

    def _on_input(self, _event: EventType) -> None:
        self.got_player_input = True

    @staticmethod
    def _on_refresh_map(event: EventType) -> None:
        RenderMapEvent.fire(event)
        RenderEntitiesEvent.fire({"entities": [], "all": True})

    def _on_game_log(self, event: EventType) -> None:
        for line in event["lines"]:
            self.morgue.info(line.message)

    def _on_game_over(self, event: EventType) -> None:
        if event.get("shutdown"):
            log.info("Shutting down.")
            self.game_over = True

    def _is_player_turn(self) -> bool:
        for ent in self.world.players:
            if self.world.has_component(ent, GUTMyTurn):
                return True
        return False

    def update(self) -> None:
        """Update the game world."""
        # if it's currently nobody's turn:
        #     if initiative queue is empty:
        #         roll initiative for every actor and sort
        #     set lowest initiative actor to MyTurn
        # if it's the player's turn:
        #     if no input:
        #         continue
        #     interpret input
        #     do player turn
        # else:
        #     do actor's turn
        # if map needs render:
        #     render map
        # if entities need render:
        #     render only entities that need it
        self.world.process_group(ProcessGroup.time)
        if self._is_player_turn():
            if self.got_player_input:
                self.got_player_input = False
                self.world.process_group(ProcessGroup.player)
        self.world.process_group(ProcessGroup.default)
        self.world.process_group(ProcessGroup.render)
        self.world.process_group(ProcessGroup.gamelog)
