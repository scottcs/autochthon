"""Color palette."""
from enum import IntEnum


class Palette(IntEnum):
    """Color palette."""

    black = 0x000000
    white = 0xFFFFFF
    red = 0xFF0000
    green = 0x00FF00
    blue = 0x0000FF
    yellow = 0xFFFF00
    purple = 0xFF00FF
    cyan = 0x00FFFF
    orange = 0xFFA500
    brown = 0x654321
    dark_grey = 0x333333


class DangerPalette(IntEnum):
    """Danger level colors."""

    deadly = 0xFF6699
    dangerous = 0xFF6666
    threatening = 0xFFFF66
    fair = 0xAAAAAA
    weak = 0x66FFFF
    helpless = 0x666666


class MessagePalette(IntEnum):
    """Message colors."""

    danger = 0xFF6666
    warning = 0xFFFF66
    side_note = 0x666666
    default = 0xAAAAAA
    very_negative = 0xFF6699
    negative = 0x654321
    positive = 0x669966
    very_positive = 0x66FF66
    holy_crap = 0xFF66FF


class ItemPalette(IntEnum):
    """Colors for item descriptions."""

    trash = 0x666666
    common = 0xAAAAAA
    uncommon = 0x66FF66
    rare = 0x9999FF
    epic = 0xCC66FF
    legendary = 0xFFA500
    artifact = 0xFF9999
