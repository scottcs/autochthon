"""Render utilities."""
import logging
import typing

import game.data

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def get_facing(dx: int, dy: int) -> str:
    """Get a facing/direction string from an x and y movement coordinate."""
    if dx < 0:
        if dy < 0:
            facing = "nw"
        elif dy > 0:
            facing = "sw"
        else:
            facing = "w"
    elif dx > 0:
        if dy < 0:
            facing = "ne"
        elif dy > 0:
            facing = "se"
        else:
            facing = "e"
    else:
        if dy < 0:
            facing = "n"
        else:
            facing = "s"
    return facing


class _TileCache:
    """Tile Cache."""

    def __init__(self) -> None:
        self._cache: typing.Dict[typing.Sequence, int] = {}

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
        direction = self._get_direction(category, name, variant, direction)
        frame = frame or 0
        key_ = (category, name, variant, direction, frame)
        id_ = self._cache.get(key_, None)

        if id_ is None:
            main_offset = int(game.data.tileset["tilesets"][category]["offset"], 0)
            category_data = game.data.tile_ids.get(category, None)
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

    def _get_direction(
        self,
        category: str,
        name: str,
        variant: typing.Optional[int],
        direction: typing.Optional[str] = None,
    ) -> str:
        """Get the best direction for the tile."""
        category_data = game.data.tile_ids.get(category, None)
        if category_data:
            tile_data = category_data.get(name, None)
            if tile_data:
                if "variations" in tile_data:
                    if variant is not None:
                        direction = self._find_best_direction(
                            tile_data["variations"][variant], direction
                        )
                else:
                    direction = self._find_best_direction(tile_data, direction)
        if direction is None:
            raise KeyError(f"Direction for ({category}, {name}, {variant}) not found")
        return direction

    @staticmethod
    def _find_best_direction(
        data: typing.Dict[typing.Any, typing.Any], direction: typing.Optional[str] = None
    ) -> typing.Optional[str]:
        if direction is not None:
            if direction in data:
                return direction
            elif "e" in data and direction in ("ne", "se"):
                return "e"
            elif "w" in data and direction in ("nw", "sw"):
                return "w"
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

    def _get_local_tile_offset(
        self, tile_data: typing.Dict[str, typing.Any], variant: int, direction: str, frame: int
    ) -> typing.Optional[int]:
        local_offset = tile_data.get("offset", None)
        if local_offset is None:
            return None
        try:
            sequence = tile_data["variations"][variant][direction]
        except KeyError:
            try:
                sequence = tile_data[direction]
            except KeyError:
                found_direction = self._find_best_direction(tile_data)
                if found_direction is None:
                    raise RuntimeError(f"No direction found for {tile_data}")
                sequence = tile_data[found_direction]
        if isinstance(sequence, int):
            local_offset += sequence
        else:
            # assumes sequence is a list
            local_offset += sequence[frame % len(sequence)]
        return local_offset


TileCache = _TileCache()
