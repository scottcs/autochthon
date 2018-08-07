"""Functions for randomness."""
from __future__ import annotations
from random import randrange, shuffle
from typing import Any, List


class ChanceList:
    """A list of items, weighted by chance.

    Iteration removes items from the list.

    """
    def __init__(self, items: List[Any], weights: List[int]) -> None:
        super().__init__()
        self._original_items: List[Any] = []
        self._items: List[Any] = []
        self.set(items, weights)

    def set(self, items: List[Any], weights: List[int]) -> None:
        """Set the chance list according to the given weights."""
        self._original_items = []
        for i, item in enumerate(items):
            self._original_items.extend([item for _ in range(weights[i])])
        self.reset()

    def reset(self) -> None:
        """Reset the list to its original values."""
        self._items = self._original_items.copy()
        shuffle(self._items)

    def __iter__(self) -> ChanceList:
        return self

    def __next__(self) -> Any:
        if len(self._items) == 0:
            raise StopIteration
        return self._items.pop()

    def __repr__(self) -> str:
        return repr(self._items)


def coin_flip() -> bool:
    """Choose a random bool."""
    return randrange(2) == 0
