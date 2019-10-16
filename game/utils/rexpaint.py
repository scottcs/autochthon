"""REXPaint utilities."""
import dataclasses
import gzip
import pathlib
import typing

VERSION_BYTES = 4
LAYER_COUNT_BYTES = 4
LAYER_WIDTH_BYTES = 4
LAYER_HEIGHT_BYTES = 4
LAYER_KEYCODE_BYTES = 4
LAYER_FG_COLOR_BYTES = 3
LAYER_BG_COLOR_BYTES = 3
LAYER_CELL_BYTES = LAYER_KEYCODE_BYTES + LAYER_FG_COLOR_BYTES + LAYER_BG_COLOR_BYTES


class RGBColor(typing.NamedTuple):
    """Represent an RGB color."""

    r: int
    g: int
    b: int


@dataclasses.dataclass
class Cell:
    """Represent a REXPaint cell."""

    keycode: int
    fg: RGBColor
    bg: RGBColor

    def as_key(self) -> str:
        """Return a string to be used as a key in data files."""
        # NOTE: ignoring bg color for now
        return f"{self.keycode},{self.fg.r},{self.fg.g},{self.fg.b}"


@dataclasses.dataclass
class Layer:
    """Represent a REXPaint layer."""

    width: int
    height: int
    columns: typing.List[typing.List[Cell]]


@dataclasses.dataclass
class XPData:
    """Represent the data in an entire file."""

    version: int
    width: int
    height: int
    layers: typing.List[Layer]


def _bytes_to_int(arr: bytearray, offset: int, length: int) -> int:
    return int.from_bytes(arr[offset : offset + length], byteorder="little")


def _parse_layer_data(data: bytearray) -> Layer:
    offset = 0
    width = _bytes_to_int(data, offset, LAYER_WIDTH_BYTES)
    offset += LAYER_WIDTH_BYTES
    height = _bytes_to_int(data, offset, LAYER_HEIGHT_BYTES)
    offset += LAYER_HEIGHT_BYTES

    columns = []

    for x in range(width):
        col = []
        for y in range(height):
            col.append(_parse_cell_data(data[offset : offset + LAYER_CELL_BYTES]))
            offset += LAYER_CELL_BYTES
        columns.append(col)
    return Layer(width, height, columns)


def _parse_cell_data(data: bytearray) -> Cell:
    offset = 0

    keycode = _bytes_to_int(data, offset, LAYER_KEYCODE_BYTES)
    offset += LAYER_KEYCODE_BYTES

    fg_r = _bytes_to_int(data, offset, 1)
    offset += 1
    fg_g = _bytes_to_int(data, offset, 1)
    offset += 1
    fg_b = _bytes_to_int(data, offset, 1)
    offset += 1

    bg_r = _bytes_to_int(data, offset, 1)
    offset += 1
    bg_g = _bytes_to_int(data, offset, 1)
    offset += 1
    bg_b = _bytes_to_int(data, offset, 1)
    offset += 1

    return Cell(keycode, RGBColor(fg_r, fg_g, fg_b), RGBColor(bg_r, bg_g, bg_b))


def load_xp(filename: pathlib.Path) -> XPData:
    """Load a REXPaint .xp file and return its data."""
    with gzip.open(filename) as f:
        xp_bytes = f.read()

    offset = 0
    version = _bytes_to_int(xp_bytes, offset, VERSION_BYTES)
    offset += VERSION_BYTES
    layer_count = _bytes_to_int(xp_bytes, offset, LAYER_COUNT_BYTES)
    offset += LAYER_COUNT_BYTES

    layers = []

    current_largest_width = 0
    current_largest_height = 0

    for layer in range(layer_count):
        this_layer_width = _bytes_to_int(xp_bytes, offset, LAYER_WIDTH_BYTES)
        this_layer_height = _bytes_to_int(xp_bytes, offset + LAYER_WIDTH_BYTES, LAYER_HEIGHT_BYTES)

        current_largest_width = max(current_largest_width, this_layer_width)
        current_largest_height = max(current_largest_height, this_layer_height)

        layer_data_size = (
            LAYER_WIDTH_BYTES
            + LAYER_HEIGHT_BYTES
            + (LAYER_CELL_BYTES * this_layer_width * this_layer_height)
        )
        layers.append(_parse_layer_data(xp_bytes[offset : offset + layer_data_size]))
        offset += layer_data_size
    return XPData(version, current_largest_width, current_largest_height, layers)
