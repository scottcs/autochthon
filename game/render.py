"""Render utilities."""
import logging
import pathlib
import typing

import bearlibterminal.terminal as blt

import game.data
import game.types
import game.utils.geometry

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
        self._cache: typing.Dict[typing.Sequence[typing.Union[str, int]], int] = {}

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
                result: str = [k for k in data.keys() if k not in ("offset", "variations")][0]
                return result
            except IndexError:
                return None

    def _get_local_tile_offset(
        self, tile_data: typing.Dict[str, typing.Any], variant: int, direction: str, frame: int
    ) -> typing.Optional[int]:
        local_offset: typing.Optional[int] = tile_data.get("offset", None)
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


def get_conversion_value(category: str, index: int) -> float:
    """Get the conversion value of a tileset to the grid."""
    if category == "font":
        size: int = game.data.tileset["font"]["size"][index]
    else:
        size = game.data.tileset["tilesets"][category]["size"][index]
        size *= game.data.config["tile_scale"]
    cell_pixel_size: int = game.data.tileset["window"]["cellsize"][index]
    return size / cell_pixel_size


def snap_tile_to_grid_x(category: str, tile_x: int) -> int:
    """Get the snapped grid x coordinate for a tile (this is lossy)."""
    return int(tile_x * get_conversion_value(category, 0))


def snap_tile_to_grid_y(category: str, tile_y: int) -> int:
    """Get the snapped grid y coordinate for a tile (this is lossy)."""
    return int(tile_y * get_conversion_value(category, 1))


def grid_to_tile_x(category: str, grid_x: int) -> int:
    """Get the tile x coord for a grid x coord (several grid coords return the same tile coord)."""
    return int(grid_x / get_conversion_value(category, 0))


def grid_to_tile_y(category: str, grid_y: int) -> int:
    """Get the tile y coord for a grid y coord (several grid coords return the same tile coord)."""
    return int(grid_y / get_conversion_value(category, 1))


class BaseRenderer:
    """Base renderer class."""

    def __init__(self) -> None:
        self.width: int = game.data.tileset["window"]["width"]
        self.height: int = game.data.tileset["window"]["height"]
        self.center = [self.width // 2, self.height // 2]
        log.debug(f"BaseRenderer w: {self.width}, h: {self.height}, c: {self.center}")
        self.font_size = game.data.tileset["font"]["size"]
        self.font_file = pathlib.Path(f"{game.data.FONT_PATH}/{game.data.tileset['font']['file']}")
        self.title = f"{game.data.config['title']} v{game.VERSION}"

    def refresh(self) -> None:
        """Refresh graphics."""
        raise NotImplementedError()

    def clear_layer(
        self, layer: int, rect: typing.Optional[game.utils.geometry.Rect] = None
    ) -> None:
        """Clear the given layer or part of the layer."""
        raise NotImplementedError()

    @staticmethod
    def draw_tile(x: int, y: int, tile_id: int) -> None:
        """Draw a tile."""
        raise NotImplementedError()

    def draw_text(self, x: int, y: int, text: str) -> None:
        """Draw some text."""
        raise NotImplementedError()

    def draw_gamelog(self, x: int, y: int, lines: typing.Sequence[game.types.LogLine]) -> None:
        """Draw a game log line."""
        raise NotImplementedError()

    def close(self) -> None:
        """Close all windows."""
        raise NotImplementedError()

    @staticmethod
    def colorize_text(text: str, color: str) -> str:
        """Return a colorized string of text for BearLibTerminal."""
        raise NotImplementedError()

    def colorize_gamelog(self, lines: typing.Sequence[game.types.LogLine]) -> str:
        """Return a colorized string of log lines for BearLibTerminal."""
        raise NotImplementedError()

    def set_color(self, color: str) -> None:
        """Set the color for drawing."""
        raise NotImplementedError()

    def reset_color(self) -> None:
        """Set the color for drawing to the default value."""
        raise NotImplementedError()

    def set_layer(self, layer: int) -> None:
        """Set the layer for drawing."""
        raise NotImplementedError()


class BearLibRenderer(BaseRenderer):
    """Bearlibterminal renderer."""

    def __init__(self) -> None:
        super().__init__()
        if not blt.open():
            log.critical("Unable to initialize terminal window!")
        window_size = f"size={self.width}x{self.height}"
        cell_pixel_w, cell_pixel_h = game.data.tileset["window"]["cellsize"]
        cell_size = f"cellsize={cell_pixel_w}x{cell_pixel_h}"
        blt.set(f"window: {window_size}, title='{self.title}', {cell_size}")
        blt.set(f"font: {self.font_file}, size={str(self.font_size[0])}x{str(self.font_size[1])}")
        blt.composition(blt.TK_ON)
        blt.color("white")
        self._load_tilesets()

    @staticmethod
    def _load_tilesets() -> None:
        tile_scale = game.data.config["tile_scale"]
        for tileset_name, item in game.data.tileset["tilesets"].items():
            item_file = pathlib.Path(f"{game.data.TILES_PATH}/{item['file']}")
            load_str = f"{item['offset']}: {item_file}"
            width, height = item["size"]
            load_str += f", size={str(width)}x{str(height)}"
            if tile_scale != 1:
                width *= tile_scale
                height *= tile_scale
                load_str += f", resize={str(width)}x{str(height)}, resize-filter=nearest"
            load_str += f", align={item['align']}"
            cell_pixel_w, cell_pixel_h = game.data.tileset["window"]["cellsize"]
            x = width // cell_pixel_w
            y = height // cell_pixel_h
            load_str += f", spacing={str(x)}x{str(y)}"
            blt.set(load_str)

    def refresh(self) -> None:
        """Refresh graphics."""
        blt.refresh()

    def clear_layer(
        self, layer: int, rect: typing.Optional[game.utils.geometry.Rect] = None
    ) -> None:
        """Clear the given layer, or part of the layer."""
        blt.layer(layer)
        if rect is None:
            blt.clear_area(0, 0, self.width, self.height)
        else:
            blt.clear_area(rect.x1, rect.x2, rect.w, rect.h)

    def set_color(self, color: str) -> None:
        """Set the color for drawing."""
        blt.color(color)

    def reset_color(self) -> None:
        """Set the color for drawing to the default value."""
        blt.color("white")

    def set_layer(self, layer: int) -> None:
        """Set the layer for drawing."""
        blt.layer(layer)

    @staticmethod
    def draw_tile(x: int, y: int, tile_id: int) -> None:
        """Draw on the given layer."""
        blt.put(x, y, tile_id)

    def draw_text(self, x: int, y: int, text: str) -> None:
        """Draw some text."""
        blt.puts(x, y, text)

    def draw_gamelog(self, x: int, y: int, lines: typing.Sequence[game.types.LogLine]) -> None:
        """Draw a game log line."""
        self.draw_text(x, y, self.colorize_gamelog(lines))

    def close(self) -> None:
        """Close all windows."""
        blt.close()

    @staticmethod
    def colorize_text(text: str, color: str) -> str:
        """Return a colorized string of text for BearLibTerminal."""
        return f"[color={color}]{text}[/color]"

    def colorize_gamelog(self, lines: typing.Sequence[game.types.LogLine]) -> str:
        """Return a colorized string of log lines for BearLibTerminal."""
        return "".join([self.colorize_text(l.message, l.color) for l in lines])
