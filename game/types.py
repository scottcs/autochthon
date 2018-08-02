"""Typing for the game module."""
from typing import Dict, List, Callable, Any


GameMapCellData = List[List[int]]
GameMapData = Dict[str, GameMapCellData]

EventType = Dict
EventHandler = Callable[[EventType], Any]

Entity = int
