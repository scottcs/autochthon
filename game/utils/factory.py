"""Factory utilities."""
from game.component.movement import Position
from game.types import Entity
from game.world import World
from gamedata.entity.assemblage.player import Player


def make_player(world: World, x: int=0, y: int=0, *variations) -> Entity:
    """Make a player and add it to the world."""
    player = world.assemble_entity(Player, *variations)
    world.players.add(player)
    pos = world.component_for_entity(player, Position)
    pos.x = x
    pos.y = y
    return player
