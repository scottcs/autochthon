"""Language related utilities."""


class Verb:
    """Represent a verb and it's tenses.

    Tense is always active, never passive.
    """
    def __init__(self, present: str, past: str):
        self.present: str = present
        self.past: str = past
