"""Container components."""
from __future__ import annotations
from dataclasses import dataclass, field
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
    count: int = field(init=False)
    equipped: bool = field(init=False)

    def __post_init__(self) -> None:
        self.count = 1
        self.equipped = False


@dataclass
class GUTContained:
    """This entity is contained by another entity."""

    by_ent: Entity
    component_class: Any
    slot: int
    slot_labels: Sequence[str] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

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


class Item:
    """An Item."""


class Equipment:
    """Equipment slots."""

    def __init__(
        self,
        head_name: str = "head",
        head_max: int = 1,
        face_name: str = "face",
        face_max: int = 1,
        neck_name: str = "neck",
        neck_max: int = 1,
        shoulder_name: str = "shoulders",
        shoulder_max: int = 1,
        back_name: str = "back",
        back_max: int = 1,
        torso_name: str = "torso",
        torso_max: int = 1,
        waist_name: str = "waist",
        waist_max: int = 1,
        tail_name: str = "tail",
        tail_max: int = 0,
        wrist_name: str = "wrists",
        wrist_max: int = 2,
        hand_name: str = "hands",
        hand_max: int = 1,
        finger_name: str = "fingers",
        finger_max: int = 2,
        leg_name: str = "legs",
        leg_max: int = 1,
        foot_name: str = "feet",
        foot_max: int = 1,
        implant_name: str = "implant",
        implant_max: int = 3,
        shield_name: str = "shield",
        shield_max: int = 1,
        melee_name: str = "melee",
        melee_max: int = 1,
        ranged_name: str = "ranged",
        ranged_max: int = 1,
    ):
        self.slots = {
            EquipType.head: {'name': head_name, 'max': head_max},
            EquipType.face: {'name': face_name, 'max': face_max},
            EquipType.neck: {'name': neck_name, 'max': neck_max},
            EquipType.shoulder: {'name': shoulder_name, 'max': shoulder_max},
            EquipType.back: {'name': back_name, 'max': back_max},
            EquipType.torso: {'name': torso_name, 'max': torso_max},
            EquipType.waist: {'name': waist_name, 'max': waist_max},
            EquipType.tail: {'name': tail_name, 'max': tail_max},
            EquipType.wrist: {'name': wrist_name, 'max': wrist_max},
            EquipType.hand: {'name': hand_name, 'max': hand_max},
            EquipType.finger: {'name': finger_name, 'max': finger_max},
            EquipType.leg: {'name': leg_name, 'max': leg_max},
            EquipType.foot: {'name': foot_name, 'max': foot_max},
            EquipType.implant: {'name': implant_name, 'max': implant_max},
            EquipType.shield: {'name': shield_name, 'max': shield_max},
            EquipType.melee: {'name': melee_name, 'max': melee_max},
            EquipType.ranged: {'name': ranged_name, 'max': ranged_max},
        }
