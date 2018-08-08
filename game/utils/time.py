"""Time-based utilities."""
from __future__ import annotations
from typing import Optional, Union, Any

MOMENTS_PER_TURN = 100


class GameTime:
    """Represents an amount of in-game time.

    Can be represented as an integer or a float. Float representation is
    considered as TURNS.MOMENTS, while integers are simply MOMENTS.

    """
    def __init__(self, time: Optional[Union[GameTime, int]]=None) -> None:
        self._last_time = 0
        if time is None:
            time = 0
        if not isinstance(time, (GameTime, int)):
            raise TypeError(f'Cannot convert {type(time)} to GameTime')
        if isinstance(time, GameTime):
            time = time.total_moments
        self._time: int = time

    @property
    def turn(self) -> int:
        """Current turn."""
        return int(self._time / MOMENTS_PER_TURN)

    @property
    def moment(self) -> int:
        """Current moment."""
        return abs(self._time - self.turn * MOMENTS_PER_TURN)

    @property
    def total_moments(self):
        """Total moments."""
        return self._time

    @property
    def last_change(self) -> GameTime:
        """Amount of time changed since last time."""
        return GameTime(-1 * (self._last_time - self._time))

    @property
    def last_time(self) -> GameTime:
        """Last time before most recent change."""
        return GameTime(self._last_time)

    def __iadd__(self, other: Any) -> GameTime:
        self._last_time = self._time
        self._time += GameTime(other)._time
        return self

    def __isub__(self, other: Any) -> GameTime:
        self._last_time = self._time
        self._time -= GameTime(other)._time
        return self

    def __add__(self, other: Any) -> GameTime:
        return GameTime(self._time + GameTime(other)._time)

    def __sub__(self, other: Any) -> GameTime:
        return GameTime(self._time - GameTime(other)._time)

    def __lt__(self, other: Any) -> bool:
        return self._time < GameTime(other)._time

    def __eq__(self, other: Any) -> bool:
        return self._time == GameTime(other)._time

    def __le__(self, other: Any) -> bool:
        return self._time <= GameTime(other)._time

    def __neg__(self) -> GameTime:
        return GameTime(-self._time)

    def __bool__(self) -> bool:
        return bool(self._time)

    def __repr__(self) -> str:
        return f'{self._time / MOMENTS_PER_TURN}'
