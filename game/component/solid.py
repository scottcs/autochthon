"""Solid component (can collide with other Solids)."""
from enum import Enum, auto


# TODO: Probably, these should all just be components
#   Like: Destructable, Hurtable, Openable
class SolidFlavor(Enum):
    """Flavors of solid."""
    wall = auto()
    enemy = auto()
    player = auto()
    door = auto()


class Solid:
    """Solid Component."""
    def __init__(self, flavor: SolidFlavor) -> None:
        self.flavor: SolidFlavor = flavor
