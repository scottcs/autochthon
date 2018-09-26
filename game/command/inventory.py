"""Inventory command."""
from .base import BaseCommand
from game.component.container import GUTContained
from game.component.descriptive import Name
from game.component.player import Player
from game.component.gamelog import GUTCommandLog
from game.events import (
    ChoiceAcceptedEvent,
    ChoiceFromListEvent,
    ChooseFromListEvent,
    MenuClosedEvent,
)
from game.types import EventType
from gamedata.palette import ItemPalette


class InventoryCommand(BaseCommand):
    """Inventory command."""

    def run(self) -> None:
        """Run the command."""
        for ent, _ in self.world.get_component(Player):
            items_carried = self._get_items_carried(ent)
            if items_carried:
                ChoiceFromListEvent.handle(self._on_choice)
                MenuClosedEvent.handle(self._on_menu_closed)
                ChooseFromListEvent.fire({"header": "Describe what?", "items": items_carried})
            else:
                cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                cmd_log.add("You aren't carrying anything!")

    def _on_choice(self, event: EventType) -> None:
        input_key = self._keys_from_event(event)
        for ent, _ in self.world.get_component(Player):
            for item_ent, components in self.world.get_components(GUTContained, Name):
                contained, name = components
                if contained.by_ent == ent and contained.label == input_key.key:
                    cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                    cmd_log.add("It's ")
                    cmd_log.append(name.generic, ItemPalette.epic)
                    cmd_log.append(".")
                    ChoiceAcceptedEvent.fire()
                    break
