"""Functions for randomness."""
from __future__ import annotations
import hashlib
import logging
from pathlib import Path
import random
from random import shuffle, randrange, randint, choice  # TODO: remove these
import re
from typing import Any, List, Callable, Optional, Sequence

from game.utils.pcg32 import PCG32Generator

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

MAX_UINT32 = 4294967295
WEIGHTED_DEF = re.compile(r'(?<=^weighted\(\()([^)]+)\), \(([^)]+)\)\)')
STEP_DEF = re.compile(r'(?<=^step\()([^)]+)\)')
DIE_DEF = re.compile(r'(\d+d\d+)([+-]\d+)?')
WORDS_FILE = Path('/usr/share/dict/words')  # TODO: replace with one in this repo with game terms?

_collision_check = {}


def get_random_words(rng: Any=None, count: int=3) -> str:
    """Get a string of `count` random words, CamelCased, using the given rng or Python's."""
    result = ''
    if rng is None:
        rng = random
    with WORDS_FILE.open() as f:
        lines = f.readlines()
    for x in range(count):
        try:
            word = lines[rng.rand(len(lines))].strip()
        except AttributeError:
            word = lines[rng.randrange(0, len(lines))].strip()
        result += word.capitalize()
    return result


def string_hash(s: str) -> int:
    """Convert a string into a deterministic hash integer."""
    h = int(hashlib.sha1(s.encode('utf-8')).hexdigest(), 16)
    while h in _collision_check and _collision_check[h] != s:
        log.warning(f'Collision between {s} and {_collision_check[h]}')
        h += 1
    _collision_check.setdefault(h, s)
    return h


class _GameRNG:
    """RNG with game related function."""

    def __init__(self, name: str, rng: Any) -> None:
        self.name = name
        self._rng = rng

    def fraction(self) -> float:
        """Return a random float between 0 and 1."""
        return self._rng.get_next_uint32() / MAX_UINT32

    def rand(self, lower: int=0, upper: int=0) -> int:
        """Return a random integer in range [lower, upper], including both endpoints."""
        if upper > 0:
            start = lower
            bound = upper - lower
        elif lower > 0:
            start = 0
            bound = lower
        else:
            return self._rng.get_next_uint32()
        return start + self._rng.get_next_uint(bound + 1)

    def choice(self, options: Sequence[Any]) -> int:
        """Return a random choice amongst the options."""
        return options[self.rand(len(options) - 1)]

    def coin(self) -> bool:
        """Return the result of a coin flip."""
        return bool(self.rand(1))


class RNG:
    """Base random number generator."""

    def __init__(self, seed: Optional[str]=None) -> None:
        if not seed:
            seed = get_random_words()
        self.seed = seed
        self.seed_hash = string_hash(self.seed)
        self._rng = PCG32Generator(self.seed_hash, 0)
        self._cache = {}

    def get(self, stream: Optional[str]=None) -> _GameRNG:
        """Get a sub-rng."""
        if not stream:
            stream = get_random_words(rng=self._rng)
        if stream not in self._cache:
            stream_hash = string_hash(stream)
            rng = _GameRNG(stream, PCG32Generator(self.seed_hash, stream_hash))
            self._cache[stream] = rng
        return self._cache[stream]


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


def parse(text: str) -> Optional[Callable]:
    """Parse a string and return a function to provide the requested randomness.

    Looks for:
        'step(min, max, step_amount)'
            where min is a number, max is a number, and step_amount is a number.
            returns a function that returns a number between min and max, at step_amount intervals
            (ex: step(-0.1, 0.1, 0.1) returns either -0.1, 0.0, or 0.1)
        'XdY+Z'
            where X, Y and Z are integers (and +Z is optional)
            returns a function that rolls X amount of Y-sided die and returns the sum + Z
        'weighted((...), (...))'
            where the first tuple is a list of items, and the second tuple is a list of integers
            the two tuples must have the same length
            returns a function that returns a value chosen from the values with the given weights
            (ex: weighted(('a', 'b', 'c'), (1, 1, 2)) returns a choice from ['a', 'b', 'c', 'c'])

    """
    found = WEIGHTED_DEF.search(text)
    func = None
    if found:
        func = _parse_weighted(*found.groups())
    else:
        found = STEP_DEF.search(text)
        if found:
            func = _parse_step(*found.groups())
        else:
            found = DIE_DEF.search(text)
            if found:
                func = _parse_die(*found.groups())
    return func


def _parse_weighted(items_str: str, weights_str: str) -> Callable:
    items = [i.strip(' \'"') for i in items_str.split(',')]
    weights = [int(w.strip()) for w in weights_str.split(',')]
    choices = []
    for i, item in enumerate(items):
        choices.extend([item for _ in range(weights[i])])

    def _closure():
        return choice(choices)

    return _closure


def _parse_step(expr: str) -> Callable:
    try:
        s_min, s_max, s_step = [int(e.strip()) for e in expr.split(',')]
    except ValueError:
        s_min, s_max, s_step = [float(e.strip()) for e in expr.split(',')]
    x = s_min
    choices = []
    while x < s_max:
        choices.append(x)
        x += s_step
    choices.append(s_max)

    def _closure():
        return choice(choices)

    return _closure


def _parse_die(expr: str, addend: Optional[str]=None) -> Callable:
    amt, sides = [int(x.strip()) for x in expr.split('d')]
    if addend is not None:
        addend = int(addend.strip())

    def _closure():
        total = addend or 0
        for _ in range(amt):
            total += randint(1, sides)
        return total

    return _closure
