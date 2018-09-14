"""Action components."""
from dataclasses import dataclass
from gamedata.base_engine_values import TIME_UNITS_PER_TURN


@dataclass
class Actor:
    """Actor components use time units of energy to take actions."""
    time_units: int = 0
    rate: int = TIME_UNITS_PER_TURN

    def __str__(self) -> str:
        return f"{self.time_units} ({self.rate}/turn)"
