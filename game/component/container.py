"""Container components."""
from __future__ import annotations
from typing import Any

from game.types import Entity, EquipType


class Container:
    """This entity can contain Containable entities."""

    # To facilitate iterating over all container components on an entity
    container_types: set = set()

    def __init__(
        self, name: str, insert_msg: str, max_slots: int = 0, equip_type: EquipType = EquipType.any
    ) -> None:
        self.name: str = name
        self.insert_msg: str = insert_msg
        self.max_slots: int = max_slots
        self.equip_type: EquipType = equip_type
        self.container_types.add(self.__class__)


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


class GUTContainerInsert:
    """Insert a Containable entity into a container."""

    def __init__(self, container_ent: Entity) -> None:
        self.container_ent = container_ent


class GUTContainerRemove:
    """Remove a Containable entity from a container."""

    def __init__(self, container_ent: Entity) -> None:
        self.container_ent = container_ent


class EquipmentSlotHead(Container):
    """Equipment slot intended for the head."""

    def __init__(self, max_slots: int = 1, equip_type: EquipType = EquipType.head) -> None:
        super().__init__("head", "you put on", max_slots, equip_type)


class EquipmentSlotTorso(Container):
    """Equipment slot intended for the torso."""

    def __init__(self, max_slots: int = 1, equip_type: EquipType = EquipType.torso) -> None:
        super().__init__("torso", "you put on", max_slots, equip_type)


class EquipmentSlotHand(Container):
    """Equipment slot intended for the hand."""

    def __init__(self, max_slots: int = 2, equip_type: EquipType = EquipType.hand) -> None:
        super().__init__("hand", "you put on", max_slots, equip_type)


class EquipmentSlotMainHand(Container):
    """Equipment slot intended for the main_hand."""

    def __init__(self, max_slots: int = 1, equip_type: EquipType = EquipType.main_hand) -> None:
        super().__init__("main-hand", "you wield", max_slots, equip_type)
