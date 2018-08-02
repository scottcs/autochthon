"""Game states."""

from enum import Enum, auto


class GameState(Enum):
    """Game states."""
    UNKNOWN = auto()
    LOADING = auto()
    MAIN_MENU = auto()
    CREATING = auto()
    PLAYING = auto()
    IN_GAME_MENU = auto()
    SHUTDOWN = auto()
