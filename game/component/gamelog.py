"""Game log components."""
from typing import Optional

from game.types import LogLine
from gamedata.palette import MessagePalette


class BaseLog:
    """Component for the game log."""

    def __init__(
        self, initial_line: Optional[str] = None, initial_color: int = MessagePalette.default
    ) -> None:
        self.lines: list = []
        if initial_line is not None:
            self.add(initial_line, color=initial_color)

    def add(self, message: str, color: int = MessagePalette.default) -> None:
        """Add a new line to the log."""
        # capitalize
        message = f"{message[0].upper()}{message[1:]}"

        # if this isn't the first line, add a space before it
        try:
            last = self.lines.pop()
        except IndexError:
            last = None
        if last:
            if last.color == color:
                message = f"{last.message} {message}"
            else:
                self.lines.append(last)
                message = " " + message
        self.append(message, color)

    def append(self, message: str, color: int = MessagePalette.default) -> None:
        """Append to the log without a space."""
        self.lines.append(LogLine(message, color))


class GUTCombatLog(BaseLog):
    """Combat log."""


class GUTStatusLog(BaseLog):
    """Log status effects."""


class GUTCommandLog(BaseLog):
    """Log command results."""
