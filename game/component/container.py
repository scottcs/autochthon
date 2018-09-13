"""Container components."""
from __future__ import annotations
from typing import Any, Optional

from game.types import Entity, EquipType


class Container:
    """This entity can contain Containable entities."""

    def __init__(
        self, name: str, max_slots: int = 0, equip_type: EquipType = EquipType.any
    ) -> None:
        self.name: str = name
        self.max_slots: int = max_slots
        self.equip_type: EquipType = equip_type


class Containable:
    """This entity can be contained by a Container entity."""

    def __init__(self, equip_type: EquipType = EquipType.none, stackable: bool = False) -> None:
        self.equip_type: EquipType = equip_type
        self.stackable: bool = stackable
        self.count: int = 1


class GUTContained:
    """This entity is contained by another entity."""

    slot_labels = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    def __init__(self, ent: Entity, component_class: Any, slot: int) -> None:
        self.by_ent: Entity = ent
        self.component_class: Any = component_class
        self.slot: int = slot

    @property
    def label(self) -> str:
        """Label of the slot."""
        return self.slot_labels[self.slot]

    @classmethod
    def slot_for_label(cls, label: str) -> int:
        """Get the slot from the label."""
        return cls.slot_labels.index(label)


class GUTContainerTransfer:
    """Remove or insert a Containable entity out of or into a Container."""

    def __init__(self, to_ent: Optional[Entity]=None) -> None:
        # If to_ent is None, assume it's to the floor
        self.to_ent: Optional[Entity] = to_ent
