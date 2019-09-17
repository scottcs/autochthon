"""Status effect messages."""
import game.constants.palette

MsgDeath = (
    ("You die!", game.constants.palette.MessagePalette.danger),
    ("{0} dies!", game.constants.palette.MessagePalette.positive),
    ("{0} dies!", game.constants.palette.MessagePalette.default),
)
