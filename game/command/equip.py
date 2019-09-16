"""Equip/Unequip command."""
import game.command.base
import game.component.container
import game.component.descriptive
import game.component.gamelog
import game.component.player
import game.events
import game.types
import gamedata.palette


class Equip(game.command.base.BaseCommand):
    """Equip/Unequip command."""

    def run(self) -> None:
        """Run the command."""
        for ent, _ in self.world.get_component(game.component.player.Player):
            items_carried = self._get_items_carried(ent)
            if items_carried:
                game.events.ChoiceFromList.handle(self.on_choice)
                game.events.MenuClosed.handle(self._on_menu_closed)
                game.events.ChooseFromList.fire(
                    {
                        "header": "Equip/Unequip what?",
                        "items": items_carried,
                        "disable": [game.types.Equip.none.name],
                    }
                )
            else:
                cmd_log = self.world.get_or_add_component(ent, game.component.gamelog.GUTCommand)
                cmd_log.add("You have nothing to eqiup!")

    def on_choice(self, event: game.types.EventType) -> None:
        """Callback for ChoiceFromList event."""
        input_key = self._keys_from_event(event)
        for ent, _ in self.world.get_component(game.component.player.Player):
            equipment = self.world.component_for_entity(ent, game.component.container.Equipment)
            want_to_equip = None
            for item_ent, components in self.world.get_components(
                game.component.container.GUTContained,
                game.component.descriptive.Name,
                game.component.container.Containable,
            ):
                contained, name, containable = components
                if contained.by_ent == ent and contained.label == input_key.key:
                    if containable.equip_type != game.types.Equip.none and equipment:
                        want_to_equip = (containable, name)
                        break
            if want_to_equip:
                equip_count = 0
                for item_ent, components in self.world.get_components(
                    game.component.container.GUTContained, game.component.container.Containable
                ):
                    contained, containable = components
                    if (
                        containable.equipped
                        and containable.equip_type == want_to_equip[0].equip_type
                    ):
                        equip_count += 1
                equipment_slot = equipment.slots[want_to_equip[0].equip_type]
                name = equipment_slot["name"]
                if want_to_equip[0].equipped:
                    want_to_equip[0].equipped = False
                    cmd_log = self.world.get_or_add_component(
                        ent, game.component.gamelog.GUTCommand
                    )
                    cmd_log.add("You unequip ")
                    cmd_log.append(want_to_equip[1].generic, gamedata.palette.ItemPalette.epic)
                    cmd_log.append(f" from your {name} slot.")
                    game.events.ChoiceAccepted.fire()
                else:
                    if equipment_slot["max"] > equip_count:
                        want_to_equip[0].equipped = True
                        cmd_log = self.world.get_or_add_component(
                            ent, game.component.gamelog.GUTCommand
                        )
                        cmd_log.add("You equip ")
                        cmd_log.append(want_to_equip[1].generic, gamedata.palette.ItemPalette.epic)
                        cmd_log.append(f" in your {name} slot.")
                        game.events.ChoiceAccepted.fire()
                    else:
                        msg = f"You can't equip any more items in your {name} slot."
                        cmd_log = self.world.get_or_add_component(
                            ent, game.component.gamelog.GUTCommand
                        )
                        cmd_log.add(msg)
                        game.events.ChoiceDeclined.fire({"status": msg})
            else:
                cmd_log = self.world.get_or_add_component(ent, game.component.gamelog.GUTCommand)
                cmd_log.add("You can't find the item you want to equip.")
