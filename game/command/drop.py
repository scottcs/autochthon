"""Drop item."""
import logging

import game.command.base
import game.component.container
import game.component.descriptive
import game.component.gamelog
import game.component.movement
import game.component.player
import game.events
import game.types
import gamedata.palette

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Drop(game.command.base.BaseCommand):
    """Drop an item."""

    def run(self) -> None:
        """Run the command."""
        for ent, _ in self.world.get_component(game.component.player.Player):
            pos = self.world.component_for_entity(ent, game.component.movement.Position)
            item = self.world.get_item_at_position(pos.x, pos.y)
            if item:
                cmd_log = self.world.get_or_add_component(ent, game.component.gamelog.GUTCommand)
                cmd_log.add(
                    "There is already an item on the ground here!",
                    gamedata.palette.MessagePalette.negative,
                )
                return
            items_carried = self._get_items_carried(ent)
            if items_carried:
                game.events.ChoiceFromList.handle(self.on_choice)
                game.events.MenuClosed.handle(self._on_menu_closed)
                game.events.ChooseFromList.fire(
                    {"header": "Drop what?", "items": items_carried, "multiple": True}
                )
            else:
                cmd_log = self.world.get_or_add_component(ent, game.component.gamelog.GUTCommand)
                cmd_log.add("You have nothing to drop!")

    def on_choice(self, event: game.types.EventType) -> None:
        """Callback for ChoiceFromList event."""
        input_key = self._keys_from_event(event)
        for ent, _ in self.world.get_component(game.component.player.Player):
            for item_ent, components in self.world.get_components(
                game.component.container.GUTContained, game.component.descriptive.Name
            ):
                contained, name = components
                if contained.by_ent == ent and contained.label == input_key.key:
                    if self.world.drop_item(ent, item_ent):
                        game.events.ChoiceAccepted.fire()
                    else:
                        cmd_log = self.world.get_or_add_component(
                            ent, game.component.gamelog.GUTCommand
                        )
                        cmd_log.add(
                            "There is already an item on the ground here!",
                            gamedata.palette.MessagePalette.negative,
                        )
                        game.events.ChoiceDeclined.fire({"status": "You can't drop that!"})
                    break
