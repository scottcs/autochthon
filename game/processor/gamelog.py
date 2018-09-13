"""Game Log processing."""
from typing import Any

import esper

from game.component.gamelog import GUTCombatLog, GUTStatusLog, GUTCommandLog
from game.events import GameLogEvent


class GameLogProcessor(esper.Processor):
    """Process the game log."""

    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process the game log."""
        for component_class in (GUTCommandLog, GUTCombatLog, GUTStatusLog):
            for ent, log in self.world.get_component(component_class):
                if not log.lines:
                    continue
                GameLogEvent.fire({"lines": log.lines})
                self.world.remove_component(ent, component_class)
