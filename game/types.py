"""Typing for the game module."""
import enum
import inspect
import typing

import game.const.palette
import game.utils.random

Config = typing.MutableMapping[typing.Any, typing.Any]
Event = typing.Dict[typing.Any, typing.Any]
EventHandler = typing.Callable[[Event], typing.Any]
Layout = typing.Dict[str, typing.Any]

Entity = int


class RenderLayer(enum.IntEnum):
    """Render layers, from bottom to top."""

    background = enum.auto()
    floor = enum.auto()
    item = enum.auto()
    wall = enum.auto()
    icon = enum.auto()
    enemy = enum.auto()
    player = enum.auto()
    effect = enum.auto()


class Priority(enum.IntEnum):
    """Processor priorities."""

    gamelog = enum.auto()
    render = enum.auto()
    psychopomps = enum.auto()
    attributes = enum.auto()
    damage_resolution = enum.auto()
    defense = enum.auto()
    attack_hit = enum.auto()
    attack_deflect = enum.auto()
    attack_block = enum.auto()
    attack_dodge = enum.auto()
    attack_miss = enum.auto()
    targeting = enum.auto()
    movement = enum.auto()
    ai = enum.auto()
    container = enum.auto()
    turn = enum.auto()
    time = enum.auto()
    player_bump = enum.auto()
    player_input = enum.auto()


class ProcessGroup(enum.Enum):
    """Groups of processors."""

    default = enum.auto()
    player = enum.auto()
    time = enum.auto()
    render = enum.auto()
    gamelog = enum.auto()


class GameState(enum.Enum):
    """Game states."""

    unknown = enum.auto()
    loading = enum.auto()
    main_menu = enum.auto()
    creating = enum.auto()
    playing = enum.auto()
    in_game_menu = enum.auto()
    shutdown = enum.auto()


class Attack(enum.Enum):
    """Attack types."""

    melee = enum.auto()
    projectile = enum.auto()


class Equip(enum.Enum):
    """Equipment types -- where an item was intended to be worn/held."""

    none = enum.auto()
    head = enum.auto()
    face = enum.auto()
    neck = enum.auto()
    shoulder = enum.auto()
    back = enum.auto()
    torso = enum.auto()
    waist = enum.auto()
    tail = enum.auto()
    wrist = enum.auto()
    hand = enum.auto()
    finger = enum.auto()
    leg = enum.auto()
    foot = enum.auto()
    implant = enum.auto()
    shield = enum.auto()
    melee = enum.auto()
    ranged = enum.auto()
    any = enum.auto()


Number = typing.Union[int, float]


class Modifier:
    """Modifier set."""

    def __init__(
        self, addend: typing.Union[Number, str] = 0, factor: typing.Union[Number, str] = 0
    ) -> None:
        self._addend: Number = 0
        self._factor: Number = 0
        self._addend_func: typing.Optional[typing.Callable[[], Number]] = None
        self._factor_func: typing.Optional[typing.Callable[[], Number]] = None
        # TODO: I'm not convinced this is the best way to do this. RNG per entity instead? How?
        rng = game.utils.random.RNGCache.get("ModifierClass")
        if isinstance(addend, str):
            self._addend_func = game.utils.random.parse(addend, rng)
        else:
            self._addend = addend
        if isinstance(factor, str):
            self._factor_func = game.utils.random.parse(factor, rng)
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


class LogLine(typing.NamedTuple):
    """A Game log message with color."""

    message: str = ""
    color: str = game.const.palette.Message.default


def get_union_types(union_type: typing.Any) -> tuple:
    """Get a tuple of the types of a union."""
    try:
        if union_type.__origin__ is typing.Union:
            return tuple(union_type.__args__)
    except (AttributeError, TypeError):
        pass
    # noinspection PyRedundantParentheses
    return (union_type,)


def is_in_union(arg: typing.Any, union_type: typing.Union) -> bool:
    """Return true if the given argument is included in the union type."""
    return isinstance(arg, get_union_types(union_type))


def parameter_types(func: typing.Callable) -> dict:
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


class PlayerRenderData(typing.NamedTuple):
    """Player render data."""

    x: int
    y: int
    fov: int
    layer: RenderLayer
    tile_id: int
    color: str


class TileType(enum.Enum):
    """Tile types."""

    floor = enum.auto()
    wall_v = enum.auto()
    wall_h = enum.auto()
