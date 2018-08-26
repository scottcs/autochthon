"""Base helper components to be subclassed."""
from math import floor
from typing import Optional, Union

from game.types import Number, Modifier
from game.utils.random import ChanceList


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


class BaseBoolChanceComponent:
    """Base boolean chance bag component."""
    def __init__(self, chance: int, out_of: int) -> None:
        self._chances = ChanceList([True, False], [chance, out_of])

    def update(self, chance: int, out_of: int) -> None:
        """Update the chances."""
        self._chances.set([True, False], [chance, out_of])

    def get(self) -> bool:
        """Returns whether the next try is a success."""
        try:
            success = next(self._chances)
        except StopIteration:
            self._chances.reset()
            success = next(self._chances)
        return bool(success)


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
