"""Action components."""
from dataclasses import dataclass


@dataclass
class Actor:
    """Actor components use initiative values to take actions (lower is faster)."""

    base_initiative: int
    initiative: int = 0
    counter: int = 0


class GUTMyTurn:
    """Current Actor's turn."""
