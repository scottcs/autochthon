"""Game Log processing."""
import typing

import esper

import game.component.gamelog
import game.events


class GameLog(esper.Processor):
    """Process the game log."""

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process the game log."""
        for component_class in (
            game.component.gamelog.TMPCommand,
            game.component.gamelog.TMPCombat,
            game.component.gamelog.TMPStatus,
            game.component.gamelog.TMPDescription,
        ):
            for ent, log in self.world.get_component(component_class):
                if not log.lines:
                    continue
                game.events.GameLog.fire({"lines": log.lines})
                self.world.remove_component(ent, component_class)
