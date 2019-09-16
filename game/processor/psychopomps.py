"""Processor for escorting the deceased elsewhere."""
import logging
import typing

import esper

import game.component.action
import game.component.descriptive
import game.component.status

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Psychopomps(esper.Processor):
    """Escort of the dead."""

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process dead entities."""
        for ent, _ in self.world.get_component(game.component.status.GUTDead):
            name = f"Entity {ent}"
            if self.world.has_component(ent, game.component.descriptive.Name):
                name = f"{self.world.component_for_entity(ent, game.component.descriptive.Name).generic} (Entity {ent})"
            log.debug(f"Escorting {name} to the afterlife.")
            if self.world.has_component(ent, game.component.action.GUTMyTurn):
                self.world.remove_component(ent, game.component.action.GUTMyTurn)
            self.world.delete_entity(ent)
