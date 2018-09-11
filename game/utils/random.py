"""Functions for randomness."""
from __future__ import annotations
import hashlib
import logging
from pathlib import Path
import random
import re
from typing import Any, Callable, Optional, Sequence

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

WEIGHTED_DEF = re.compile(r'(?<=^weighted\(\()([^)]+)\), \(([^)]+)\)\)')
STEP_DEF = re.compile(r'(?<=^step\()([^)]+)\)')
DIE_DEF = re.compile(r'(\d+d\d+)([+-]\d+)?')
WORDS_FILE = Path('/usr/share/dict/words')  # TODO: replace with one in this repo with game terms?


######################################################################
# From `clubsandwich`:
#
# Implementation of the PCG random number generator, Python OO style.
#
# For the original docs, read
# `this <http://www.pcg-random.org/using-pcg-c-basic.html>`_.
######################################################################


def _uint32(n: int) -> int:
    return n & 0xffffffff


def _uint64(n: int) -> int:
    return n & 0xffffffffffffffff


class PCG32Generator:
    """Implementation of the PCG random number generator, Python OO style."""
    __slots__ = ['state', 'inc']

    def __init__(self, state: int, seq: int) -> None:
        """
        :param state: Any 64-bit value. This is the "current state" of the
                      generator within the output sequence. The RNG iterates
                      through all 2^64 possible internal states.
        :param seq: Any 64-bit value (only 63 bits are significant). This value
                    defines which of the 2^63 possible random sequences the
                    current state is iterating through; it holds the same value
                    over the lifetime of the RNG.

        Different values for sequence constant cause the generator to produce a
        different (and unique) sequence of random numbers (sometimes called the
        stream). In other words, it's as if you have 2^63 different RNGs available,
        and this constant lets you choose which one you're using.

        You can create as many separate RNGs as you like. If you give them
        different sequence constants, they will be independent and uncorrelated
        with each other (i.e., their sequences will not overlap at all).
        """
        self.state = 0
        self.inc = _uint64(seq << 1) | 1
        self._advance()
        self.state = _uint64(self.state + state)
        self._advance()

    def _advance(self) -> int:
        old_state = self.state
        self.state = _uint64(old_state * 6364136223846793005 + self.inc)
        xor_shifted = _uint32(((old_state >> 18) ^ old_state) >> 27)
        rot = _uint32(old_state >> 59)
        return _uint32((xor_shifted >> rot) | (xor_shifted << ((-rot) & 31)))

    def get_next_uint32(self) -> int:
        """
        Mutates internal state and returns the next random value in the sequence,
        a 32-bit unsigned integer.
        """
        return self._advance()

    def get_next_uint(self, bound: int) -> int:
        """
        :param int bound: Max value (exclusive)

        Return a value between zero (inclusive) and *bound* (exclusive).
        """
        # To avoid bias, we need to make the range of the RNG a multiple of
        # bound, which we do by dropping output less than a threshold.
        # A naive scheme to calculate the threshold would be to do
        #
        # uint32_t threshold = 0x100000000ull % bound;
        #
        # but 64-bit div/mod is slower than 32-bit div/mod (especially on
        # 32-bit platforms). In essence, we do
        #
        # uint32_t threshold = (0x100000000ull-bound) % bound;
        #
        # because this version will calculate the same modulus, but the LHS
        # value is less than 2^32.
        bound = _uint32(bound)
        threshold = _uint32(-bound) % bound

        # Uniformity guarantees that this loop will terminate. In practice, it
        # should usually terminate quickly; on average (assuming all bounds are
        # equally likely), 82.25% of the time, we can expect it to require just
        # one iteration. In the worst case, someone passes a bound of 2^31 + 1
        # (i.e., 2147483649), which invalidates almost 50% of the range. In
        # practice, bounds are typically small and only a tiny amount of the range
        # is eliminated.
        while True:
            val = self.get_next_uint32()
            if val >= threshold:
                return val % bound


