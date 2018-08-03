"""Typing for the game module."""
from enum import Enum, auto
from typing import Dict, List, Callable, Any


GameMapCellData = List[List[int]]
GameMapData = Dict[str, GameMapCellData]

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
