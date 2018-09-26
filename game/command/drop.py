"""Drop item."""
import logging

from .base import BaseCommand
from game.component.container import GUTContained
from game.component.descriptive import Name
from game.component.gamelog import GUTCommandLog
from game.component.movement import Position
from game.component.player import Player
from game.events import (
    ChooseFromListEvent,
    ChoiceFromListEvent,
    ChoiceAcceptedEvent,
    ChoiceDeclinedEvent,
    MenuClosedEvent,
)
from game.types import EventType
from gamedata.palette import MessagePalette

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class DropCommand(BaseCommand):
    """Drop an item."""

    def _command(self) -> None:
        for ent, _ in self.world.get_component(Player):
            pos = self.world.component_for_entity(ent, Position)
            item = self.world.get_item_at_position(pos.x, pos.y)
            if item:
                cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                cmd_log.add(
                    "There is already an item on the ground here!", MessagePalette.negative
                )
                return
            items_carried = self._get_items_carried(ent)
            if items_carried:
                ChoiceFromListEvent.handle(self._on_choice)
                MenuClosedEvent.handle(self._on_menu_closed)
                ChooseFromListEvent.fire(
                    {"header": "Drop what?", "items": items_carried, "multiple": True}
                )
            else:
                cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                cmd_log.add("You have nothing to drop!")

    def _on_choice(self, event: EventType) -> None:
        input_key = self._keys_from_event(event)
        for ent, _ in self.world.get_component(Player):
            for item_ent, components in self.world.get_components(GUTContained, Name):
                contained, name = components
                if contained.by_ent == ent and contained.label == input_key.key:
                    if self.world.drop_item(ent, item_ent):
                        ChoiceAcceptedEvent.fire()
                    else:
                        cmd_log = self.world.get_or_add_component(ent, GUTCommandLog)
                        cmd_log.add("You can't drop that!")
                        ChoiceDeclinedEvent.fire({"status": "You can't drop that!"})
                    break
