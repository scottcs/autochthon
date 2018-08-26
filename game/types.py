"""Typing for the game module."""
from enum import Enum, auto, IntEnum
from typing import Dict, Callable, Any, NamedTuple, Union, Optional

from game.utils.random import parse


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


class Priority(IntEnum):
    """Processor priorities."""
    psychopomps = auto()
    render = auto()
    gamelog = auto()
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


class Modifier:
    """Modifier set."""

    def __init__(self, addend: Union[Number, str]=0, factor: Union[Number, str]=0):
        self._addend: Number = 0
        self._factor: Number = 0
        self._addend_func: Optional[Callable] = None
        self._factor_func: Optional[Callable] = None
        if isinstance(addend, str):
            self._addend_func = parse(addend)
        else:
            self._addend = addend
        if isinstance(factor, str):
            self._factor_func = parse(factor)
        else:
            self._factor = factor

    @property
    def addend(self):
        """Get addend, calling its func if it exists."""
        if self._addend_func is not None:
            return self._addend_func()
        return self._addend

    @property
    def factor(self):
        """Get factor, calling its func if it exists."""
        if self._factor_func is not None:
            return self._factor_func()
        return self._factor


class LogLine(NamedTuple):
    """A Game log message with color."""
    message: str = ''
    color: int = 0xffffff


class ComponentSchema(NamedTuple):
    """A schema for a component."""
    type: Any
    args: tuple
    kwargs: dict