class GameRNG:
    """RNG with game related function."""

    def __init__(self, name: str, rng: Any) -> None:
        self.name = name
        self._rng = rng

    def rand(self, lower: Optional[int]=None, upper: Optional[int]=None) -> int:
        """Return a random integer in range [lower, upper], including both endpoints."""
        if upper is None:
            if lower is None:
                return self._rng.get_next_uint32()
            else:
                return self._rng.get_next_uint(lower + 1)
        else:
            if lower is None:
                raise RuntimeError('cannot have upper without lower')
            if lower > upper:
                raise RuntimeError('lower must be <= upper')
            if lower == upper:
                return lower
            return lower + self._rng.get_next_uint((upper - lower) + 1)

    def percent(self, percent: float, precision: Optional[int]=1000) -> bool:
        """Return whether not a percentage roll succeeds."""
        return self._rng.get_next_uint(precision) < (percent * precision)

    def choice(self, options: Sequence[Any]) -> Any:
        """Return a random choice amongst the options."""
        return options[self.rand(len(options) - 1)]

    def coin(self) -> bool:
        """Return the result of a coin flip."""
        return bool(self.rand(1))


class RNGCache:
    """Random number generator cache."""

    seed: str = None
    _rng: PCG32Generator = None
    _cache: dict = {}
    _collision_check: dict = {}

    @classmethod
    def init(cls, seed: Optional[str]=None) -> None:
        """Initialize the cache."""
        cls._cache = {}
        if not seed:
            seed = cls.get_random_words()
        cls.seed = seed
        cls._collision_check[0] = '_ZERO_'
        cls._rng = PCG32Generator(cls.string_hash(cls.seed), 0)

    @classmethod
    def get(cls, stream: Optional[str]=None) -> GameRNG:
        """Get a sub-rng."""
        if cls._rng is None:
            raise RuntimeError('Attempt to get RNG from uninitialized cache')
        if not stream:
            stream = cls.get_random_words()
        if stream not in cls._cache:
            rng = GameRNG(stream, PCG32Generator(cls.string_hash(cls.seed),
                                                 cls.string_hash(stream)))
            cls._cache[stream] = rng
        return cls._cache[stream]

    @classmethod
    def string_hash(cls, s: str) -> int:
        """Convert a string into a deterministic hash integer."""
        h = int(hashlib.sha1(s.encode('utf-8')).hexdigest(), 16)
        while h in cls._collision_check and cls._collision_check[h] != s:
            log.warning(f'Collision between {s} and {cls._collision_check[h]}')
            h += 1
        cls._collision_check.setdefault(h, s)
        return h

    @classmethod
    def get_random_words(cls, count: int=3) -> str:
        """Get a string of `count` random words, CamelCased."""
        result = ''
        with WORDS_FILE.open() as f:
            lines = f.readlines()
        for x in range(count):
            if cls._rng is None:
                word = lines[random.randrange(0, len(lines))].strip()
            else:
                word = lines[cls._rng.get_next_uint(len(lines))].strip()
            result += word.capitalize()
        return result


def _parse_weighted(rng: GameRNG, items_str: str, weights_str: str) -> Callable:
    items = [i.strip(' \'"') for i in items_str.split(',')]
    weights = [int(w.strip()) for w in weights_str.split(',')]
    choices = []
    for i, item in enumerate(items):
        choices.extend([item for _ in range(weights[i])])

    def _closure():
        return rng.choice(choices)

    return _closure


def _parse_step(rng: GameRNG, expr: str) -> Callable:
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
        return rng.choice(choices)

    return _closure


def _parse_die(rng: GameRNG, expr: str, addend: Optional[str]=None) -> Callable:
    amt, sides = [int(x.strip()) for x in expr.split('d')]
    if addend is not None:
        addend = int(addend.strip())

    def _closure():
        total = addend or 0
        for _ in range(amt):
            total += rng.rand(1, sides)
        return total

    return _closure


def parse(text: str, rng: GameRNG) -> Optional[Callable]:
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
        func = _parse_weighted(rng, *found.groups())
    else:
        found = STEP_DEF.search(text)
        if found:
            func = _parse_step(rng, *found.groups())
        else:
            found = DIE_DEF.search(text)
            if found:
                func = _parse_die(rng, *found.groups())
    return func
