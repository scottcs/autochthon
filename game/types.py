"""Typing for the game module."""
import inspect
from enum import Enum, IntEnum, auto
from typing import Any, Callable, Dict, NamedTuple, Optional, Union

from game.utils.random import RNGCache, parse
from gamedata.palette import MessagePalette

EventType = Dict
EventHandler = Callable[[EventType], Any]

Entity = int


class RenderLayer(Enum):
    """Render layers, from bottom to top."""

    background = auto()
    floor = auto()
    item = auto()
    wall = auto()
    icon = auto()
    enemy = auto()
    player = auto()
    effect = auto()


class Priority(IntEnum):
    """Processor priorities."""

    gamelog = auto()
    render = auto()
    psychopomps = auto()
    attributes = auto()
    damage_resolution = auto()
    defense = auto()
    attack_hit = auto()
    attack_deflect = auto()
    attack_block = auto()
    attack_dodge = auto()
    attack_miss = auto()
    targeting = auto()
    movement = auto()
    ai = auto()
    container = auto()
    turn = auto()
    time = auto()
    player_bump = auto()
    player_input = auto()


class ProcessGroup(Enum):
    """Groups of processors."""

    default = auto()
    player = auto()
    time = auto()
    render = auto()
    gamelog = auto()


class GameState(Enum):
    """Game states."""

    unknown = auto()
    loading = auto()
    main_menu = auto()
    creating = auto()
    playing = auto()
    in_game_menu = auto()
    shutdown = auto()


class AttackType(Enum):
    """Attack types."""

    melee = auto()
    projectile = auto()


class EquipType(Enum):
    """Equipment types -- where an item was intended to be worn/held."""

    none = auto()
    head = auto()
    face = auto()
    neck = auto()
    shoulder = auto()
    back = auto()
    torso = auto()
    waist = auto()
    tail = auto()
    wrist = auto()
    hand = auto()
    finger = auto()
    leg = auto()
    foot = auto()
    implant = auto()
    shield = auto()
    melee = auto()
    ranged = auto()
    any = auto()


Number = Union[int, float]


class Modifier:
    """Modifier set."""

    def __init__(self, addend: Union[Number, str] = 0, factor: Union[Number, str] = 0) -> None:
        self._addend: Number = 0
        self._factor: Number = 0
        self._addend_func: Optional[Callable[[], Number]] = None
        self._factor_func: Optional[Callable[[], Number]] = None
        # TODO: I'm not convinced this is the best way to do this. RNG per entity instead? How?
        rng = RNGCache.get("ModifierClass")
        if isinstance(addend, str):
            self._addend_func = parse(addend, rng)
        else:
            self._addend = addend
        if isinstance(factor, str):
            self._factor_func = parse(factor, rng)
        else:
            self._factor = factor

    @property
    def addend(self) -> Number:
        """Get addend, calling its func if it exists."""
        if self._addend_func is not None:
            return self._addend_func()
        return self._addend

    @property
    def factor(self) -> Number:
        """Get factor, calling its func if it exists."""
        if self._factor_func is not None:
            return self._factor_func()
        return self._factor


class LogLine(NamedTuple):
    """A Game log message with color."""

    message: str = ""
    color: int = MessagePalette.default


def get_union_types(union_type: Any) -> tuple:
    """Get a tuple of the types of a union."""
    try:
        if union_type.__origin__ is Union:
            return tuple(union_type.__args__)
    except (AttributeError, TypeError):
        pass
    # noinspection PyRedundantParentheses
    return (union_type,)


def is_in_union(arg: Any, union_type: Union) -> bool:
    """Return true if the given argument is included in the union type."""
    return isinstance(arg, get_union_types(union_type))


def parameter_types(func: Callable) -> dict:
    """Get a dict of parameter names and allowed types from a function."""
    result = {}
    sig = inspect.signature(func)
    for name, parameter in sig.parameters.items():
        if name in ("self", "args", "kwargs"):
            continue
        types = get_union_types(parameter.annotation)
        result[name] = {"types": types}
        if parameter.default != inspect.Parameter.empty:
            result[name]["default"] = parameter.default
    return result
