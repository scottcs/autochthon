"""Processor for escorting the deceased elsewhere."""
import logging
from typing import Any

import esper

from game.component.action import GUTMyTurn
from game.component.descriptive import Name
from game.component.status import GUTDead

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Psychopomps(esper.Processor):
    """Escort of the dead."""

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process dead entities."""
        for ent, _ in self.world.get_component(GUTDead):
            name = f"Entity {ent}"
            if self.world.has_component(ent, Name):
                name = f"{self.world.component_for_entity(ent, Name).generic} (Entity {ent})"
            log.debug(f"Escorting {name} to the afterlife.")
            self.world.remove_component(ent, GUTMyTurn)
            self.world.delete_entity(ent)
