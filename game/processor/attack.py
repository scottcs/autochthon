"""Attack processors."""
import logging
import random
from typing import Any

import esper

from game.component.action import Actor
from game.component.attack import (CurrentTarget, AttackCostModifier, AttackHitModifier,
                                   ImmuneToDodge, AttackDodgeModifier)
from game.component.base import accumulate_modifiers
from game.component.damage import TakeDamageBludgeoning, ModifierInflictDamageBludgeoning
from game.types import Entity, AttackType
from gamedata.base_engine_values import ATTACK_COST, HIT_CHANCE, DODGE_CHANCE

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


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
                log.debug(f'You have a {chance * 100}% chance to hit...')
                if random.random() > chance:
                    # Miss
                    log.debug('MISS!')
                    self.world.remove_component(ent, CurrentTarget)
                else:
                    log.debug('HIT!')


class AttackDodgeProcessor(esper.Processor):
    """Process whether attack was dodged."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process whether attack missed."""
        for ent, target in self.world.get_component(CurrentTarget):
            if self.world.has_component(ent, ImmuneToDodge):
                # can't be dodged, so just remove component
                self.world.remove_component(ent, ImmuneToDodge)
                log.debug(f'{ent} Attack is immune to being dodged.')
                continue
            if target.attack == AttackType.melee:
                mods = []
                for mod in self.world.try_component(target.entity, AttackDodgeModifier):
                    mods.append(mod)
                # TODO: Gather other modifiers
                modifier = accumulate_modifiers(*mods)
                chance = DODGE_CHANCE + modifier.factor
                log.debug(f'{target.entity} has a {chance * 100}% chance to dodge...')
                if random.random() > chance:
                    log.debug('NO DODGE!')
                else:
                    log.debug('DODGE!')
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
