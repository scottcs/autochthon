"""Time processor."""
import esper

from game.component.actor import Actor


class TimeProcessor(esper.Processor):
    """Time processor."""

    def __init__(self) -> None:
        super().__init__()

    def process(self, data: dict) -> None:
        """Process time."""
        if data['time_passed']:
            for entity, actor in self.world.get_component(Actor):
                actor.time_units += actor.rate
