"""Attack components."""
from game.component.base_components import BaseModifierComponent
from game.types import Entity


class BaseAttackComponent:
    """Base attack component class."""
    def __init__(self, target: Entity) -> None:
        self.target: Entity = target


class AttackTargeting(BaseAttackComponent):
    """Attack component for targeting."""
    def __init__(self, target: Entity, x: int, y: int) -> None:
        super().__init__(target)
        self.x: int = x
        self.y: int = y


class AttackHappening(BaseAttackComponent):
    """Attack is happening."""


class AttackHit(BaseAttackComponent):
    """Attack succeeded."""


class AttackHitModifier(BaseModifierComponent):
    """Attack modifier for hit chance."""


class AttackMissed(BaseAttackComponent):
    """Attack failed: attacker missed."""


class AttackDodged(BaseAttackComponent):
    """Attack failed: target dodged."""


class AttackDodgeModifier(BaseModifierComponent):
    """Attack modifier for dodge chance."""


class ImmuneToDodge:
    """Attack cannot be dodged."""


class AttackBlocked(BaseAttackComponent):
    """Attack failed: target blocked."""


class AttackBlockModifier(BaseModifierComponent):
    """Attack modifier for block chance."""


class ImmuneToBlock:
    """Attack cannot be blocked."""


class AttackParried(BaseAttackComponent):
    """Attack failed: target parried."""


class AttackParryModifier(BaseModifierComponent):
    """Attack modifier for parry chance."""


class ImmuneToParry:
    """Attack cannot be parried."""
