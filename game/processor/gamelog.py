"""Game Log processing."""
from typing import Any

import esper

from game.component.gamelog import CombatLog
from game.events import GameLogEvent


class GameLogProcessor(esper.Processor):
    """Process the game log."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process the game log."""
        for ent, log in self.world.get_component(CombatLog):
            GameLogEvent.fire({'lines': log.lines})
            self.world.remove_component(ent, CombatLog)
