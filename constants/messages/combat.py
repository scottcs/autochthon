"""Combat related messages."""
import constants.palette

MsgAttack = (
    ("You attack {1} with {2}!", constants.palette.MessagePalette.default),
    ("{0} attacks you with {2}!", constants.palette.MessagePalette.negative),
    ("{0} attacks {1} with {2}!", constants.palette.MessagePalette.positive),
)

MsgMiss = (
    ("You miss!", constants.palette.MessagePalette.negative),
    ("{0} misses!", constants.palette.MessagePalette.positive),
    ("{0} misses!", constants.palette.MessagePalette.default),
)

MsgAttackImmune = (
    ("Your attack cannot be {1}!", constants.palette.MessagePalette.positive),
    ("{0}'s attack cannot be {1}!", constants.palette.MessagePalette.negative),
    ("{0}'s attack cannot be {1}!", constants.palette.MessagePalette.default),
)

MsgDefend = (
    ("You {1}!", constants.palette.MessagePalette.positive),
    ("{0} {1}!", constants.palette.MessagePalette.negative),
    ("{0} {1}!", constants.palette.MessagePalette.default),
)

MsgDamageImmune = (
    ("You are immune to {1}!", constants.palette.MessagePalette.very_positive),
    ("{0} is immune to {1}!", constants.palette.MessagePalette.very_negative),
    ("{0} is immune to {1}!", constants.palette.MessagePalette.default),
)

MsgDamageResist = (
    ("You resist {1} and only take {2} damage!", constants.palette.MessagePalette.very_positive),
    ("{0} resists {1} and only takes {2} damage!", constants.palette.MessagePalette.very_negative),
    ("{0} resists {1} and only takes {2} damage!", constants.palette.MessagePalette.default),
)

MsgDamageVulnerable = (
    (
        "You are vulnerable to {1} and take {2} damage!",
        constants.palette.MessagePalette.very_negative,
    ),
    (
        "{0} is vulnerable to {1} and takes {2} damage!",
        constants.palette.MessagePalette.very_positive,
    ),
    ("{0} is vulnerable to {1} and takes {2} damage!", constants.palette.MessagePalette.default),
)

MsgDamageNormal = (
    ("You take {2} {1} damage!", constants.palette.MessagePalette.negative),
    ("{0} takes {2} {1} damage!", constants.palette.MessagePalette.positive),
    ("{0} takes {2} {1} damage!", constants.palette.MessagePalette.default),
)
