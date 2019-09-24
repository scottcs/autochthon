"""Main game class."""
import logging
import pathlib
import time
import typing

import appdirs

import game
import game.component.action
import game.component.attack
import game.const.base_engine_values
import game.const.config
import game.const.layout
import game.core.map
import game.core.world
import game.events
import game.processor.ai
import game.processor.attack
import game.processor.attribute
import game.processor.container
import game.processor.damage
import game.processor.gamelog
import game.processor.movement
import game.processor.player_bump
import game.processor.player_input
import game.processor.psychopomps
import game.processor.render
import game.processor.time
import game.types
import game.utils.dataloader
import game.utils.factory
import game.utils.language
import game.utils.random

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def _safe_dir(name: str) -> str:
    return name.lower().replace(" ", "_")


class Game:
    """Main game object."""

    def __init__(self) -> None:
        self.config = game.const.config.DATA
        self.dirs = appdirs.AppDirs(_safe_dir(self.config["title"]), _safe_dir(self.config["org"]))
        self.game_over: bool = False
        self.got_player_input: bool = False
        self.world: game.core.world.World = game.core.world.World()
        self.layout: game.types.Layout = {}
        self.state: game.types.GameState = game.types.GameState.unknown
        self.loader: game.utils.dataloader.DataLoader = game.utils.dataloader.DataLoader()
        self.loader.load_all_json()
        self.morgue: logging.Logger = self._setup_morgue()
        version_string = f'* {self.config["title"]} version {game.VERSION}'
        log.info(version_string)
        self.morgue.info(version_string)

        # TODO: menu state first
        # TODO: allow player to set seed and pass it here
        self.set_state_playing("Test1")

    def _setup_morgue(self) -> logging.Logger:
        """Set up the morgue log."""
        morgue_dir = (
            pathlib.Path(self.dirs.user_log_dir)
            / pathlib.Path(self.config["directories"]["base"])
            / pathlib.Path(self.config["directories"]["morgue"])
            / pathlib.Path(self.config["player"]["name"])
        )
        morgue_dir.mkdir(parents=True, exist_ok=True)
        log_file = morgue_dir / pathlib.Path(f"{time.time()}.morgue")
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

    def set_state_playing(self, layout_name, seed: typing.Optional[str] = None) -> None:
        """Set the game state to playing."""
        self.layout = game.const.layout.DATA[layout_name]

        game.utils.random.RNGCache.init(seed)
        self.state = game.types.GameState.playing

        game.events.GameLog.handle(self._on_game_log)
        game.events.GameOver.handle(self._on_game_over)

        dodge_processor = game.processor.attack.AttackDefense(
            game.utils.language.Verb("dodges", "dodged"),
            game.component.attack.DodgeModifier,
            game.component.attack.ImmuneToDodge,
            game.const.base_engine_values.DODGE_CHANCE,
        )
        block_processor = game.processor.attack.AttackDefense(
            game.utils.language.Verb("blocks", "blocked"),
            game.component.attack.BlockModifier,
            game.component.attack.ImmuneToBlock,
            game.const.base_engine_values.BLOCK_CHANCE,
        )
        deflect_processor = game.processor.attack.AttackDefense(
            game.utils.language.Verb("deflects", "deflected"),
            game.component.attack.DeflectModifier,
            game.component.attack.ImmuneToDeflect,
            game.const.base_engine_values.DEFLECT_CHANCE,
        )

        self.world.add_processor(
            game.processor.player_input.PlayerInput(),
            priority=game.types.Priority.player_input,
            group=game.types.ProcessGroup.player,
        )
        self.world.add_processor(
            game.processor.player_bump.PlayerBump(),
            priority=game.types.Priority.player_bump,
            group=game.types.ProcessGroup.player,
        )
        self.world.add_processor(
            game.processor.time.Turn(),
            priority=game.types.Priority.turn,
            group=game.types.ProcessGroup.time,
        )
        self.world.add_processor(
            game.processor.container.Container(), priority=game.types.Priority.container
        )
        self.world.add_processor(game.processor.ai.AI(), priority=game.types.Priority.ai)
        self.world.add_processor(
            game.processor.movement.Movement(), priority=game.types.Priority.movement
        )
        self.world.add_processor(
            game.processor.attack.AttackTargeting(), priority=game.types.Priority.targeting
        )
        self.world.add_processor(
            game.processor.attack.AttackMiss(), priority=game.types.Priority.attack_miss
        )
        self.world.add_processor(dodge_processor, priority=game.types.Priority.attack_dodge)
        self.world.add_processor(block_processor, priority=game.types.Priority.attack_block)
        self.world.add_processor(deflect_processor, priority=game.types.Priority.attack_deflect)
        self.world.add_processor(
            game.processor.attack.AttackHit(), priority=game.types.Priority.attack_hit
        )
        self.world.add_processor(
            game.processor.damage.DamageBludgeoningMitigation(),
            priority=game.types.Priority.defense,
        )
        self.world.add_processor(
            game.processor.damage.DamageBludgeoning(),
            priority=game.types.Priority.damage_resolution,
        )
        self.world.add_processor(
            game.processor.attribute.HP(), priority=game.types.Priority.attributes
        )
        self.world.add_processor(
            game.processor.psychopomps.Psychopomps(),
            priority=game.types.Priority.psychopomps,
            group=game.types.ProcessGroup.render,
        )
        self.world.add_processor(
            game.processor.gamelog.GameLog(),
            priority=game.types.Priority.gamelog,
            group=game.types.ProcessGroup.gamelog,
        )
        self.world.add_processor(
            game.processor.render.BearLibRender(),
            priority=game.types.Priority.render,
            group=game.types.ProcessGroup.render,
        )

        current_map = game.core.map.ClassicMap(
            self.config["map"]["max_tiles_w"],
            self.config["map"]["max_tiles_h"],
            config=self.layout["map"],
        )
        current_map.create()
        self.world.map = current_map
        self._populate_map()

    def _populate_map(self) -> None:
        player_factory = game.utils.factory.Player(self.loader, self.world)
        enemy_factory = game.utils.factory.Enemy(self.loader, self.world)
        item_factory = game.utils.factory.Item(self.loader, self.world)

        player = player_factory.make(self.layout["player"])
        self.world.add_component(player, game.component.action.TMPMyTurn())
        for enemy in self.layout["enemies"]:
            for _ in range(enemy["count"]):
                enemy_factory.make(enemy["assemblages"])
        for item in self.layout["items"]:
            for _ in range(item["count"]):
                item_factory.make(item["assemblages"])

    def _on_game_log(self, event: game.types.Event) -> None:
        for line in event["lines"]:
            self.morgue.info(line.message)

    def _on_game_over(self, event: game.types.Event) -> None:
        if event.get("shutdown"):
            log.info("Shutting down.")
            self.game_over = True

    def _is_player_turn(self) -> bool:
        for ent in self.world.players:
            if self.world.has_component(ent, game.component.action.TMPMyTurn):
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
        self.world.process_group(game.types.ProcessGroup.time)
        if self._is_player_turn():
            self.world.process_group(game.types.ProcessGroup.player, state=self.state)
        self.world.process_group(game.types.ProcessGroup.default)
        self.world.process_group(game.types.ProcessGroup.gamelog)
        self.world.process_group(game.types.ProcessGroup.render)
