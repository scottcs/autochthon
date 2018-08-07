"""Time processor."""
import esper

from game.component.actor import Actor
from game.events import GameTimeEvent, TimePassedEvent
from game.types import EventType
from game.utils.time import GameTime, MOMENTS_PER_TURN


class TimeProcessor(esper.Processor):
    """Time processor."""
    def __init__(self) -> None:
        super().__init__()
        self.needs_update = True
        GameTimeEvent.handle(self.on_game_time)

    def on_game_time(self, _event: EventType) -> None:
        """Handle game turn event."""
        self.needs_update = True

    def process(self, *args, **kwargs):
        """Process actors."""
        if self.needs_update:
            for ent, component in self.world.get_component(Actor):
                component.time_units += component.rate
            self.needs_update = False
            TimePassedEvent.fire({'time': GameTime(MOMENTS_PER_TURN)})
