"""Descriptive components."""
from typing import Optional, List


class Name:
    """Name component."""
    def __init__(self,
                 first: str,
                 last: Optional[str]=None,
                 titles: Optional[List[str]]=None,
                 nickname: Optional[str]=None,
                 proper: bool=False,
                 plural: Optional[str]=None) -> None:
        self.first: str = first
        self.nickname: Optional[str] = nickname
        self.last: Optional[str] = last
        self.titles: Optional[List[str]] = titles
        self.proper: bool = proper
        self._plural: Optional[str] = plural

    @property
    def specific(self) -> str:
        """This specific entity."""
        if self.proper:
            return str(self)
        return f'the {self}'

    @property
    def generic(self) -> str:
        """A generic version of this entity."""
        if self.proper:
            return str(self)
        if str(self).lower()[0] in 'aeiou':
            return f'an {self}'
        return f'a {self}'

    @property
    def plural(self) -> str:
        """Many of this entity."""
        if self._plural is None:
            return f'{self}s'
        return self._plural

    def __str__(self) -> str:
        name = f'{self.first}'
        if self.nickname:
            name = f'{name} "{self.nickname}"'
        if self.last:
            name = f'{name} {self.last}'
        if self.titles:
            if not self.titles[0].startswith('the '):
                name += ':'
            name = f'{name} {", ".join(self.titles)}'
        return name
