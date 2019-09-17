"""Damage processors."""
import typing

import esper

import game.component.attribute
import game.component.base
import game.component.damage
import game.component.descriptive
import game.component.gamelog
import game.constants.messages.combat
import game.utils.language


class DamageBludgeoningMitigation(esper.Processor):
    """Processor for mitigating Bludgeoning damage."""

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process TakeDamageBludgeoning components."""
        for ent, damage in self.world.get_component(game.component.damage.GUTTakeBludgeoning):
            if self.world.has_component(ent, game.component.damage.ImmuneBludgeoning):
                combat_log = self.world.get_or_add_component(ent, game.component.gamelog.GUTCombat)
                name = self.world.get_or_add_component(
                    ent, game.component.descriptive.Name, f"Entity {ent}"
                )
                combat_log.add(
                    *game.utils.language.msg(
                        self.world.players,
                        (ent,),
                        game.constants.messages.combat.MsgDamageImmune,
                        name.specific,
                        "Bludgeoning",
                    )
                )
                self.world.remove_component(ent, game.component.damage.GUTTakeBludgeoning)
            else:
                mods = []
                for mod in self.world.try_component(
                    ent, game.component.damage.ModifierTakeBludgeoning
                ):
                    mods.append(mod)
                modifier = game.component.base.accumulate_modifiers(*mods)
                full_amount = damage.amount
                damage.amount = (damage.amount + modifier.addend) * (1 + modifier.factor)
                combat_log = self.world.get_or_add_component(ent, game.component.gamelog.GUTCombat)
                name = self.world.get_or_add_component(
                    ent, game.component.descriptive.Name, f"Entity {ent}"
                )
                if damage.amount > full_amount:
                    combat_log.add(
                        *game.utils.language.msg(
                            self.world.players,
                            (ent,),
                            game.constants.messages.combat.MsgDamageVulnerable,
                            name.specific,
                            "Bludgeoning",
                            damage.amount,
                        )
                    )
                elif damage.amount < full_amount:
                    combat_log.add(
                        *game.utils.language.msg(
                            self.world.players,
                            (ent,),
                            game.constants.messages.combat.MsgDamageResist,
                            name.specific,
                            "Bludgeoning",
                            damage.amount,
                        )
                    )
                else:
                    combat_log.add(
                        *game.utils.language.msg(
                            self.world.players,
                            (ent,),
                            game.constants.messages.combat.MsgDamageNormal,
                            name.specific,
                            "Bludgeoning",
                            damage.amount,
                        )
                    )
                if damage.amount <= 0:
                    self.world.remove_component(ent, game.component.damage.GUTTakeBludgeoning)


class DamageBludgeoning(esper.Processor):
    """Processor for applying Bludgeoning damage."""

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process TakeDamageBludgeoning components."""
        for ent, damage in self.world.get_component(game.component.damage.GUTTakeBludgeoning):
            for change_hp in self.world.try_component(ent, game.component.attribute.GUTChangeHP):
                change_hp.amount -= damage.amount
                break
            else:
                self.world.add_component(ent, game.component.attribute.GUTChangeHP(-damage.amount))
            self.world.remove_component(ent, game.component.damage.GUTTakeBludgeoning)
