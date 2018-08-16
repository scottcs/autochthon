"""Enemy Factory."""
from gamedata.entity.assemblage import schema
from game.component.action import Actor
from game.component.ai import AISimpleMind
from game.component.attack import (AttackDodgeModifier,
                                   ImmuneToDodge, AttackBlockModifier, ImmuneToBlock,
                                   AttackDeflectModifier, ImmuneToDeflect)
from game.component.attribute import HP
from game.component.damage import (ImmuneDamageBludgeoning,
                                   ModifierTakeDamageBludgeoning)
from game.component.descriptive import Name
from game.component.movement import Position, MoveCostModifier
from game.component.render import Renderable
from game.component.status import Solid
from game.types import Entity, RenderLayer
from game.world import World
from gamedata.palette import Palette


Enemy = (
        Position(),
        Solid(),
)
