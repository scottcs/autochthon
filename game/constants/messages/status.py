"""Status effect messages."""
import game.constants.palette

Death = (
    ("You die!", game.constants.palette.Message.danger),
    ("{0} dies!", game.constants.palette.Message.positive),
    ("{0} dies!", game.constants.palette.Message.default),
)
