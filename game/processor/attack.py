"""Attack processors."""
import random
from typing import Any

import esper

from game.component.action import Actor
from game.component.attack import CurrentTarget, AttackCostModifier, AttackHitModifier
from game.component.base import accumulate_modifiers
from game.component.damage import TakeDamageBludgeoning, ModifierInflictDamageBludgeoning
from game.component.gamelog import CombatLog
from game.types import Entity, AttackType, Number
from game.utils.language import Verb
from gamedata.base_engine_values import ATTACK_COST, HIT_CHANCE


class AttackTargetingProcessor(esper.Processor):
    """Attack targeting processor."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process AttackTargeting components."""
        for ent, components in self.world.get_components(Actor, CurrentTarget):
            actor, target = components
            if not self.still_can_target(ent, target):
                self.world.remove_component(ent, CurrentTarget)
                continue
            actor.time_units -= self.get_action_cost(ent)
            combat_log = self.world.get_or_add_component(ent, CombatLog)
            combat_log.add(f'{ent} {target.attack} attacks {target.entity}.')
            self.world.add_component(ent, combat_log)

    def still_can_target(self, _ent: Entity, target: CurrentTarget) -> bool:
        """Determine if target is still valid."""
        if target.attack == AttackType.melee:
            existing: Entity = self.world.get_solid_entity_at_position(target.x, target.y)
            if existing != target.entity:
                return False
        return True

    def get_action_cost(self, ent: Entity) -> int:
        """Get the action cost for attacking."""
        mods = []
        for mod in self.world.try_component(ent, AttackCostModifier):
            mods.append(mod)
        # TODO: any other modifiers
        modifier = accumulate_modifiers(*mods)
        return (ATTACK_COST + modifier.addend) * (1 + modifier.factor)


class AttackMissProcessor(esper.Processor):
    """Process whether attack missed."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process whether attack missed."""
        for ent, target in self.world.get_component(CurrentTarget):
            if target.attack == AttackType.melee:
                mods = []
                for mod in self.world.try_component(ent, AttackHitModifier):
                    mods.append(mod)
                # TODO: Gather other modifiers
                modifier = accumulate_modifiers(*mods)
                chance = HIT_CHANCE + modifier.factor
                combat_log = self.world.get_or_add_component(ent, CombatLog)
                if random.random() > chance:
                    combat_log.add(f'{ent} missed!', 0x3333ff)
                    self.world.remove_component(ent, CurrentTarget)


class AttackDefenseProcessor(esper.Processor):
    """Process whether attack was defended."""
    def __init__(self,
                 verb: Verb,
                 modifier_component_class: Any,
                 immunity_component_class: Any,
                 base_chance: Number) -> None:
        super().__init__()
        self.verb: Verb = verb
        self.modifier_component_class: Any = modifier_component_class
        self.immunity_component_class: Any = immunity_component_class
        self.base_chance: Number = base_chance

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process whether an attack was defended."""
        for ent, target in self.world.get_component(CurrentTarget):
            if self.world.has_component(ent, self.immunity_component_class):
                # This attack cannot be thwarted by this defense
                self.world.remove_component(ent, self.immunity_component_class)
                combat_log = self.world.get_or_add_component(ent, CombatLog)
                combat_log.add(f'{ent}\'s attack cannot be {self.verb.past}!')
                continue
            if target.attack == AttackType.melee:
                mods = []
                for mod in self.world.try_component(target.entity, self.modifier_component_class):
                    mods.append(mod)
                # TODO: Gather other modifiers
                modifier = accumulate_modifiers(*mods)
                chance = self.base_chance + modifier.factor
                if chance > 0:
                    if random.random() < chance:
                        combat_log = self.world.get_or_add_component(ent, CombatLog)
                        combat_log.add(f'{target.entity} {self.verb.present}!')
                        # TODO: Add success comp for other processors (DeflectSuccess -> Disarm)
                        self.world.remove_component(ent, CurrentTarget)


class AttackHitProcessor(esper.Processor):
    """Attack happened, nothing stopped it, so generate AttackHit."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process AttackHappening."""
        for ent, target in self.world.get_component(CurrentTarget):
            if target.attack == AttackType.melee:
                self.generate_melee_damage(ent, target)
            # TODO: generate effects here too (knockback, electric arc, etc)
            self.world.remove_component(ent, CurrentTarget)

    def generate_melee_damage(self, ent: Entity, target: CurrentTarget) -> None:
        """Generate DoDamage components on attacker."""
        mods = []
        # TODO: check equipment
        # TODO: check attributes
        # TODO: check race
        # TODO: etc
        for mod in self.world.try_component(ent, ModifierInflictDamageBludgeoning):
            mods.append(mod)
        modifier = accumulate_modifiers(*mods)
        damage = modifier.addend * (1 + modifier.factor)
        if damage > 0:
            self.world.add_component(target.entity, TakeDamageBludgeoning(damage))
