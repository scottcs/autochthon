"""Render utilities."""
import json
from pathlib import Path

TILE_IDS = Path('static/img/oryx_ur/tile_ids.json')


class _TileCache:
    """Tile Cache."""
    def __init__(self) -> None:
        self._cache = {}
        with TILE_IDS.open() as f:
            self._ids = json.load(f)

    def id_from_name(self, name: str) -> int:
        """Get a tile ID from its name."""
        id_ = self._cache.get(name, None)
        if id_ is None:
            for key, data in self._ids.items():
                if data['name'] == name:
                    id_ = key
                    self._cache[name] = id_
                    break
        return id_


TileCache = _TileCache()
