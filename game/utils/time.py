"""Time-based utilities."""
from __future__ import annotations
from typing import Optional, Union, Any

MOMENTS_PER_TURN = 10


class GameTime:
    """Represents an amount of in-game time.

    Can be represented as an integer or a float. Float representation is
    considered as TURNS.MOMENTS, while integers are simply MOMENTS.

    """
    def __init__(self,
                 turn: Optional[Union[GameTime, float, int]]=None,
                 moment: Optional[int]=None) -> None:
        self._last_time = 0
        if turn is None:
            turn = 0
        if not isinstance(turn, (GameTime, float, int)):
            raise TypeError(f'Cannot convert {type(turn)} to GameTime')
        if isinstance(turn, GameTime):
            moment = turn._time
            turn = 0
        elif isinstance(turn, float):
            turn, moment = [int(x) for x in str(turn).split('.')]
        else:
            if moment is None:
                moment = turn
                turn = 0
            else:
                moment = moment or 0
        self._time: int = turn * MOMENTS_PER_TURN + moment

    @property
    def turn(self) -> int:
        """Current turn."""
        return self._time // MOMENTS_PER_TURN

    @property
    def moment(self) -> int:
        """Current moment."""
        return self._time - self.turn * MOMENTS_PER_TURN

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

    def __bool__(self) -> bool:
        return bool(self._time)

    def __repr__(self) -> str:
        return f'{self.turn}.{self.moment}'
