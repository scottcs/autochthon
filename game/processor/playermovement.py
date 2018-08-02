"""Player movement processor."""
from typing import Any

import esper

from game.component.positional import Positional
from game.events import PlayerMovementEvent


class PlayerMovementProcessor(esper.Processor):
    """Player movement processor."""
    def __init__(self, player: int) -> None:
        super().__init__()
        self.player: int = player
        PlayerMovementEvent.handle(self.on_move)

    def on_move(self, event: dict) -> None:
        """Enqueue a movement event."""
        player_pos = self.world.component_for_entity(self.player, Positional)
        player_pos.x += event.get('dx', 0)
        player_pos.y += event.get('dy', 0)

    def process(self, *args: Any) -> None:
        """Process player movement events."""
