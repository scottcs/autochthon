"""Container components."""
from typing import Any

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

    def __init__(self, equip_type: EquipType = EquipType.none, stackable: bool = False):
        self.equip_type: EquipType = equip_type
        self.stackable: bool = stackable
        self.count: int = 1


class GUTContained:
    """This entity is contained by another entity."""

    def __init__(self, ent: Entity, component_class: Any, slot: int) -> None:
        self.ent: Entity = ent
        self.component_class: Any = component_class
        self.slot: int = slot


class EquipmentSlotHead(Container):
    """Equipment slot intended for the head."""

    def __init__(self, max_slots: int = 1, equip_type: EquipType = EquipType.head) -> None:
        super().__init__("head", max_slots, equip_type)


class EquipmentSlotTorso(Container):
    """Equipment slot intended for the torso."""

    def __init__(self, max_slots: int = 1, equip_type: EquipType = EquipType.torso) -> None:
        super().__init__("torso", max_slots, equip_type)


class EquipmentSlotHand(Container):
    """Equipment slot intended for the hand."""

    def __init__(self, max_slots: int = 2, equip_type: EquipType = EquipType.hand) -> None:
        super().__init__("hand", max_slots, equip_type)


class EquipmentSlotMainHand(Container):
    """Equipment slot intended for the main_hand."""

    def __init__(self, max_slots: int = 1, equip_type: EquipType = EquipType.main_hand) -> None:
        super().__init__("main-hand", max_slots, equip_type)
