"""Game log components."""
from typing import Optional

from game.types import LogLine
from gamedata.palette import MessagePalette


class BaseLog:
    """Component for the game log."""
    def __init__(self,
                 initial_line: Optional[str]=None,
                 initial_color: Optional[int]=None) -> None:
        self.lines: list = []
        if initial_line is not None:
            self.add(initial_line, color=initial_color)

    def add(self, message: str, color: Optional[int]=None) -> None:
        """Add a new line to the log."""
        if color is None:
            color = MessagePalette.default
        self.lines.append(LogLine(message, color))

    def append_last(self, message: str) -> None:
        """Append to the last log line."""
        try:
            last = self.lines.pop()
            self.add(last.message + message, last.color)
        except IndexError:
            self.add(message)


class GUTCombatLog(BaseLog):
    """Combat log."""


class GUTStatusLog(BaseLog):
    """Log status effects."""
