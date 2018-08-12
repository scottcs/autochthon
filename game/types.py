"""Typing for the game module."""
from enum import Enum, auto, IntEnum
from typing import Dict, Callable, Any, NamedTuple, Union


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


class DirectionType(Enum):
    """Cardinal direction type."""
    n = 1
    ne = 2
    e = 3
    se = 4
    s = 5
    sw = 6
    w = 7
    nw = 8


class Priority(IntEnum):
    """Processor priorities."""
    psychopomps = auto()
    render = auto()
    attributes = auto()
    movement = auto()
    damage_resolution = auto()
    defense = auto()
    attack_hit = auto()
    attack_deflect = auto()
    attack_block = auto()
    attack_dodge = auto()
    attack_miss = auto()
    targeting = auto()
    ai = auto()
    time = auto()
    player_bump = auto()
    player_input = auto()


class ProcessGroup(Enum):
    """Groups of processors."""
    default = auto()
    player = auto()
    time = auto()
    render = auto()


class GameState(Enum):
    """Game states."""
    UNKNOWN = auto()
    LOADING = auto()
    MAIN_MENU = auto()
    CREATING = auto()
    PLAYING = auto()
    IN_GAME_MENU = auto()
    SHUTDOWN = auto()


class AttackType(Enum):
    """Attack types."""
    melee = auto()
    projectile = auto()


Number = Union[int, float]


class Modifier(NamedTuple):
    """Modifier set."""
    addend: Number = 0
    factor: Number = 0
