"""Processor for escorting the deceased elsewhere."""
from typing import Any

import esper

from game.component.dead import Dead


class Psychopomps(esper.Processor):
    """Escort of the dead."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process dead entities."""
        for ent, _ in self.world.get_component(Dead):
            self.world.delete_entity(ent)
