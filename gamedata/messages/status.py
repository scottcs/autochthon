"""Status effect messages."""
import gamedata.palette

MsgDeath = (
    ("You die!", gamedata.palette.MessagePalette.danger),
    ("{0} dies!", gamedata.palette.MessagePalette.positive),
    ("{0} dies!", gamedata.palette.MessagePalette.default),
)
