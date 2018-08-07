"""Movement processor."""
from typing import Any

import esper

from game.component.position import Position
from game.component.velocity import Velocity
from game.events import MoveEntityEvent, WorldNeedsUpdateEvent, TimePassedEvent
from game.types import EventType


class MovementProcessor(esper.Processor):
    """Movement processor."""
    def __init__(self) -> None:
        super().__init__()
        self.needs_update = False
        MoveEntityEvent.handle(self.on_move_entity)
        TimePassedEvent.handle(self.on_time_passed)

    @staticmethod
    def on_move_entity(event: EventType) -> None:
        """Handle move entity event."""
        velocity = event['velocity']
        velocity.x = event['dx']
        velocity.y = event['dy']

    def on_time_passed(self, _event: EventType) -> None:
        """Handle time passed event."""
        self.needs_update = True

    def process(self, *args: Any) -> None:
        """Process player movement events."""
        # TODO: take velocity.speed into account
        if self.needs_update:
            for entity, components in self.world.get_components(Position, Velocity):
                position, velocity = components
                if velocity.x or velocity.y:
                    position.x += velocity.x
                    position.y += velocity.y
                    # TODO: use speed instead of setting this to 0
                    velocity.x = velocity.y = 0
                    WorldNeedsUpdateEvent.fire()
