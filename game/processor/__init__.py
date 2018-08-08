"""Processor module."""
from enum import IntEnum, auto


class Priority(IntEnum):
    """Processor priorities."""
    render = auto()
    movement = auto()
    time = auto()
    collision = auto()
    ai = auto()
    input = auto()
