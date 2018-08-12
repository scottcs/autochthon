"""Game Log processing."""
from typing import Any

import esper

from game.component.gamelog import CombatLog


class GameLogProcessor(esper.Processor):
    """Process the game log."""
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process the game log."""
        for ent, log in self.world.get_component(CombatLog):
            message = ''.join(log.lines)
            # TODO: color
            # TODO: send event
            print(message)
            self.world.remove_component(ent, CombatLog)
