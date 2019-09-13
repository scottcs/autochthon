"""Language related utilities."""
import dataclasses
import typing

import game.types


@dataclasses.dataclass
class Verb:
    """Represent a verb and it's tenses.

    Tense is always active, never passive.
    """

    present: str
    past: str


def msg(
    players: typing.AbstractSet[game.types.Entity],
    entities: typing.Iterable[game.types.Entity],
    messages: tuple,
    *args: typing.Any
) -> typing.Tuple[str, int]:
    """Determine the message based on which entity, if any, is the player."""
    for i, ent in enumerate(entities):
        if ent in players:
            return messages[i][0].format(*args), messages[i][1]
    return messages[-1][0].format(*args), messages[-1][1]
