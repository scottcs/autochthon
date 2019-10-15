"""Attack components."""
import dataclasses

import game.component.base
import game.types


@dataclasses.dataclass
class TMPCurrentTarget:
    """Component for targeting an entity or location."""

    x: int
    y: int
    attack: game.types.Attack
    entity: game.types.Entity


class HitModifier(game.component.base.BaseModifierComponent):
    """Attack modifier for hit chance."""


class DodgeModifier(game.component.base.BaseModifierComponent):
    """Attack modifier for dodge chance."""


@dataclasses.dataclass
class ImmuneToDodge(game.component.base.BaseTemporaryComponent):
    """Attack cannot be dodged."""


class BlockModifier(game.component.base.BaseModifierComponent):
    """Attack modifier for block chance."""


@dataclasses.dataclass
class ImmuneToBlock(game.component.base.BaseTemporaryComponent):
    """Attack cannot be blocked."""


class DeflectModifier(game.component.base.BaseModifierComponent):
    """Attack modifier for chance to deflect incoming attack."""


@dataclasses.dataclass
class ImmuneToDeflect(game.component.base.BaseTemporaryComponent):
    """Attack cannot be deflected."""
