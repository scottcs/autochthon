"""Combat related messages."""
import game.const.palette

Attack = (
    ("You attack {1} with {2}!", game.const.palette.Message.default),
    ("{0} attacks you with {2}!", game.const.palette.Message.negative),
    ("{0} attacks {1} with {2}!", game.const.palette.Message.positive),
)

Miss = (
    ("You miss!", game.const.palette.Message.negative),
    ("{0} misses!", game.const.palette.Message.positive),
    ("{0} misses!", game.const.palette.Message.default),
)

AttackImmune = (
    ("Your attack cannot be {1}!", game.const.palette.Message.positive),
    ("{0}'s attack cannot be {1}!", game.const.palette.Message.negative),
    ("{0}'s attack cannot be {1}!", game.const.palette.Message.default),
)

Defend = (
    ("You {1}!", game.const.palette.Message.positive),
    ("{0} {1}!", game.const.palette.Message.negative),
    ("{0} {1}!", game.const.palette.Message.default),
)

DamageImmune = (
    ("You are immune to {1}!", game.const.palette.Message.very_positive),
    ("{0} is immune to {1}!", game.const.palette.Message.very_negative),
    ("{0} is immune to {1}!", game.const.palette.Message.default),
)

DamageResist = (
    ("You resist {1} and only take {2} damage!", game.const.palette.Message.very_positive),
    ("{0} resists {1} and only takes {2} damage!", game.const.palette.Message.very_negative),
    ("{0} resists {1} and only takes {2} damage!", game.const.palette.Message.default),
)

DamageVulnerable = (
    ("You are vulnerable to {1} and take {2} damage!", game.const.palette.Message.very_negative),
    ("{0} is vulnerable to {1} and takes {2} damage!", game.const.palette.Message.very_positive),
    ("{0} is vulnerable to {1} and takes {2} damage!", game.const.palette.Message.default),
)

DamageNormal = (
    ("You take {2} {1} damage!", game.const.palette.Message.negative),
    ("{0} takes {2} {1} damage!", game.const.palette.Message.positive),
    ("{0} takes {2} {1} damage!", game.const.palette.Message.default),
)
