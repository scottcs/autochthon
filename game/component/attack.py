"""Attack components."""
from typing import Optional

from game.component.base import BaseModifierComponent
from game.types import Entity, AttackType


class CurrentTarget:
    """Component for targeting an entity or location."""
    def __init__(self, x: int, y: int, attack: AttackType, entity: Optional[Entity]=None) -> None:
        self.x: int = x
        self.y: int = y
        self.attack = attack
        self.entity: Optional[Entity] = entity


class AttackHitModifier(BaseModifierComponent):
    """Attack modifier for hit chance."""


class AttackDodgeModifier(BaseModifierComponent):
    """Attack modifier for dodge chance."""


class ImmuneToDodge:
    """Attack cannot be dodged."""


class AttackBlockModifier(BaseModifierComponent):
    """Attack modifier for block chance."""


class ImmuneToBlock:
    """Attack cannot be blocked."""


class AttackParryModifier(BaseModifierComponent):
    """Attack modifier for parry chance."""


class ImmuneToParry:
    """Attack cannot be parried."""
