"""Player factory."""
from . import schema
from game.component.action import Actor
from game.component.attack import (AttackCostModifier, AttackHitModifier, ImmuneToBlock,
                                   ImmuneToDeflect, ImmuneToDodge)
from game.component.attribute import HP
from game.component.damage import ModifierInflictDamageBludgeoning
from game.component.descriptive import Name
from game.component.movement import Position
from game.component.player import PlayerControlled
from game.component.render import Renderable
from game.component.status import Solid
from game.types import Entity, RenderLayer
from game.world import World
from gamedata.palette import Palette


def orc(world: World, ent: Entity) -> None:
    """Orc variation.

    Specify when making the character with:
        world.assemble_ent(Player, orc)
    """
    deflect = world.get_or_add_component(ent, ImmuneToDeflect)
    deflect.temporary = False
    hp = world.component_for_entity(ent, HP)
    hp.max *= 1.1
    hp.value = hp.max


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
