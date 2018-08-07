"""Typing for the game module."""
from enum import Enum, auto
from typing import Dict, Callable, Any, NamedTuple


class MapCell(NamedTuple):
    """Map cell."""
    x: int = 0
    y: int = 0
    transparent: bool = False
    walkable: bool = False
    fov: bool = False
    explored: bool = False


EventType = Dict
EventHandler = Callable[[EventType], Any]

Entity = int


class RenderLayer(Enum):
    """Render layers, from bottom to top."""
    BACKGROUND = auto()
    FLOOR = auto()
    ITEM = auto()
    WALL = auto()
    ICON = auto()
    ENEMY = auto()
    PLAYER = auto()
    EFFECT = auto()
