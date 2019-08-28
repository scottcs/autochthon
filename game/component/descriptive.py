"""Descriptive components."""
from dataclasses import InitVar, dataclass
from typing import MutableSequence, Optional


@dataclass
class Name:
    """Name component."""

    first: str
    last: Optional[str] = None
    titles: Optional[MutableSequence[str]] = None
    nickname: Optional[str] = None
    proper: bool = False
    plural_str: InitVar[Optional[str]] = None

    def __post_init__(self, plural_str: Optional[str]) -> None:
        self._plural = plural_str

    @property
    def specific(self) -> str:
        """This specific entity."""
        if self.proper:
            return str(self)
        return f"the {self}"

    @property
    def generic(self) -> str:
        """A generic version of this entity."""
        if self.proper:
            return str(self)
        if str(self).lower()[0] in "aeiou":
            return f"an {self}"
        return f"a {self}"

    @property
    def plural(self) -> str:
        """Many of this entity."""
        if self._plural is None:
            return f"{self}s"
        return self._plural

    def __str__(self) -> str:
        name = f"{self.first}"
        if self.nickname:
            name = f'{name} "{self.nickname}"'
        if self.last:
            name = f"{name} {self.last}"
        if self.titles:
            if not self.titles[0].startswith("the "):
                name += ":"
            name = f'{name} {", ".join(self.titles)}'
        return name


# Ideas for making fatter components:
# Name is not a component, but a type similar to the above class.
# Same with Description.
# Any stats relevant to the Item (or Species) should be stored on the component.
# TODO: look for code that always lumps the same components together and consider making them fat
#
# class Item:
#     """An item."""
#
#     def __init__(self, name: Name, description: Description, weight: int=0, rarity:
#     Rarity=Rarity.common) -> None:
#         pass
#
# class Species:
#     """A species."""
#
#     def __init__(
#         self, name: Name, description: Description, rarity: Rarity=Rarity.common
#     ) -> None:
#         pass
