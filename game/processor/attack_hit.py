"""Attack hit processor."""
from typing import Any

import esper

from game.component.attack import CurrentTarget
from game.component.base import apply_modifier
from game.component.damage import TakeDamageBludgeoning, ModifierDamageBludgeoning
from game.types import Entity, AttackType


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
