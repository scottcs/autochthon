"""Descriptive components."""
from typing import Optional, List


class Name:
    """Name component."""
    def __init__(self,
                 first: str,
                 last: Optional[str]=None,
                 titles: Optional[List[str]]=None) -> None:
        self.first: str = first
        self.last: Optional[str] = last
        self.titles: Optional[List[str]] = titles

    def __str__(self) -> str:
        name = f'{self.first}'
        if self.last:
            name = f'{name} {self.last}'
        if self.titles:
            if not self.titles[0].startswith('the'):
                name += ','
            name = f'{name} {", ".join(self.titles)}'
        return name
