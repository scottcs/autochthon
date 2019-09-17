"""Game log components."""
import typing

import game.constants.palette
import game.types


class BaseLog:
    """Component for the game log."""

    def __init__(
        self,
        initial_line: typing.Optional[str] = None,
        initial_color: int = game.constants.palette.Message.default,
    ) -> None:
        self.lines: list = []
        if initial_line is not None:
            self.add(initial_line, color=initial_color)

    def add(self, message: str, color: int = game.constants.palette.Message.default) -> None:
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

    def append(self, message: str, color: int = game.constants.palette.Message.default) -> None:
        """Append to the log without a space."""
        self.lines.append(game.types.LogLine(message, color))


class GUTCombat(BaseLog):
    """Combat log."""


class GUTStatus(BaseLog):
    """Log status effects."""


class GUTCommand(BaseLog):
    """Log command results."""


class GUTDescription(BaseLog):
    """Log descriptions."""
