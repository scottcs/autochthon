"""Player components."""
import dataclasses


@dataclasses.dataclass
class TMPPlayerBump:
    """Player wants to do something that passes time, maybe in a direction."""

    dx: int = 0
    dy: int = 0


@dataclasses.dataclass
class Player:
    """Player component."""

    fov: int = 7
