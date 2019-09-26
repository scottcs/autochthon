"""Status effect messages."""
import game.palette

Death = (
    ("You die!", game.palette.Message.danger),
    ("{0} dies!", game.palette.Message.positive),
    ("{0} dies!", game.palette.Message.default),
)
