"""Attack processors."""
import random
from typing import Any

import esper

from game.component.action import Actor
from game.component.attack import GUTCurrentTarget, AttackCostModifier, AttackHitModifier
from game.component.base import accumulate_modifiers
from game.component.damage import GUTTakeDamageBludgeoning, ModifierInflictDamageBludgeoning
from game.component.descriptive import Name
from game.component.gamelog import GUTCombatLog
from game.types import Entity, AttackType, Number
from game.utils.language import Verb, msg
from gamedata.base_engine_values import ATTACK_COST, HIT_CHANCE
from gamedata.messages.combat import MsgAttack, MsgMiss, MsgAttackImmune, MsgDefend


class AttackTargetingProcessor(esper.Processor):
    """Attack targeting processor."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process AttackTargeting components."""
        for ent, components in self.world.get_components(Actor, GUTCurrentTarget):
            actor, target = components
            if not self.still_can_target(ent, target):
                self.world.remove_component(ent, GUTCurrentTarget)
                continue
            actor.time_units -= self.get_action_cost(ent)
            combat_log = self.world.get_or_add_component(ent, GUTCombatLog)
            aggressor_name = self.world.get_or_add_component(ent, Name, f'Entity {ent}')
            defender_name = self.world.get_or_add_component(target.entity, Name,
                                                            f'Entity {target.entity}')
            combat_log.add(*msg(self.world.players, (ent, target.entity), MsgAttack,
                                aggressor_name, defender_name, target.attack))
            self.world.add_component(ent, combat_log)

    def still_can_target(self, _ent: Entity, target: GUTCurrentTarget) -> bool:
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
        return int((ATTACK_COST + modifier.addend) * (1 + modifier.factor))


class AttackMissProcessor(esper.Processor):
    """Process whether attack missed."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process whether attack missed."""
        for ent, target in self.world.get_component(GUTCurrentTarget):
            if target.attack == AttackType.melee:
                mods = []
                for mod in self.world.try_component(ent, AttackHitModifier):
                    mods.append(mod)
                # TODO: Gather other modifiers
                modifier = accumulate_modifiers(*mods)
                chance = HIT_CHANCE + modifier.factor
                combat_log = self.world.get_or_add_component(ent, GUTCombatLog)
                if random.random() > chance:
                    name = self.world.get_or_add_component(ent, Name, f'Entity {ent}')
                    combat_log.add(*msg(self.world.players, (ent, target.entity), MsgMiss, name))
                    self.world.remove_component(ent, GUTCurrentTarget)


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
        for ent, target in self.world.get_component(GUTCurrentTarget):
            if self.world.has_component(ent, self.immunity_component_class):
                # This attack cannot be thwarted by this defense
                immune = self.world.component_for_entity(ent, self.immunity_component_class)
                if immune.temporary:
                    self.world.remove_component(ent, self.immunity_component_class)
                name = self.world.get_or_add_component(ent, Name, f'Entity {ent}')
                combat_log = self.world.get_or_add_component(ent, GUTCombatLog)
                combat_log.add(*msg(self.world.players, (ent, target.entity), MsgAttackImmune,
                                    name, self.verb.past))
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
                        combat_log = self.world.get_or_add_component(ent, GUTCombatLog)
                        name = self.world.get_or_add_component(
                            target.entity, Name, f'Entity {target.entity}')
                        combat_log.add(*msg(self.world.players, (target.entity, ent), MsgDefend,
                                            name, self.verb.present))
                        # TODO: Add success comp for other processors (DeflectSuccess -> Disarm)
                        self.world.remove_component(ent, GUTCurrentTarget)


class AttackHitProcessor(esper.Processor):
    """Attack happened, nothing stopped it, so generate AttackHit."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process AttackHappening."""
        for ent, target in self.world.get_component(GUTCurrentTarget):
            if target.attack == AttackType.melee:
                self.generate_melee_damage(ent, target)
            # TODO: generate effects here too (knockback, electric arc, etc)
            self.world.remove_component(ent, GUTCurrentTarget)

    def generate_melee_damage(self, ent: Entity, target: GUTCurrentTarget) -> None:
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
            self.world.add_component(target.entity, GUTTakeDamageBludgeoning(damage))
