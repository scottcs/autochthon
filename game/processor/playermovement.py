"""Player movement processor."""
import esper

from game.component.positional import Positional
from game.events import PlayerMovementEvent, QueueWorkEvent


class PlayerMovementProcessor(esper.Processor):
    """Player movement processor."""
    def __init__(self) -> None:
        super().__init__()
        PlayerMovementEvent.handle(self.on_move)

    def on_move(self, event: dict) -> None:
        """Enqueue a movement event."""
        player_pos: Positional = self.world.component_for_entity(self.world.player, Positional)
        player_pos.x += event.get('dx', 0)
        player_pos.y += event.get('dy', 0)
        QueueWorkEvent.fire({'work': 'move'})

    def process(self, data: dict) -> None:
        """Process player movement events."""
