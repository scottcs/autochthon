"""Processor for escorting the deceased elsewhere."""
import logging
from typing import Any

import esper

from game.component.status import Dead

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Psychopomps(esper.Processor):
    """Escort of the dead."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process dead entities."""
        for ent, _ in self.world.get_component(Dead):
            log.debug(f'Escorting {ent} to the afterlife.')
            self.world.delete_entity(ent)
