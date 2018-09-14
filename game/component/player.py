"""Player components."""
from dataclasses import dataclass


@dataclass
class GUTPlayerBump:
    """Player wants to do something that passes time, maybe in a direction."""

    dx: int = 0
    dy: int = 0


@dataclass
class Player:
    """Player component."""

    fov: int = 7
