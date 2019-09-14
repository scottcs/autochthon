"""Base player command."""
import typing

import game.component.container
import game.component.descriptive
import game.core.world
import game.events
import game.types
import game.utils.input
import gamedata.palette


class InputKey(typing.NamedTuple):
    """Key and modifiers from an input event."""

    key: str
    modifiers: typing.Dict[str, bool]


class BaseCommand:
    """Base player command."""

    def __init__(self, world: game.core.world.World) -> None:
        self.world: game.core.world.World = world
        self.submenu = False

    def run(self) -> None:
        """Run the command."""
        raise NotImplementedError("Must implement in child class.")

    def _get_items_carried(self, ent: game.types.Entity) -> dict:
        items_carried: dict = {"equipped": [], "unequipped": []}
        for item_ent, components in self.world.get_components(
            game.component.container.GUTContained,
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
                        gamedata.palette.ItemPalette.rare,
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

    @staticmethod
    def _keys_from_event(event: game.types.EventType) -> InputKey:
        key: str = game.utils.input.get_key(event["code"])
        modifiers: typing.Dict[str, bool] = game.utils.input.unpack_modifiers(event["modifiers"])
        if modifiers["shift"]:
            key = key.upper()
        return InputKey(key, modifiers)

    def on_choice(self, event: game.types.EventType) -> None:
        """Callback for ChoiceFromList event."""
        # Implement in child class if needed.
        pass

    def _on_menu_closed(self, _event: game.types.EventType) -> None:
        game.events.ChoiceFromList.unhandle(self.on_choice)
        game.events.MenuClosed.unhandle(self._on_menu_closed)
