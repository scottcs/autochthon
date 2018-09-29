"""Inventory command."""
from .base import BaseCommand
from .drop import DropCommand
from .equip import EquipCommand
from game.component.container import GUTContained
from game.component.descriptive import Name
from game.component.player import Player
from game.component.gamelog import GUTCommandLog
from game.core.world import World
from game.events import (
    ChoiceAcceptedEvent,
    ChoiceDeclinedEvent,
    ChoiceFromListEvent,
    ChooseFromListEvent,
    DescribeEvent,
    MenuClosedEvent,
    SubMenuClosedEvent,
)
from game.types import EventType
from gamedata.palette import ItemPalette


class InventoryCommand(BaseCommand):
    """Inventory command."""

    def __init__(self, world: World) -> None:
        super().__init__(world)
        self.selected = None

    def run(self) -> None:
        """Run the command."""
        for ent, _ in self.world.get_component(Player):
            items_carried = self._get_items_carried(ent)
            if items_carried:
                ChoiceFromListEvent.handle(self.on_choice)
                MenuClosedEvent.handle(self._on_menu_closed)
                ChooseFromListEvent.fire({"header": "Describe what?", "items": items_carried})
            else:
                cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                cmd_log.add("You aren't carrying anything!")

    def on_choice(self, event: EventType) -> None:
        """Callback for ChoiceFromListEvent."""
        input_key = self._keys_from_event(event)
        for ent, _ in self.world.get_component(Player):
            if self.submenu:
                if input_key.key == "d":
                    DropCommand(self.world).on_choice(self.selected)
                    ChoiceAcceptedEvent.fire()
                elif input_key.key == "e":
                    EquipCommand(self.world).on_choice(self.selected)
                    ChoiceAcceptedEvent.fire()
                else:
                    ChoiceDeclinedEvent.fire({"status": "Do what?"})
            else:
                for item_ent, components in self.world.get_components(GUTContained, Name):
                    contained, name = components
                    if contained.by_ent == ent and contained.label == input_key.key:
                        self.selected = event
                        DescribeEvent.fire({
                            "name": (name.generic, ItemPalette.epic),
                            "msg": [
                                ("It's ", None), (name.generic, ItemPalette.epic), (".", None)
                            ],
                            "choices": "d) Drop  e) Equip/Unequip",
                        })
                        self.submenu = True
                        SubMenuClosedEvent.handle(self._on_submenu_closed)
                        break

    def _on_submenu_closed(self, _event: EventType) -> None:
        self.submenu = False
        self.selected = None
        SubMenuClosedEvent.unhandle(self._on_submenu_closed)
