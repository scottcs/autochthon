"""Attack components."""
import dataclasses
import typing

import game.component.base
import game.types


@dataclasses.dataclass
class GUTCurrentTarget:
    """Component for targeting an entity or location."""

    x: int
    y: int
    attack: game.types.AttackType
    entity: typing.Optional[game.types.Entity] = None


class AttackHitModifier(game.component.base.BaseModifierComponent):
    """Attack modifier for hit chance."""


class AttackDodgeModifier(game.component.base.BaseModifierComponent):
    """Attack modifier for dodge chance."""


@dataclasses.dataclass
class ImmuneToDodge(game.component.base.BaseTemporaryComponent):
    """Attack cannot be dodged."""


class AttackBlockModifier(game.component.base.BaseModifierComponent):
    """Attack modifier for block chance."""


@dataclasses.dataclass
class ImmuneToBlock(game.component.base.BaseTemporaryComponent):
    """Attack cannot be blocked."""


class AttackDeflectModifier(game.component.base.BaseModifierComponent):
    """Attack modifier for chance to deflect incoming attack."""


@dataclasses.dataclass
class ImmuneToDeflect(game.component.base.BaseTemporaryComponent):
    """Attack cannot be deflected."""
