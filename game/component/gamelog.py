"""Game log components."""
import typing

import game.palette
import game.types


class BaseLog:
    """Component for the game log."""

    def __init__(
        self,
        initial_line: typing.Optional[str] = None,
        initial_color: str = game.palette.Message.default,
    ) -> None:
        self.lines: list = []
        if initial_line is not None:
            self.add(initial_line, color=initial_color)

    def add(self, message: str, color: str = game.palette.Message.default) -> None:
        """Add a new line to the log."""
        # capitalize
        message = f"{message[0].upper()}{message[1:]}"

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
        self.add_raw(message, color)

    def add_raw(self, message: str, color: str = game.palette.Message.default) -> None:
        """Append to the log without any additional formatting."""
        self.lines.append(game.types.LogLine(message, color))

    def __str__(self) -> str:
        return "".join([l.message for l in self.lines])

    def blt_colorized(self) -> str:
        """Return a colorized string of the lines for BearLibTerminal."""
        return "".join([f"[color={l.color}]{l.message}[/color]" for l in self.lines])


class TMPCombat(BaseLog):
    """Combat log."""


class TMPStatus(BaseLog):
    """Log status effects."""


class TMPCommand(BaseLog):
    """Log command results."""


class TMPDescription(BaseLog):
    """Log descriptions."""
