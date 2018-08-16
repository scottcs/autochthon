"""Player assemblages."""
from game.component.action import Actor
from game.component.attack import (ImmuneToDeflect, AttackCostModifier, AttackHitModifier,
                                   ImmuneToBlock, ImmuneToDodge)
from game.component.attribute import HP
from game.component.damage import ModifierInflictDamageBludgeoning
from game.component.descriptive import Name
from game.component.movement import Position
from game.component.player import PlayerControlled
from game.component.render import Renderable
from game.component.status import Solid
from gamedata.entity.assemblage import schema
from game.types import RenderLayer
from gamedata.palette import Palette

Player = (
    schema(Actor),
    schema(AttackCostModifier, factor=-0.1),
    schema(AttackHitModifier, factor=0.2),
    schema(HP, 10),
    schema(ImmuneToBlock, temporary=True),
    schema(ImmuneToDeflect, temporary=True),
    schema(ImmuneToDodge, temporary=True),
    schema(ModifierInflictDamageBludgeoning, 5),
    schema(Name, 'Player'),
    schema(PlayerControlled),
    schema(Position),
    schema(Renderable, 1, Palette.yellow, RenderLayer.PLAYER),
    schema(Solid),
)

