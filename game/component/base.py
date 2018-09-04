"""Base helper components to be subclassed."""
from math import floor
from typing import Optional, Union

from game.types import Number, Modifier


class BaseModifierComponent:
    """Base modifier component."""
    def __init__(self, addend: Union[Number, str]=0, factor: Union[Number, str]=0) -> None:
        self.modifier: Modifier = Modifier(addend, factor)


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


class BaseTemporaryComponent:
    """Basic component that can optionally be temporary."""
    def __init__(self, temporary: bool=False) -> None:
        self.temporary = temporary


def accumulate_modifiers(*modifiers: BaseModifierComponent) -> Modifier:
    """Accumulate all modifiers and return the result."""
    addend: float = 0
    factor: float = 0
    for mod in modifiers:
        addend += mod.modifier.addend
        factor += mod.modifier.factor
    return Modifier(addend, factor)
