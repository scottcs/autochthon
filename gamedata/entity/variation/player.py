"""Player variations."""
from game.component.attack import ImmuneToDeflect
from game.component.attribute import HP
from game.types import Entity
from game.world import World


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
