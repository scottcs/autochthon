"""Base player command."""
from typing import NamedTuple, Dict

from game.component.container import GUTContained, Containable
from game.component.descriptive import Name
from game.core.world import World
from game.events import (
    ChoiceFromListEvent,
    MenuClosedEvent,
)
from game.types import Entity, EventType
from game.utils.input import get_key, unpack_modifiers
from gamedata.palette import ItemPalette


class InputKey(NamedTuple):
    """Key and modifiers from an input event."""
    key: str
    modifiers: Dict[str, bool]


class BaseCommand:
    """Base player command."""

    def __init__(self, world: World) -> None:
        self.world: World = world
        self.submenu = False

    def run(self) -> None:
        """Run the command."""
        raise NotImplementedError("Must implement in child class.")

    def _get_items_carried(self, ent: Entity) -> dict:
        items_carried: dict = {"equipped": [], "unequipped": []}
        for item_ent, components in self.world.get_components(GUTContained, Name, Containable):
            contained, name, containable = components
            if contained.by_ent == ent:
                if containable.equipped:
                    item_list = items_carried["equipped"]
                else:
                    item_list = items_carried["unequipped"]
                item_list.append(
                    (containable.equip_type.name, contained.label, name.generic, ItemPalette.rare)
                )
        if items_carried["equipped"]:
            items_carried["equipped"].sort()
        else:
            del items_carried["equipped"]
        if items_carried["unequipped"]:
            items_carried["unequipped"].sort()
        else:
            del items_carried["unequipped"]
        return items_carried

    @staticmethod
    def _keys_from_event(event: EventType) -> InputKey:
        key: str = get_key(event["code"])
        modifiers: Dict[str, bool] = unpack_modifiers(event["modifiers"])
        if modifiers["shift"]:
            key = key.upper()
        return InputKey(key, modifiers)

    def _on_choice(self, event: EventType) -> None:
        # Implement in child class if needed.
        pass

    def _on_menu_closed(self, _event: EventType) -> None:
        ChoiceFromListEvent.unhandle(self._on_choice)
        MenuClosedEvent.unhandle(self._on_menu_closed)
