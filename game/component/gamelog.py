"""Game log components."""
from typing import List, Optional


class CombatLog:
    """Component for the combat log."""
    def __init__(self, lines: Optional[List[str]]=None):
        self.lines = lines or []
