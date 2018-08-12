"""Attack processors."""
from typing import Any

import esper

from game.component.action import Actor
from game.component.attack import CurrentTarget, AttackCostModifier
from game.component.base import apply_modifier
from game.component.damage import TakeDamageBludgeoning, ModifierDamageBludgeoning
from game.types import Entity, AttackType
from game.utils.time import MOMENTS_PER_TURN


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
        cost = MOMENTS_PER_TURN
        # TODO: any other modifiers
        for mod in self.world.try_component(ent, AttackCostModifier):
            cost = apply_modifier(cost, mod)
        return cost


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
        # TODO: check equipment
        # TODO: check attributes
        # TODO: check race
        # TODO: etc
        bludgeoning_damage = 0
        for mod in self.world.try_component(ent, ModifierDamageBludgeoning):
            bludgeoning_damage = apply_modifier(bludgeoning_damage, mod)
        if bludgeoning_damage > 0:
            self.world.add_component(target.entity, TakeDamageBludgeoning(bludgeoning_damage))
