"""Attack processors."""
import typing

import esper

import game.component.action
import game.component.attack
import game.component.base
import game.component.damage
import game.component.descriptive
import game.component.gamelog
import game.const.base_engine_values
import game.const.messages.combat
import game.types
import game.utils.language
import game.utils.random


class AttackTargeting(esper.Processor):
    """Attack targeting processor."""

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process AttackTargeting components."""
        for ent, components in self.world.get_components(
            game.component.action.Actor,
            game.component.attack.TMPCurrentTarget,
            game.component.action.TMPMyTurn,
        ):
            actor, target = components[:2]
            if not self.still_can_target(ent, target):
                self.world.actor_takes_turn(ent, game.component.attack.TMPCurrentTarget)
                continue
            combat_log = self.world.get_or_add_component(ent, game.component.gamelog.TMPCombat)
            aggressor_name = self.world.get_or_add_component(
                ent, game.component.descriptive.Name, f"Entity {ent}"
            )
            defender_name = self.world.get_or_add_component(
                target.entity, game.component.descriptive.Name, f"Entity {target.entity}"
            )
            combat_log.add(
                *game.utils.language.msg(
                    self.world.players,
                    (ent, target.entity),
                    game.const.messages.combat.Attack,
                    aggressor_name.specific,
                    defender_name.specific,
                    target.attack,
                )
            )
            self.world.add_component(ent, combat_log)
            self.world.actor_takes_turn(ent)

    def still_can_target(
        self, _ent: game.types.Entity, target: game.component.attack.TMPCurrentTarget
    ) -> bool:
        """Determine if target is still valid."""
        if target.attack == game.types.Attack.melee:
            for existing in self.world.entities_at_position(target.x, target.y):
                if existing == target.entity:
                    return True
        return False


class AttackMiss(esper.Processor):
    """Process whether attack missed."""

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process whether attack missed."""
        rng = game.utils.random.RNGCache.get("AttackProcessor")
        for ent, target in self.world.get_component(game.component.attack.TMPCurrentTarget):
            if target.attack == game.types.Attack.melee:
                mods = []
                for mod in self.world.try_component(ent, game.component.attack.HitModifier):
                    mods.append(mod)
                # TODO: Gather other modifiers
                modifier = game.component.base.accumulate_modifiers(*mods)
                chance = game.const.base_engine_values.HIT_CHANCE + modifier.factor
                combat_log = self.world.get_or_add_component(ent, game.component.gamelog.TMPCombat)
                if not rng.percent(chance):
                    name = self.world.get_or_add_component(
                        ent, game.component.descriptive.Name, f"Entity {ent}"
                    )
                    combat_log.add(
                        *game.utils.language.msg(
                            self.world.players,
                            (ent, target.entity),
                            game.const.messages.combat.Miss,
                            name.specific,
                        )
                    )
                    self.world.remove_component(ent, game.component.attack.TMPCurrentTarget)


class AttackDefense(esper.Processor):
    """Process whether attack was defended."""

    def __init__(
        self,
        verb: game.utils.language.Verb,
        modifier_component_class: typing.Any,
        immunity_component_class: typing.Any,
        base_chance: game.types.Number,
    ) -> None:
        self.verb: game.utils.language.Verb = verb
        self.modifier_component_class: typing.Any = modifier_component_class
        self.immunity_component_class: typing.Any = immunity_component_class
        self.base_chance: game.types.Number = base_chance

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process whether an attack was defended."""
        rng = game.utils.random.RNGCache.get("AttackProcessor")
        for ent, target in self.world.get_component(game.component.attack.TMPCurrentTarget):
            if self.world.has_component(ent, self.immunity_component_class):
                # This attack cannot be thwarted by this defense
                immune = self.world.component_for_entity(ent, self.immunity_component_class)
                if immune.temporary:
                    self.world.remove_component(ent, self.immunity_component_class)
                name = self.world.get_or_add_component(
                    ent, game.component.descriptive.Name, f"Entity {ent}"
                )
                combat_log = self.world.get_or_add_component(ent, game.component.gamelog.TMPCombat)
                combat_log.add(
                    *game.utils.language.msg(
                        self.world.players,
                        (ent, target.entity),
                        game.const.messages.combat.AttackImmune,
                        name.specific,
                        self.verb.past,
                    )
                )
                continue
            if target.attack == game.types.Attack.melee:
                mods = []
                for mod in self.world.try_component(target.entity, self.modifier_component_class):
                    mods.append(mod)
                # TODO: Gather other modifiers
                modifier = game.component.base.accumulate_modifiers(*mods)
                chance = self.base_chance + modifier.factor
                if chance > 0:
                    if not rng.percent(chance):
                        combat_log = self.world.get_or_add_component(
                            ent, game.component.gamelog.TMPCombat
                        )
                        name = self.world.get_or_add_component(
                            target.entity,
                            game.component.descriptive.Name,
                            f"Entity {target.entity}",
                        )
                        combat_log.add(
                            *game.utils.language.msg(
                                self.world.players,
                                (target.entity, ent),
                                game.const.messages.combat.Defend,
                                name.specific,
                                self.verb.present,
                            )
                        )
                        # TODO: Add success comp for other processors (DeflectSuccess -> Disarm)
                        self.world.remove_component(ent, game.component.attack.TMPCurrentTarget)


class AttackHit(esper.Processor):
    """Attack happened, nothing stopped it, so generate AttackHit."""

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process AttackHappening."""
        for ent, target in self.world.get_component(game.component.attack.TMPCurrentTarget):
            if target.attack == game.types.Attack.melee:
                self.generate_melee_damage(ent, target)
            # TODO: generate effects here too (knockback, electric arc, etc)
            self.world.remove_component(ent, game.component.attack.TMPCurrentTarget)

    def generate_melee_damage(
        self, ent: game.types.Entity, target: game.component.attack.TMPCurrentTarget
    ) -> None:
        """Generate DoDamage components on attacker."""
        mods = []
        # TODO: check equipment
        # TODO: check attributes
        # TODO: check race
        # TODO: etc
        for mod in self.world.try_component(ent, game.component.damage.ModifierInflictBludgeoning):
            mods.append(mod)
        modifier = game.component.base.accumulate_modifiers(*mods)
        damage = modifier.addend * (1 + modifier.factor)
        if damage > 0:
            self.world.add_component(
                target.entity, game.component.damage.TMPTakeBludgeoning(damage)
            )
