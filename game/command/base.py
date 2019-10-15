"""Base player command."""
import typing

import game.component.container
import game.component.descriptive
import game.events
import game.palette
import game.types
import game.world


class BaseCommand:
    """Base player command."""

    def __init__(self, world: game.world.World) -> None:
        self.world = world
        self.submenu = False

    def run(self) -> None:
        """Run the command."""
        raise NotImplementedError("Must implement in child class.")

    def _get_items_carried(
        self, ent: game.types.Entity
    ) -> typing.Dict[str, typing.List[typing.Any]]:
        items_carried: typing.Dict[str, typing.List[typing.Any]] = {
            "equipped": [],
            "unequipped": [],
        }
        for item_ent, components in self.world.get_components(
            game.component.container.TMPContained,
            game.component.descriptive.Name,
            game.component.container.Containable,
        ):
            contained, name, containable = components
            if contained.by_ent == ent:
                if containable.equipped:
                    item_list = items_carried["equipped"]
                else:
                    item_list = items_carried["unequipped"]
                item_list.append(
                    (
                        containable.equip_type.name,
                        contained.label,
                        name.generic,
                        game.palette.Item.rare,
                    )
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

    def on_choice(self, event: game.types.Event) -> None:
        """Callback for ChoiceFromList event."""
        # Implement in child class if needed.
        pass

    def _on_menu_closed(self, _event: game.types.Event) -> None:
        game.events.ChoiceFromList.unhandle(self.on_choice)
        game.events.MenuClosed.unhandle(self._on_menu_closed)
