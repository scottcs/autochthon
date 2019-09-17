"""Status effect messages."""
import game.const.palette

Death = (
    ("You die!", game.const.palette.Message.danger),
    ("{0} dies!", game.const.palette.Message.positive),
    ("{0} dies!", game.const.palette.Message.default),
)
