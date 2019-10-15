"""Container components."""
from __future__ import annotations

import dataclasses
import typing

import game.types


@dataclasses.dataclass
class Container:
    """This entity can contain Containable entities."""

    name: str
    max_slots: int = 0
    equip_type: game.types.Equip = game.types.Equip.any


@dataclasses.dataclass
class Containable:
    """This entity can be contained by a Container entity."""

    equip_type: game.types.Equip = game.types.Equip.none
    stackable: bool = False
    count: int = dataclasses.field(init=False)
    equipped: bool = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.count = 1
        self.equipped = False


@dataclasses.dataclass
class TMPContained:
    """This entity is contained by another entity."""

    by_ent: game.types.Entity
    component_class: typing.Any
    slot: int
    slot_labels: typing.Sequence[
        str
    ] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    @property
    def label(self) -> str:
        """Label of the slot."""
        return self.slot_labels[self.slot]

    def slot_for_label(self, label: str) -> int:
        """Get the slot from the label."""
        return self.slot_labels.index(label)


@dataclasses.dataclass
class TMPTransfer:
    """Remove or insert a Containable entity out of or into a Container.

    If to_ent is None, assume it's to the floor
    """

    to_ent: typing.Optional[game.types.Entity] = None


class Item:
    """An Item."""


class Equipment:
    """Equipment slots."""

    def __init__(
        self,
        head_name="head",
        head_max=1,
        face_name="face",
        face_max=1,
        neck_name="neck",
        neck_max=1,
        shoulder_name="shoulders",
        shoulder_max=1,
        back_name="back",
        back_max=1,
        torso_name="torso",
        torso_max=1,
        waist_name="waist",
        waist_max=1,
        tail_name="tail",
        tail_max=0,
        wrist_name="wrists",
        wrist_max=2,
        hand_name="hands",
        hand_max=1,
        finger_name="fingers",
        finger_max=2,
        leg_name="legs",
        leg_max=1,
        foot_name="feet",
        foot_max=1,
        implant_name="implant",
        implant_max=3,
        shield_name="shield",
        shield_max=1,
        melee_name="melee",
        melee_max=1,
        ranged_name="ranged",
        ranged_max=1,
    ) -> None:
        self.slots = {
            game.types.Equip.head: {"name": head_name, "max": head_max},
            game.types.Equip.face: {"name": face_name, "max": face_max},
            game.types.Equip.neck: {"name": neck_name, "max": neck_max},
            game.types.Equip.shoulder: {"name": shoulder_name, "max": shoulder_max},
            game.types.Equip.back: {"name": back_name, "max": back_max},
            game.types.Equip.torso: {"name": torso_name, "max": torso_max},
            game.types.Equip.waist: {"name": waist_name, "max": waist_max},
            game.types.Equip.tail: {"name": tail_name, "max": tail_max},
            game.types.Equip.wrist: {"name": wrist_name, "max": wrist_max},
            game.types.Equip.hand: {"name": hand_name, "max": hand_max},
            game.types.Equip.finger: {"name": finger_name, "max": finger_max},
            game.types.Equip.leg: {"name": leg_name, "max": leg_max},
            game.types.Equip.foot: {"name": foot_name, "max": foot_max},
            game.types.Equip.implant: {"name": implant_name, "max": implant_max},
            game.types.Equip.shield: {"name": shield_name, "max": shield_max},
            game.types.Equip.melee: {"name": melee_name, "max": melee_max},
            game.types.Equip.ranged: {"name": ranged_name, "max": ranged_max},
        }
