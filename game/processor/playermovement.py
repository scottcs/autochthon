"""Player movement processor."""
import esper

from game.component.positional import Positional
from game.events import PlayerMovementEvent, WorkEnqueueEvent, MapResizeEvent
from game.types import EventType


class PlayerMovementProcessor(esper.Processor):
    """Player movement processor."""
    def __init__(self, map_width: int, map_height: int) -> None:
        super().__init__()
        self.map_width: int = map_width
        self.map_height: int = map_height
        PlayerMovementEvent.handle(self.on_player_movement)
        MapResizeEvent.handle(self.on_map_resize)

    def on_player_movement(self, event: EventType) -> None:
        """Enqueue a movement event."""
        player_pos: Positional = self.world.component_for_entity(self.world.player, Positional)
        player_pos.x += event.get('dx', 0)
        player_pos.y += event.get('dy', 0)
        player_pos.x = min(max(player_pos.x, 0), self.map_width - 1)
        player_pos.y = min(max(player_pos.y, 0), self.map_height - 1)
        WorkEnqueueEvent.fire({'work': 'move'})

    def on_map_resize(self, event: EventType) -> None:
        """Handle when the map is resized."""
        self.map_width = event['width']
        self.map_height = event['height']

    def process(self, data: dict) -> None:
        """Process player movement events."""
