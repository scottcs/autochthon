"""Damage processors."""
from typing import Any

import esper

from game.component.attribute import ChangeHP
from game.component.base import apply_modifier
from game.component.damage import (TakeDamageBludgeoning, ResistDamageBludgeoning,
                                   ImmuneDamageBludgeoning)


class DamageBludgeoningMitigationProcessor(esper.Processor):
    """Processor for mitigating Bludgeoning damage."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process TakeDamageBludgeoning components."""
        for ent, damage in self.world.get_component(TakeDamageBludgeoning):
            if self.world.has_component(ent, ImmuneDamageBludgeoning):
                self.world.remove_component(ent, TakeDamageBludgeoning)
            else:
                amount = damage.amount
                for resist in self.world.try_component(ent, ResistDamageBludgeoning):
                    amount = apply_modifier(amount, resist)
                damage.amount = amount
                if damage.amount <= 0:
                    self.world.remove_component(ent, TakeDamageBludgeoning)


class DamageBludgeoningProcessor(esper.Processor):
    """Processor for applying Bludgeoning damage."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process TakeDamageBludgeoning components."""
        for ent, damage in self.world.get_component(TakeDamageBludgeoning):
            for change_hp in self.world.try_component(ent, ChangeHP):
                change_hp.amount -= damage.amount
                break
            else:
                self.world.add_component(ent, ChangeHP(-damage.amount))
            self.world.remove_component(ent, TakeDamageBludgeoning)


