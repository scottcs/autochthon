"""Combat related messages."""
from gamedata.palette import MessagePalette


MsgAttack = (
    ("You attack {1} with {2}!", MessagePalette.default),
    ("{0} attacks you with {2}!", MessagePalette.negative),
    ("{0} attacks {1} with {2}!", MessagePalette.positive),
)

MsgMiss = (
    ("You miss!", MessagePalette.negative),
    ("{0} misses!", MessagePalette.positive),
    ("{0} misses!", MessagePalette.default),
)

MsgAttackImmune = (
    ("Your attack cannot be {1}!", MessagePalette.positive),
    ("{0}'s attack cannot be {1}!", MessagePalette.negative),
    ("{0}'s attack cannot be {1}!", MessagePalette.default),
)

MsgDefend = (
    ("You {1}!", MessagePalette.positive),
    ("{0} {1}!", MessagePalette.negative),
    ("{0} {1}!", MessagePalette.default),
)

MsgDamageImmune = (
    ("You are immune to {1}!", MessagePalette.very_positive),
    ("{0} is immune to {1}!", MessagePalette.very_negative),
    ("{0} is immune to {1}!", MessagePalette.default),
)

MsgDamageResist = (
    ("You resist {1} and only take {2} damage!", MessagePalette.very_positive),
    ("{0} resists {1} and only takes {2} damage!", MessagePalette.very_negative),
    ("{0} resists {1} and only takes {2} damage!", MessagePalette.default),
)

MsgDamageVulnerable = (
    ("You are vulnerable to {1} and take {2} damage!", MessagePalette.very_negative),
    ("{0} is vulnerable to {1} and takes {2} damage!", MessagePalette.very_positive),
    ("{0} is vulnerable to {1} and takes {2} damage!", MessagePalette.default),
)

MsgDamageNormal = (
    ("You take {2} {1} damage!", MessagePalette.negative),
    ("{0} takes {2} {1} damage!", MessagePalette.positive),
    ("{0} takes {2} {1} damage!", MessagePalette.default),
)
