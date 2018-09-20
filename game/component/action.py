"""Action components."""
from dataclasses import dataclass


@dataclass
class Actor:
    """Actor components use initiative values to take actions (lower is faster)."""

    base_initiative: int

    def __post_init__(self) -> None:
        self.initiative: int = self.base_initiative


class GUTMyTurn:
    """Current Actor's turn."""
