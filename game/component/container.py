"""Container components."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Sequence

from game.types import Entity, EquipType


@dataclass
class Container:
    """This entity can contain Containable entities."""

    name: str
    max_slots: int = 0
    equip_type: EquipType = EquipType.any


@dataclass
class Containable:
    """This entity can be contained by a Container entity."""

    equip_type: EquipType = EquipType.none
    stackable: bool = False

    def __post__init__(self) -> None:
        self.count: int = 1


@dataclass
class GUTContained:
    """This entity is contained by another entity."""

    by_ent: Entity
    component_class: Any
    slot: int
    slot_labels: Sequence = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    @property
    def label(self) -> str:
        """Label of the slot."""
        return self.slot_labels[self.slot]

    def slot_for_label(self, label: str) -> int:
        """Get the slot from the label."""
        return self.slot_labels.index(label)


@dataclass
class GUTContainerTransfer:
    """Remove or insert a Containable entity out of or into a Container.

    If to_ent is None, assume it's to the floor
    """

    to_ent: Optional[Entity] = None
