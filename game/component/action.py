"""Action components."""
from gamedata.base_engine_values import TIME_UNITS_PER_TURN


class Actor:
    """Actor components use time units of energy to take actions."""

    def __init__(self, initial_units: int = 0, rate: int = TIME_UNITS_PER_TURN) -> None:
        self.time_units: int = initial_units
        self.rate: int = rate

    def __str__(self) -> str:
        return f"{self.time_units} (+{self.rate}/turn)"
