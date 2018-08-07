"""Player movement processor."""
from typing import Any

import esper

from game.component.positional import Positional
from game.events import PlayerMovementEvent, WorkEnqueueEvent
from game.types import EventType


class PlayerMovementProcessor(esper.Processor):
    """Player movement processor."""
    def __init__(self) -> None:
        super().__init__()
        PlayerMovementEvent.handle(self.on_player_movement)

    def on_player_movement(self, event: EventType) -> None:
        """Enqueue a movement event."""
        player_pos: Positional = self.world.component_for_entity(self.world.player, Positional)
        player_pos.save_previous()
        player_pos.x += event.get('dx', 0)
        player_pos.y += event.get('dy', 0)
        player_pos.x = min(max(player_pos.x, 0), self.world.current_map.width - 1)
        player_pos.y = min(max(player_pos.y, 0), self.world.current_map.height - 1)
        if player_pos.prev_x != player_pos.x or player_pos.prev_y != player_pos.y:
            WorkEnqueueEvent.fire({'work': 'move'})

    def process(self, *args: Any) -> None:
        """Process player movement events."""
