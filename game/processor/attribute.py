"""Attribute processors."""
from typing import Any

import esper

from game.component.attribute import ChangeHP, HP
from game.component.status import Dead


class HPProcessor(esper.Processor):
    """HP Processor."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process ChangeHP."""
        for ent, components in self.world.get_components(HP, ChangeHP):
            hp, change = components
            hp.add_clamp(change.amount)
            if hp.value <= hp.min:
                # TODO: clean up dead entities (convert to corpses? that decay?)
                self.world.add_component(ent, Dead())
            self.world.remove_component(ent, ChangeHP)
