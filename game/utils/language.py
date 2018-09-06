"""Language related utilities."""
from typing import Tuple, Any, AbstractSet, Iterable

from game.types import Entity


class Verb:
    """Represent a verb and it's tenses.

    Tense is always active, never passive.
    """
    def __init__(self, present: str, past: str) -> None:
        self.present: str = present
        self.past: str = past


def msg(players: AbstractSet[Entity],
        entities: Iterable[Entity],
        messages: tuple,
        *args: Any
        ) -> Tuple[str, int]:
    """Determine the message based on which entity, if any, is the player."""
    for i, ent in enumerate(entities):
        if ent in players:
            return messages[i][0].format(*args), messages[i][1]
    return messages[-1][0].format(*args), messages[-1][1]
