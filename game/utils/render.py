"""Render utilities."""
import logging
import typing

import game.const.tile_ids
import game.const.tileset

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class _TileCache:
    """Tile Cache."""

    def __init__(self) -> None:
        self._cache: typing.Dict[typing.Sequence, int] = {}
        self._default_direction_cache: typing.Dict[typing.Sequence, str] = {}

    def get(
        self,
        category: str,
        name: str,
        variant: typing.Optional[int] = None,
        direction: typing.Optional[str] = None,
        frame: typing.Optional[int] = None,
    ) -> int:
        """Get a tile id for the specified tile."""
        variant = variant or 0
        direction = direction or self._get_default_direction(category, name, variant)
        frame = frame or 0
        key_ = (category, name, variant, direction, frame)
        id_ = self._cache.get(key_, None)

        if id_ is None:
            main_offset = int(game.const.tileset.DATA["tilesets"][category]["offset"], 0)
            category_data = game.const.tile_ids.DATA.get(category, None)
            if category_data:
                tile_data = category_data.get(name, None)
                if tile_data:
                    local_offset = self._get_local_tile_offset(
                        tile_data, variant, direction, frame
                    )
                    if local_offset is not None:
                        id_ = main_offset + local_offset
                        self._cache[key_] = id_
        if id_ is None:
            raise KeyError(f"ID {key_} not found in tile ids.")
        return id_

    def _get_default_direction(self, category: str, name: str, variant: int) -> str:
        key_ = (category, name, variant)
        direction = self._default_direction_cache.get(key_, None)
        if direction is None:
            category_data = game.const.tile_ids.DATA.get(category, None)
            if category_data:
                tile_data = category_data.get(name, None)
                if tile_data:
                    if "variations" in tile_data:
                        direction = self._find_best_direction(tile_data["variations"][variant])
                    else:
                        direction = self._find_best_direction(tile_data)
                    if direction is not None:
                        self._default_direction_cache[key_] = direction
        if direction is None:
            raise KeyError(f"Direction {key_} not found in tile ids.")
        return direction

    @staticmethod
    def _find_best_direction(data: typing.Dict[typing.Any, typing.Any]) -> typing.Optional[str]:
        if "base" in data:
            return "base"
        elif "e" in data:
            return "e"
        elif "s" in data:
            return "s"
        elif "n" in data:
            return "n"
        elif "w" in data:
            return "w"
        else:
            try:
                return [k for k in data.keys() if k not in ("offset", "variations")][0]
            except IndexError:
                return None

    @staticmethod
    def _get_local_tile_offset(
        tile_data: typing.Dict[str, typing.Any], variant: int, direction: str, frame: int
    ) -> typing.Optional[int]:
        local_offset = tile_data.get("offset", None)
        if local_offset is None:
            return None
        try:
            sequence = tile_data["variations"][variant][direction]
        except KeyError:
            sequence = tile_data[direction]
        if isinstance(sequence, int):
            local_offset += sequence
        else:
            # assumes sequence is a list
            local_offset += sequence[frame]
        return local_offset


TileCache = _TileCache()
