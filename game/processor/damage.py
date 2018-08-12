"""Damage processors."""
from typing import Any

import esper

from game.component.attribute import ChangeHP
from game.component.base import accumulate_modifiers
from game.component.damage import (TakeDamageBludgeoning, ModifierTakeDamageBludgeoning,
                                   ImmuneDamageBludgeoning)
from game.component.gamelog import CombatLog


class DamageBludgeoningMitigationProcessor(esper.Processor):
    """Processor for mitigating Bludgeoning damage."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process TakeDamageBludgeoning components."""
        for ent, damage in self.world.get_component(TakeDamageBludgeoning):
            if self.world.has_component(ent, ImmuneDamageBludgeoning):
                combat_log = self.world.get_or_add_component(ent, CombatLog)
                combat_log.add(f'{ent} was immune to Bludgeoning damage!')
                self.world.remove_component(ent, TakeDamageBludgeoning)
            else:
                mods = []
                for mod in self.world.try_component(ent, ModifierTakeDamageBludgeoning):
                    mods.append(mod)
                modifier = accumulate_modifiers(*mods)
                damage.amount = (damage.amount + modifier.addend) * (1 + modifier.factor)
                combat_log = self.world.get_or_add_component(ent, CombatLog)
                combat_log.add(f'{ent} took {damage.amount} Bludgeoning damage!')
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
