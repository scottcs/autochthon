"""Status effect messages."""
from gamedata.palette import MessagePalette


MsgDeath = (
    ("You die!", MessagePalette.danger),
    ("{0} dies!", MessagePalette.positive),
    ("{0} dies!", MessagePalette.default),
)
