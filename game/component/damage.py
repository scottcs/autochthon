"""Damage components."""
import dataclasses

import game.component.base
import game.types


@dataclasses.dataclass
class BaseDamageComponent:
    """Base damage component."""

    amount: game.types.Number


@dataclasses.dataclass
class GUTTakeBludgeoning(BaseDamageComponent):
    """Take Bludgeoning damage."""


class ModifierInflictBludgeoning(game.component.base.BaseModifierComponent):
    """Bludgeoning inflict damage modifier."""


class ModifierTakeBludgeoning(game.component.base.BaseModifierComponent):
    """Bludgeoning damage vulnerability/resistance."""


class ImmuneBludgeoning:
    """Entity is immune to Bludgeoning damage."""


@dataclasses.dataclass
class GUTTakePiercing(BaseDamageComponent):
    """Take Piercing damage."""


class ModifierInflictPiercing(game.component.base.BaseModifierComponent):
    """Piercing inflict damage modifier."""


class ModifierTakePiercing(game.component.base.BaseModifierComponent):
    """Piercing damage vulnerability/resistance."""


class ImmunePiercing:
    """Entity is immune to Piercing damage."""


@dataclasses.dataclass
class GUTTakeSlashing(BaseDamageComponent):
    """Take Slashing damage."""


class ModifierInflictSlashing(game.component.base.BaseModifierComponent):
    """Slashing inflict damage modifier."""


class ModifierTakeSlashing(game.component.base.BaseModifierComponent):
    """Slashing damage vulnerability/resistance."""


class ImmuneDamage:
    """Entity is immune to Slashing damage."""


@dataclasses.dataclass
class GUTTakeElectric(BaseDamageComponent):
    """Take Electric damage."""


class ModifierInflictElectric(game.component.base.BaseModifierComponent):
    """Electric inflict damage modifier."""


class ModifierTakeElectric(game.component.base.BaseModifierComponent):
    """Electric damage vulnerability/resistance."""


class ImmuneElectric:
    """Entity is immune to Electric damage."""
