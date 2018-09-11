"""Damage components."""
from game.component.base import BaseModifierComponent
from game.types import Number


class BaseDamageComponent:
    """Base damage component."""

    def __init__(self, amount: Number) -> None:
        self.amount: Number = amount


class GUTTakeDamageBludgeoning(BaseDamageComponent):
    """Take Bludgeoning damage."""


class ModifierInflictDamageBludgeoning(BaseModifierComponent):
    """Bludgeoning inflict damage modifier."""


class ModifierTakeDamageBludgeoning(BaseModifierComponent):
    """Bludgeoning damage vulnerability/resistance."""


class ImmuneDamageBludgeoning:
    """Entity is immune to Bludgeoning damage."""


class GUTTakeDamagePiercing(BaseDamageComponent):
    """Take Piercing damage."""


class ModifierInflictDamagePiercing(BaseModifierComponent):
    """Piercing inflict damage modifier."""


class ModifierTakeDamagePiercing(BaseModifierComponent):
    """Piercing damage vulnerability/resistance."""


class ImmuneDamagePiercing:
    """Entity is immune to Piercing damage."""


class GUTTakeDamageSlashing(BaseDamageComponent):
    """Take Slashing damage."""


class ModifierInflictDamageSlashing(BaseModifierComponent):
    """Slashing inflict damage modifier."""


class ModifierTakeDamageSlashing(BaseModifierComponent):
    """Slashing damage vulnerability/resistance."""


class ImmuneDamageSlashing:
    """Entity is immune to Slashing damage."""


class GUTTakeDamageElectric(BaseDamageComponent):
    """Take Electric damage."""


class ModifierInflictDamageElectric(BaseModifierComponent):
    """Electric inflict damage modifier."""


class ModifierTakeDamageElectric(BaseModifierComponent):
    """Electric damage vulnerability/resistance."""


class ImmuneDamageElectric:
    """Entity is immune to Electric damage."""
