"""Render utilities."""
import typing

import constants.tile_ids


class _TileCache:
    """Tile Cache."""

    def __init__(self) -> None:
        self._cache: dict = {}

    def id_from_name(self, name: str) -> int:
        """Get a tile ID from its name."""
        id_ = self._cache.get(name, None)
        if id_ is None:
            for key, data in constants.tile_ids.TILE_IDS.items():
                if data["name"] == name:
                    id_ = key
                    self._cache[name] = id_
                    break
        if id_ is None:
            raise KeyError(f"Name: {name} not found in tile ids.")
        return int(id_)

    @staticmethod
    def data_from_id(id_: int) -> dict:
        """Get tile data from its id."""
        return constants.tile_ids.TILE_IDS[str(id_)]

    def data_from_name(self, name: str) -> dict:
        """Get tile data from its name."""
        return constants.tile_ids.TILE_IDS[str(self.id_from_name(name))]

    @staticmethod
    def iter_names() -> typing.Generator[str, None, None]:
        """Iterate over tile names."""
        for data in constants.tile_ids.TILE_IDS.values():
            yield data["name"]


TileCache = _TileCache()
