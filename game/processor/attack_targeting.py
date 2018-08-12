"""Attack targeting processor."""
from typing import Any

import esper

from game.component.action import Actor, BaseActionCosts
from game.component.attack import CurrentTarget
from game.types import Entity, AttackType
from game.utils.time import GameTime


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

    def get_action_cost(self, ent: Entity) -> GameTime:
        """Get the action cost for attacking."""
        base_costs = self.world.component_for_entity(ent, BaseActionCosts)
        # TODO: any modifiers
        return base_costs.attacking
