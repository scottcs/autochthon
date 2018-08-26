"""Damage processors."""
from typing import Any

import esper

from game.component.attribute import GUTChangeHP
from game.component.base import accumulate_modifiers
from game.component.damage import (GUTTakeDamageBludgeoning, ModifierTakeDamageBludgeoning,
                                   ImmuneDamageBludgeoning)
from game.component.descriptive import Name
from game.component.gamelog import GUTCombatLog
from game.utils.language import msg
from gamedata.messages.combat import (MsgDamageImmune, MsgDamageResist, MsgDamageVulnerable,
                                      MsgDamageNormal)


class DamageBludgeoningMitigationProcessor(esper.Processor):
    """Processor for mitigating Bludgeoning damage."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process TakeDamageBludgeoning components."""
        for ent, damage in self.world.get_component(GUTTakeDamageBludgeoning):
            if self.world.has_component(ent, ImmuneDamageBludgeoning):
                combat_log = self.world.get_or_add_component(ent, GUTCombatLog)
                name = self.world.get_or_add_component(ent, Name, f'Entity {ent}')
                combat_log.add(*msg(self.world.players, (ent,), MsgDamageImmune,
                                    name.specific, 'Bludgeoning'))
                self.world.remove_component(ent, GUTTakeDamageBludgeoning)
            else:
                mods = []
                for mod in self.world.try_component(ent, ModifierTakeDamageBludgeoning):
                    mods.append(mod)
                modifier = accumulate_modifiers(*mods)
                full_amount = damage.amount
                damage.amount = (damage.amount + modifier.addend) * (1 + modifier.factor)
                combat_log = self.world.get_or_add_component(ent, GUTCombatLog)
                name = self.world.get_or_add_component(ent, Name, f'Entity {ent}')
                if damage.amount > full_amount:
                    combat_log.add(*msg(self.world.players, (ent,), MsgDamageVulnerable,
                                        name.specific, 'Bludgeoning', damage.amount))
                elif damage.amount < full_amount:
                    combat_log.add(*msg(self.world.players, (ent,), MsgDamageResist,
                                        name.specific, 'Bludgeoning', damage.amount))
                else:
                    combat_log.add(*msg(self.world.players, (ent,), MsgDamageNormal,
                                        name.specific, 'Bludgeoning', damage.amount))
                if damage.amount <= 0:
                    self.world.remove_component(ent, GUTTakeDamageBludgeoning)


class DamageBludgeoningProcessor(esper.Processor):
    """Processor for applying Bludgeoning damage."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process TakeDamageBludgeoning components."""
        for ent, damage in self.world.get_component(GUTTakeDamageBludgeoning):
            for change_hp in self.world.try_component(ent, GUTChangeHP):
                change_hp.amount -= damage.amount
                break
            else:
                self.world.add_component(ent, GUTChangeHP(-damage.amount))
            self.world.remove_component(ent, GUTTakeDamageBludgeoning)
