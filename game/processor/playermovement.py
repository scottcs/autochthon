"""Player movement processor."""

import esper

from game.component.positional import Positional
from game.events import PlayerMovementEvent


class PlayerMovementProcessor(esper.Processor):
    """Player movement processor."""
    def __init__(self, player):
        super().__init__()
        self.player = player
        PlayerMovementEvent.handle(self.on_move)

    def on_move(self, dx, dy):
        """Enqueue a movement event."""
        player_pos = self.world.component_for_entity(self.player, Positional)
        player_pos.x += dx
        player_pos.y += dy

    def process(self):
        """Process player movement events."""
