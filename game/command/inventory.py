"""Inventory command."""
import game.command.base
import game.command.drop
import game.command.equip
import game.component.container
import game.component.descriptive
import game.component.gamelog
import game.component.player
import game.const.palette
import game.core.world
import game.events
import game.types


class Inventory(game.command.base.BaseCommand):
    """Inventory command."""

    def __init__(self, world: game.core.world.World) -> None:
        super().__init__(world)
        self.selected: game.types.EventType = {}

    def run(self) -> None:
        """Run the command."""
        for ent, _ in self.world.get_component(game.component.player.Player):
            items_carried = self._get_items_carried(ent)
            if items_carried:
                game.events.ChoiceFromList.handle(self.on_choice)
                game.events.MenuClosed.handle(self._on_menu_closed)
                game.events.ChooseFromList.fire(
                    {"header": "Describe what?", "items": items_carried}
                )
            else:
                cmd_log = self.world.get_or_add_component(ent, game.component.gamelog.GUTCommand)
                cmd_log.add("You aren't carrying anything!")

    def on_choice(self, event: game.types.EventType) -> None:
        """Callback for ChoiceFromList event."""
        input_key = event["char"]
        for ent, _ in self.world.get_component(game.component.player.Player):
            if self.submenu:
                if input_key.key == "d":
                    game.command.drop.Drop(self.world).on_choice(self.selected)
                    game.events.ChoiceAccepted.fire()
                elif input_key.key == "e":
                    game.command.equip.Equip(self.world).on_choice(self.selected)
                    game.events.ChoiceAccepted.fire()
                else:
                    game.events.ChoiceDeclined.fire({"substatus": "Do what?"})
            else:
                for item_ent, components in self.world.get_components(
                    game.component.container.GUTContained, game.component.descriptive.Name
                ):
                    contained, name = components
                    if contained.by_ent == ent and contained.label == input_key.key:
                        self.selected = event
                        game.events.Describe.fire(
                            {
                                "name": (name.generic, game.const.palette.Item.epic),
                                "msg": [
                                    ("It's ", None),
                                    (name.generic, game.const.palette.Item.epic),
                                    (".", None),
                                ],
                                "choices": "d) Drop  e) Equip/Unequip",
                            }
                        )
                        self.submenu = True
                        game.events.SubMenuClosed.handle(self._on_submenu_closed)
                        break

    def _on_submenu_closed(self, _event: game.types.EventType) -> None:
        self.submenu = False
        self.selected = {}
        game.events.SubMenuClosed.unhandle(self._on_submenu_closed)
