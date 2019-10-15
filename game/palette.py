"""Color palette."""


class Base:
    """Color palette."""

    black = "#000000"
    white = "#FFFFFF"
    red = "#FF0000"
    green = "#00FF00"
    blue = "#0000FF"
    yellow = "#FFFF00"
    purple = "#FF00FF"
    cyan = "#00FFFF"
    orange = "#FFA500"
    brown = "#654321"
    dark_grey = "#333333"


class Danger:
    """Danger level colors."""

    deadly = "#FF6699"
    dangerous = "#FF6666"
    threatening = "#FFFF66"
    fair = "#AAAAAA"
    weak = "#66FFFF"
    helpless = "#666666"


class Message:
    """Message colors."""

    danger = "#FF3434"
    warning = "#FFB600"
    side_note = "#B0B0B0"
    default = "#DFDFDF"
    very_negative = "#FF8054"
    negative = "#C0AA32"
    positive = "#31CC08"
    very_positive = "#5BFFFD"
    holy_crap = "#ED2DFF"


class Item:
    """Colors for item descriptions."""

    trash = "#666666"
    common = "#AAAAAA"
    uncommon = "#66FF66"
    rare = "#9999FF"
    epic = "#CC66FF"
    legendary = "#FFA500"
    artifact = "#FF9999"


class Renderer:
    """Colors for the renderer to use."""

    beneath = "#FF62C2EA"
    remembered = "#60FFFFFF"
    visible = "#FFFFFFFF"


def color_from_class_string(class_string: str) -> str:
    """Get a palette color string from a class string like `Base.brown`."""
    palette_class, color_name = class_string.split(".")
    color: str = getattr(palette_class, color_name)
    return color
