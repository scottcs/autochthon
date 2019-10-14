"""Playing game state."""
import logging
import typing

import game.base_engine_values
import game.command.drop
import game.command.equip
import game.command.inventory
import game.command.pickup
import game.command.show_log
import game.component.action
import game.component.attack
import game.component.movement
import game.component.player
import game.data
import game.events
import game.factory
import game.input
import game.level_layout
import game.map
import game.processor.ai
import game.processor.attack
import game.processor.attribute
import game.processor.container
import game.processor.damage
import game.processor.gamelog
import game.processor.movement
import game.processor.player_bump
import game.processor.psychopomps
import game.processor.render
import game.processor.time
import game.render
import game.state.base
import game.state.gamelog
import game.types
import game.utils.dataloader
import game.utils.language
import game.utils.morgue
import game.utils.random
import game.world

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Playing(game.state.base.BaseState):
    """Playing game state."""

    def __init__(
        self,
        renderer: game.render.BaseRenderer,
        layout_name: str,
        seed: typing.Optional[str] = None,
    ) -> None:
        self.renderer = renderer
        self.layout_name = layout_name
        self.seed = seed
        self.world: game.world.World = game.world.World()
        self.layout: game.types.Layout = {}
        self.morgue = game.utils.morgue.new()

    def _on_enter(self) -> None:
        """Called when this state is entered."""
        self.morgue.info(game.data.VERSION_STRING)
        self.layout = game.level_layout.DATA[self.layout_name]
        game.utils.random.RNGCache.init(self.seed)

        game.events.GameLog.handle(self._on_game_log)
        game.events.GameOver.handle(self._on_game_over)

        self._setup_processors()
        self._setup_map()

    def _on_exit(self):
        """Called when this state is discarded or popped off the stack."""
        self.world.clear_database()
        game.events.GameLog.unhandle(self._on_game_log)
        game.events.GameOver.unhandle(self._on_game_over)

    def _on_pause(self):
        """Called when another state is pushed on top of this one."""
        game.events.GameLog.unhandle(self._on_game_log)
        game.events.GameOver.unhandle(self._on_game_over)

    def _on_resume(self):
        """Called when this state becomes top-most on the stack after having been pushed down."""
        game.events.GameLog.handle(self._on_game_log)
        game.events.GameOver.handle(self._on_game_over)

    def _update(self) -> None:
        """Update iteration."""
        self.world.process()

    def _on_game_log(self, event: game.types.Event) -> None:
        self.morgue.info(str(event["log_component"]))

    def _on_game_over(self, _event: game.types.Event) -> None:
        self.morgue.info("Game Over.")
        log.info("Game Over.")
        game.state.base.Stack.pop_to(self)

    def _setup_processors(self):
        dodge_processor = game.processor.attack.AttackDefense(
            game.utils.language.Verb("dodges", "dodged"),
            game.component.attack.DodgeModifier,
            game.component.attack.ImmuneToDodge,
            game.base_engine_values.DODGE_CHANCE,
        )
        block_processor = game.processor.attack.AttackDefense(
            game.utils.language.Verb("blocks", "blocked"),
            game.component.attack.BlockModifier,
            game.component.attack.ImmuneToBlock,
            game.base_engine_values.BLOCK_CHANCE,
        )
        deflect_processor = game.processor.attack.AttackDefense(
            game.utils.language.Verb("deflects", "deflected"),
            game.component.attack.DeflectModifier,
            game.component.attack.ImmuneToDeflect,
            game.base_engine_values.DEFLECT_CHANCE,
        )

        self.world.add_processor(
            game.processor.player_bump.PlayerBump(), priority=game.types.Priority.player_bump
        )
        self.world.add_processor(game.processor.time.Turn(), priority=game.types.Priority.turn)
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
            game.processor.psychopomps.Psychopomps(), priority=game.types.Priority.psychopomps
        )
        self.world.add_processor(
            game.processor.gamelog.GameLog(), priority=game.types.Priority.gamelog
        )
        self.world.add_processor(
            game.processor.render.Render(self.renderer), priority=game.types.Priority.render
        )

    def _setup_map(self) -> None:
        # TODO: get map type from layout
        current_map = game.map.ClassicMap(
            game.data.config["map"]["max_tiles_w"],
            game.data.config["map"]["max_tiles_h"],
            config=self.layout["map"],
        )
        current_map.create()
        self.world.map = current_map

        player_factory = game.factory.Player(self.world)
        enemy_factory = game.factory.Enemy(self.world)
        item_factory = game.factory.Item(self.world)

        player = player_factory.make(self.layout["player"])
        self.world.add_component(player, game.component.action.TMPMyTurn())
        for enemy in self.layout["enemies"]:
            for _ in range(enemy["count"]):
                enemy_factory.make(enemy["assemblages"])
        for item in self.layout["items"]:
            for _ in range(item["count"]):
                item_factory.make(item["assemblages"])

        position = self.world.component_for_entity(player, game.component.movement.Position)
        player_component = self.world.component_for_entity(player, game.component.player.Player)
        current_map.update_fov(position.x, position.y, radius=player_component.fov)

    def _on_input(self, event: game.types.Event) -> None:
        """Handle an input key."""
        input_key = event["key"]
        if not self._try_bump(input_key):
            if not self._try_menu(input_key):
                if not self._try_command(input_key):
                    # TODO: more?
                    if game.input.GameInterface.match("quit", input_key):
                        # TODO: remove this (quit through menu)
                        game.events.GameOver()

    def _try_bump(self, input_key: game.types.InputKey) -> bool:
        dx = 0
        dy = 0
        wait = game.input.GameCommand.match("wait", input_key)

        if not wait:
            bump_up = game.input.GameMovement.match_any(["nw", "n", "ne"], input_key)
            bump_down = game.input.GameMovement.match_any(["sw", "s", "se"], input_key)
            bump_left = game.input.GameMovement.match_any(["nw", "w", "sw"], input_key)
            bump_right = game.input.GameMovement.match_any(["ne", "e", "se"], input_key)

            if bump_up:
                dy -= 1
            if bump_down:
                dy += 1
            if bump_left:
                dx -= 1
            if bump_right:
                dx += 1

            if not (dx or dy):
                return False

        for ent, _ in self.world.get_component(game.component.player.Player):
            self.world.add_component(ent, game.component.player.TMPPlayerBump(dx, dy))
        return True

    def _try_menu(self, input_key: game.types.InputKey) -> bool:
        handled = False
        if game.input.GameMenu.match("gamelog", input_key):
            game.state.base.Stack.push(game.state.gamelog.GameLog(self.renderer))
            handled = True
        return handled

    def _try_command(self, input_key: game.types.InputKey) -> bool:
        handled = True
        command = game.input.GameCommand.from_input_key(input_key)
        if command is None:
            handled = False
        else:
            try:
                {
                    "pick_up": game.command.pickup.Pickup,
                    "drop": game.command.drop.Drop,
                    "inventory": game.command.inventory.Inventory,
                    "equip": game.command.equip.Equip,
                    "gamelog": game.command.show_log.ShowLog,
                }[command.lower()](self.world).run()
            except KeyError:
                handled = False
        return handled
