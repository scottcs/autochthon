"""Processor module."""
from enum import IntEnum, auto


class Priority(IntEnum):
    """Processor priorities."""
    render = auto()
    movement = auto()
    time = auto()
    collision = auto()
    player_action = auto()
    ai = auto()
    input = auto()
