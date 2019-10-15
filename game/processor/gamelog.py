"""Game Log processing."""
import collections
import typing

import game.component.gamelog
import game.data
import game.events
import game.world

buffer: typing.Deque[game.component.gamelog.BaseLog] = collections.deque(
    maxlen=game.data.config["max_game_log_buffer"]
)


class GameLog(game.world.Processor):
    """Process the game log."""

    def process(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Process the game log."""
        for component_class in (
            game.component.gamelog.TMPCommand,
            game.component.gamelog.TMPCombat,
            game.component.gamelog.TMPStatus,
            game.component.gamelog.TMPDescription,
        ):
            for ent, log_component in self.world.get_component(component_class):
                if not log_component.lines:
                    continue
                game.events.GameLog({"log_component": log_component})
                buffer.append(log_component)
                self.world.remove_component(ent, component_class)
