"""Attack components."""
from typing import Optional

from game.component.base import BaseModifierComponent, BaseTemporaryComponent
from game.types import Entity, AttackType


class GUTCurrentTarget:
    """Component for targeting an entity or location."""
    def __init__(self, x: int, y: int, attack: AttackType, entity: Optional[Entity]=None) -> None:
        self.x: int = x
        self.y: int = y
        self.attack = attack
        self.entity: Optional[Entity] = entity


class AttackCostModifier(BaseModifierComponent):
    """Attack cost modifier."""


class AttackHitModifier(BaseModifierComponent):
    """Attack modifier for hit chance."""


class AttackDodgeModifier(BaseModifierComponent):
    """Attack modifier for dodge chance."""


class ImmuneToDodge(BaseTemporaryComponent):
    """Attack cannot be dodged."""


class AttackBlockModifier(BaseModifierComponent):
    """Attack modifier for block chance."""


class ImmuneToBlock(BaseTemporaryComponent):
    """Attack cannot be blocked."""


class AttackDeflectModifier(BaseModifierComponent):
    """Attack modifier for chance to deflect incoming attack."""


class ImmuneToDeflect(BaseTemporaryComponent):
    """Attack cannot be deflected."""
