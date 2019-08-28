"""Attack components."""
from dataclasses import dataclass
from typing import Optional

from game.component.base import BaseModifierComponent, BaseTemporaryComponent
from game.types import AttackType, Entity


@dataclass
class GUTCurrentTarget:
    """Component for targeting an entity or location."""

    x: int
    y: int
    attack: AttackType
    entity: Optional[Entity] = None


class AttackHitModifier(BaseModifierComponent):
    """Attack modifier for hit chance."""


class AttackDodgeModifier(BaseModifierComponent):
    """Attack modifier for dodge chance."""


@dataclass
class ImmuneToDodge(BaseTemporaryComponent):
    """Attack cannot be dodged."""


class AttackBlockModifier(BaseModifierComponent):
    """Attack modifier for block chance."""


@dataclass
class ImmuneToBlock(BaseTemporaryComponent):
    """Attack cannot be blocked."""


class AttackDeflectModifier(BaseModifierComponent):
    """Attack modifier for chance to deflect incoming attack."""


@dataclass
class ImmuneToDeflect(BaseTemporaryComponent):
    """Attack cannot be deflected."""
