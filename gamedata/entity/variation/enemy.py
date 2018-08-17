"""Enemy variations."""
import random

from game.component.ai import AISimpleMind
from game.component.attack import AttackDeflectModifier, AttackDodgeModifier
from game.component.attribute import HP
from game.component.descriptive import Name
from game.component.movement import MoveCostModifier
from game.component.render import Renderable
from game.types import Entity
from game.world import World
from gamedata.palette import Palette


def crab(world: World, ent: Entity) -> None:
    """Crab"""
    world.add_component(ent, AISimpleMind())
    world.add_component(ent, HP(20))
    world.add_component(ent, MoveCostModifier(factor=random.choice([-0.1, 0.0, 0.1])))
    world.add_component(ent, AttackDeflectModifier(factor=0.65))
    world.add_component(ent, AttackDodgeModifier(factor=0.30))
    name = world.get_or_add_component(ent, Name)
    name.first = 'a crab'
    render: Renderable = world.get_or_add_component(ent, Renderable)
    render.tile_id = 39
    render.tint = Palette.orange
