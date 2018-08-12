"""Base helper components to be subclassed."""
from math import floor
from typing import Optional

from game.types import Number


class BaseModifierComponent:
    """Base modifier component."""
    def __init__(self, addend: Number=0, factor: Number=1) -> None:
        self.addend: Number = addend
        self.factor: Number = factor


class BaseIntMinMaxComponent:
    """Base integer with min and max values component."""
    def __init__(self,
                 initial: Number=1,
                 minimum: Optional[Number]=None,
                 maximum: Optional[Number]=None) -> None:
        self.value: int = floor(initial)
        self.min: int = floor(minimum or 0)
        self.max: int = floor(maximum or initial)

    # TODO: maybe this functionality should be moved into a function in a helper module
    def _set_clamp(self, value: Number) -> None:
        self.value = max(min(floor(value), self.max), self.min)

    def add_clamp(self, amount: Number) -> None:
        """Add amount to the attribute without going out of bounds."""
        self._set_clamp(self.value + amount)

    def multiply_clamp(self, amount: Number) -> None:
        """Multiply the attribute by this amount, without going out of bounds."""
        self._set_clamp(self.value * amount)


def apply_modifier(value: Number, mod: BaseModifierComponent) -> Number:
    """Apply a modifier component to a value."""
    value += mod.addend
    value *= mod.factor
    return value
