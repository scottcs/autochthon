"""Damage components."""
from game.component.base import BaseModifierComponent
from game.types import Number


class BaseDamageComponent:
    """Base damage component."""
    def __init__(self, amount: Number) -> None:
        self.amount: Number = amount


class TakeDamageBludgeoning(BaseDamageComponent):
    """Take Bludgeoning damage."""


class ModifierDamageBludgeoning(BaseModifierComponent):
    """Bludgeoning damage modifier."""


class ResistDamageBludgeoning(BaseModifierComponent):
    """Bludgeoning damage resistance."""


class ImmuneDamageBludgeoning:
    """Entity is immune to Bludgeoning damage."""


class TakeDamagePiercing(BaseDamageComponent):
    """Take Piercing damage."""


class ModifierDamagePiercing(BaseModifierComponent):
    """Piercing damage modifier."""


class ResistDamagePiercing(BaseModifierComponent):
    """Piercing damage resistance."""


class ImmuneDamagePiercing:
    """Entity is immune to Piercing damage."""


class TakeDamageSlashing(BaseDamageComponent):
    """Take Slashing damage."""


class ModifierDamageSlashing(BaseModifierComponent):
    """Slashing damage modifier."""


class ResistDamageSlashing(BaseModifierComponent):
    """Slashing damage resistance."""


class ImmuneDamageSlashing:
    """Entity is immune to Slashing damage."""


class TakeDamageElectric(BaseDamageComponent):
    """Take Electric damage."""


class ModifierDamageElectric(BaseModifierComponent):
    """Electric damage modifier."""


class ResistDamageElectric(BaseModifierComponent):
    """Electric damage resistance."""


class ImmuneDamageElectric:
    """Entity is immune to Electric damage."""
