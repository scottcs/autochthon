"""Tests for the seeded RNG and the randomness-expression parser in game.utils.random."""

from __future__ import annotations

import pytest

from game.utils.random import GameRNG, PCG32Generator, parse


def _rng(state: int = 0, seq: int = 0) -> GameRNG:
    """Build a GameRNG on a freshly seeded PCG32 stream."""
    return GameRNG("test", PCG32Generator(state, seq))


def test_pcg32_is_deterministic_for_a_seed() -> None:
    """The same (state, seq) reproduces the same uint32 sequence."""
    a = PCG32Generator(42, 0)
    b = PCG32Generator(42, 0)
    assert [a.get_next_uint32() for _ in range(5)] == [b.get_next_uint32() for _ in range(5)]


def test_pcg32_known_sequence() -> None:
    """Pin the start of the (42, 0) stream so an accidental behavior change is caught."""
    gen = PCG32Generator(42, 0)
    assert [gen.get_next_uint32() for _ in range(4)] == [
        565663470,
        3244226384,
        2504567229,
        903561869,
    ]


def test_pcg32_different_sequences_diverge() -> None:
    """Different seq values give independent streams from the same state."""
    a = PCG32Generator(42, 0)
    b = PCG32Generator(42, 1)
    assert a.get_next_uint32() != b.get_next_uint32()


def test_get_next_uint_stays_below_bound() -> None:
    """Bounded draws never reach the bound itself."""
    gen = PCG32Generator(7, 0)
    assert all(gen.get_next_uint(6) < 6 for _ in range(200))


def test_rand_is_inclusive_on_both_ends() -> None:
    """Both endpoints of rand(lo, hi) are reachable."""
    rng = _rng(99)
    assert {rng.rand(1, 2) for _ in range(50)} == {1, 2}


def test_rand_equal_bounds_returns_that_value() -> None:
    """Equal bounds short-circuit to that value."""
    assert _rng().rand(5, 5) == 5


def test_rand_upper_without_lower_is_an_error() -> None:
    """An upper bound with no lower bound is rejected."""
    with pytest.raises(RuntimeError, match="cannot have upper without lower"):
        _rng().rand(None, 5)


def test_rand_rejects_inverted_bounds() -> None:
    """Inverted bounds are rejected."""
    with pytest.raises(RuntimeError, match="lower must be <= upper"):
        _rng().rand(5, 2)


def test_parse_constant_die_has_no_spread() -> None:
    """Constant dice have no spread: 3d1+2 always totals 5 (three 1-sided dice plus 2)."""
    roll = parse("3d1+2", _rng())
    assert roll is not None
    assert {roll() for _ in range(20)} == {5}


def test_parse_single_unit_die() -> None:
    """A single one-sided die always rolls 1."""
    roll = parse("1d1", _rng())
    assert roll is not None
    assert roll() == 1


def test_parse_die_respects_bounds() -> None:
    """Die rolls respect their bounds: 2d6+1 stays within [3, 13]."""
    roll = parse("2d6+1", _rng(123))
    assert roll is not None
    assert all(3 <= roll() <= 13 for _ in range(200))


def test_parse_weighted_only_yields_listed_items() -> None:
    """A weighted choice never returns a value outside its item list."""
    roll = parse("weighted(('a', 'b', 'c'), (1, 1, 2))", _rng(5))
    assert roll is not None
    assert {roll() for _ in range(100)} <= {"a", "b", "c"}


def test_parse_step_yields_only_grid_points() -> None:
    """Stepped values land only on the grid points of step(-0.1, 0.1, 0.1)."""
    roll = parse("step(-0.1, 0.1, 0.1)", _rng(5))
    assert roll is not None
    assert {round(roll(), 5) for _ in range(100)} <= {-0.1, 0.0, 0.1}


def test_parse_unrecognized_text_returns_none() -> None:
    """Text matching no known form parses to None rather than raising."""
    assert parse("not a dice expression", _rng()) is None
