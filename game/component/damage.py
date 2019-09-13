"""Damage components."""
import dataclasses

import game.component.base
import game.types


@dataclasses.dataclass
class BaseDamageComponent:
    """Base damage component."""

    amount: game.types.Number


@dataclasses.dataclass
class GUTTakeDamageBludgeoning(BaseDamageComponent):
    """Take Bludgeoning damage."""


class ModifierInflictDamageBludgeoning(game.component.base.BaseModifierComponent):
    """Bludgeoning inflict damage modifier."""


class ModifierTakeDamageBludgeoning(game.component.base.BaseModifierComponent):
    """Bludgeoning damage vulnerability/resistance."""


class ImmuneDamageBludgeoning:
    """Entity is immune to Bludgeoning damage."""


@dataclasses.dataclass
class GUTTakeDamagePiercing(BaseDamageComponent):
    """Take Piercing damage."""


class ModifierInflictDamagePiercing(game.component.base.BaseModifierComponent):
    """Piercing inflict damage modifier."""


class ModifierTakeDamagePiercing(game.component.base.BaseModifierComponent):
    """Piercing damage vulnerability/resistance."""


class ImmuneDamagePiercing:
    """Entity is immune to Piercing damage."""


@dataclasses.dataclass
class GUTTakeDamageSlashing(BaseDamageComponent):
    """Take Slashing damage."""


class ModifierInflictDamageSlashing(game.component.base.BaseModifierComponent):
    """Slashing inflict damage modifier."""


class ModifierTakeDamageSlashing(game.component.base.BaseModifierComponent):
    """Slashing damage vulnerability/resistance."""


class ImmuneDamageSlashing:
    """Entity is immune to Slashing damage."""


@dataclasses.dataclass
class GUTTakeDamageElectric(BaseDamageComponent):
    """Take Electric damage."""


class ModifierInflictDamageElectric(game.component.base.BaseModifierComponent):
    """Electric inflict damage modifier."""


class ModifierTakeDamageElectric(game.component.base.BaseModifierComponent):
    """Electric damage vulnerability/resistance."""


class ImmuneDamageElectric:
    """Entity is immune to Electric damage."""
