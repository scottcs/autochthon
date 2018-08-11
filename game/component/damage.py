"""Damage components."""
from game.types import Entity


class BaseDamageComponent:
    """Base damage component."""
    def __init__(self, target: Entity, amount: int) -> None:
        self.target: Entity = target
        self.amount: int = amount


class DoDamageBludgeoning(BaseDamageComponent):
    """Do bludgeoning damage."""


class TakeDamageBludgeoning(BaseDamageComponent):
    """Take bludgeoning damage."""


class ImmuneToBludgeoningDamage:
    """Entity is immune to bludgeoning damage."""


class DoDamagePiercing(BaseDamageComponent):
    """Do piercing damage."""


class TakeDamagePiercing(BaseDamageComponent):
    """Take piercing damage."""


class ImmuneToPiercingDamage:
    """Entity is immune to piercing damage."""


class DoDamageSlashing(BaseDamageComponent):
    """Do slashing damage."""


class TakeDamageSlashing(BaseDamageComponent):
    """Take slashing damage."""


class ImmuneToSlashingDamage:
    """Entity is immune to slashing damage."""


class DoDamageElectric(BaseDamageComponent):
    """Do electric damage."""


class TakeDamageElectric(BaseDamageComponent):
    """Take electric damage."""


class ImmuneToElectricDamage:
    """Entity is immune to electric damage."""
