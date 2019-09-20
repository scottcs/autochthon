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

    danger = "#FF6666"
    warning = "#FFFF66"
    side_note = "#666666"
    default = "#AAAAAA"
    very_negative = "#FF6699"
    negative = "#654321"
    positive = "#669966"
    very_positive = "#66FF66"
    holy_crap = "#FF66FF"


class Item:
    """Colors for item descriptions."""

    trash = "#666666"
    common = "#AAAAAA"
    uncommon = "#66FF66"
    rare = "#9999FF"
    epic = "#CC66FF"
    legendary = "#FFA500"
    artifact = "#FF9999"


def color_from_class_string(class_string: str) -> str:
    """Get a palette color string from a class string like `Base.brown`."""
    palette_class, color_name = class_string.split(".")
    return getattr(palette_class, color_name)
