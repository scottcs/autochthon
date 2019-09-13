"""Base helper components to be subclassed."""
import dataclasses
import math
import typing

import game.types


class BaseModifierComponent:
    """Base modifier component."""

    def __init__(
        self,
        addend: typing.Union[game.types.Number, str] = 0,
        factor: typing.Union[game.types.Number, str] = 0,
    ) -> None:
        self.modifier: game.types.Modifier = game.types.Modifier(addend, factor)


class BaseIntMinMaxComponent:
    """Base integer with min and max values component."""

    def __init__(
        self,
        initial: game.types.Number = 1,
        minimum: typing.Optional[game.types.Number] = None,
        maximum: typing.Optional[game.types.Number] = None,
    ) -> None:
        self.value: int = math.floor(initial)
        self.min: int = math.floor(minimum or 0)
        self.max: int = math.floor(maximum or initial)

    # TODO: maybe this functionality should be moved into a function in a helper module
    def _set_clamp(self, value: game.types.Number) -> None:
        self.value = max(min(math.floor(value), self.max), self.min)

    def add_clamp(self, amount: game.types.Number) -> None:
        """Add amount to the attribute without going out of bounds."""
        self._set_clamp(self.value + amount)

    def multiply_clamp(self, amount: game.types.Number) -> None:
        """Multiply the attribute by this amount, without going out of bounds."""
        self._set_clamp(self.value * amount)


@dataclasses.dataclass
class BaseTemporaryComponent:
    """Basic component that can optionally be temporary."""

    temporary: bool = False


def accumulate_modifiers(*modifiers: BaseModifierComponent) -> game.types.Modifier:
    """Accumulate all modifiers and return the result."""
    addend: float = 0
    factor: float = 0
    for mod in modifiers:
        addend += mod.modifier.addend
        factor += mod.modifier.factor
    return game.types.Modifier(addend, factor)
